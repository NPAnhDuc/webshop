"""Opt-in structured catalog conversations; tools render all numerical facts.

Planner selects slots, never SQL/code, prices or answer prose. Caller role and
server-owned catalog are authoritative. This is not a replacement for backend auth.
"""
import copy
import hashlib
import json
import requests
from .catalog_planner import StagedCatalogPlanner,SearchClarification,UnsupportedCategory,validate_mixed_questions
from .admin_conversation import AdminConversation

SCHEMA={'type':'object','properties':{
    'action':{'type':'string','enum':['search','compare','search_documents','compare_documents','documents','admin','clarify','outside','handoff']},
    'catalog_question':{'type':'string'},'knowledge_question':{'type':'string'},
    'budget_max_vnd':{'type':'integer','minimum':0,'maximum':1_000_000_000},
    'budget_inclusive':{'type':'boolean'},'limit':{'type':'integer','minimum':0,'maximum':20},
    'category':{'type':'string'},'brand':{'type':'string'},'continuation':{'type':'boolean'},
    'clear_brand':{'type':'boolean'},'unsupported_filters':{'type':'boolean'},
    'product_refs':{'type':'array','maxItems':2,'items':{'type':'string'}}},
    'required':['action','budget_max_vnd','budget_inclusive','limit','category','brand','continuation','clear_brand','unsupported_filters','product_refs'],
    'additionalProperties':False}



class CatalogConversation:
    def __init__(self,tools,planner=None,admin_agent=None):
        self.tools=tools
        self.planner=planner or StagedCatalogPlanner()
        self.admin_agent=admin_agent or AdminConversation(tools)
        self.revision=hashlib.sha256(json.dumps(tools.catalog.snapshot,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
        self.lookup={f'P{i+1}':p for i,p in enumerate(sorted(tools.catalog.products.values(),key=lambda p:p['id'])) if p['status']=='active'}

    def run(self,question,principal_role,memory,today):
        if principal_role not in ('customer','admin'):raise PermissionError('Unknown server role')
        profile=copy.deepcopy(memory or {})
        if profile.get('owner_role',principal_role)!=principal_role:profile={}
        profile['owner_role']=principal_role
        state=profile.get('catalog_context',{})
        if not isinstance(state,dict) or state.get('revision')!=self.revision:state={}
        last=[r for r in state.get('last_selection',[]) if r in self.lookup]
        prior=state.get('filters',{})
        payload=dict(question=question,role=principal_role,today=today.isoformat(),
                     history=profile.get('history',[])[-4:],previous_filters=prior,
                     admin_context=profile.get('admin_context',{}) if principal_role=='admin' else {},
                     last_selection=[dict(position=i+1,ref=r,name=self.lookup[r]['name']) for i,r in enumerate(last)],
                     catalog=[dict(ref=r,name=p['name'],variants=[v['name'] for v in p['variants'] if v['status']=='active']) for r,p in self.lookup.items()])
        base=dict(question=question,role=principal_role,profile=profile,rows=[],sources=[],intent='clarify',
                  mode='agent_tools · structured catalog prototype',trace=['agent: planner slots then server tools; no generated arithmetic'])
        knowledge_question=None
        def finish(text,action,intent='clarify',evidence=None):
            base.update(answer=text,basic_action=action,intent=intent)
            if evidence is not None:
                base['tool_evidence']=evidence
                base['sources']=[dict(source=evidence['source'],data_kind=evidence['data_kind'],snapshot_captured_at=evidence['snapshot_captured_at'])]
            if knowledge_question is not None:
                doc_args=dict(question=knowledge_question)
                try:output=self.tools.execute(principal_role,'documents.answer',doc_args)
                except (ValueError,RuntimeError,OSError,requests.RequestException):
                    output=dict(status='unavailable',executed=False,reason='Chưa truy xuất được nguồn tài liệu; chưa trả lời phần kiến thức/chính sách.')
                calls=[] if evidence is None else [dict(tool='catalog.search' if plan['action']=='search_documents' else 'catalog.compare',arguments=arguments,output=evidence)]
                calls.append(dict(tool='documents.answer',arguments=doc_args,output=output))
                base['tool_evidence']=dict(calls=calls)
                if evidence is not None:base['tool_evidence']['catalog']=evidence
                base['partial']=True
                base['components']=dict(catalog=dict(status='completed' if evidence is not None else action),
                    documents=dict(status=output['status'],executed=output['executed'],question=knowledge_question))
                base['answer']=text+'\n\nPhần kiến thức/chính sách: '+output['reason']
            return base
        try:
            plan=self.planner(payload)
            if not isinstance(plan,dict):raise ValueError('Invalid planner object')
            mixed=plan.get('action') in ('search_documents','compare_documents')
            expected=set(SCHEMA['required'])|({'catalog_question','knowledge_question'} if mixed else set())
            if set(plan)!=expected:raise ValueError('Invalid planner keys')
            if mixed:
                validate_mixed_questions(question,{key:plan[key] for key in ('catalog_question','knowledge_question')})
            if plan['action'] not in SCHEMA['properties']['action']['enum']:raise ValueError('Invalid action')
            for key in ['budget_inclusive','continuation','clear_brand','unsupported_filters']:
                if type(plan[key]) is not bool:raise ValueError('Invalid bool')
            for key,maximum in [('budget_max_vnd',1_000_000_000),('limit',20)]:
                if type(plan[key]) is not int or not 0<=plan[key]<=maximum:raise ValueError('Invalid integer')
            if any(not isinstance(plan[k],str) or len(plan[k])>100 for k in ['brand','category']):raise ValueError('Invalid filter')
            refs=plan['product_refs']
            if not isinstance(refs,list) or len(refs)>2 or any(not isinstance(r,str) or r not in self.lookup for r in refs):raise ValueError('Invalid product reference')
        except SearchClarification as exc:
            return finish(str(exc),'clarify')
        except UnsupportedCategory as exc:
            return finish(str(exc),'deferred')
        except (ValueError,TypeError,KeyError,requests.RequestException):
            return finish('Chưa xác định chắc yêu cầu. Bạn nêu ngân sách hoặc hai mã máy cụ thể giúp tôi nhé.','unavailable')
        base['plan']=plan
        action=plan['action'].removesuffix('_documents') if mixed else plan['action']
        if mixed:knowledge_question=plan['knowledge_question']
        if action=='admin':
            if principal_role=='customer':return finish('Thông tin giá vốn và quản trị chỉ dành cho tài khoản quản lý.','denied','denied')
            return self.admin_agent.run(question,principal_role,profile,today)
        if action=='documents':
            arguments=dict(question=question)
            output=self.tools.execute(principal_role,'documents.answer',arguments)
            base['tool_evidence']=dict(calls=[dict(tool='documents.answer',arguments=arguments,output=output)])
            base['capability_status']=dict(name='documents.answer',status=output['status'],executed=False)
            return finish(output['reason'],'documents')
        if action in ('documents','outside','handoff','clarify'):
            messages={'documents':'Câu này cần nguồn kiến thức/chính sách; nhánh tài liệu chưa được kết nối với chế độ công cụ thử nghiệm.',
                      'outside':'Tôi hỗ trợ sản phẩm máy tính và nghiệp vụ cửa hàng. Bạn muốn tìm hoặc so sánh máy nào?',
                      'handoff':'Chưa có kênh chuyển nhân viên được kết nối; chưa có yêu cầu nào được gửi.',
                      'clarify':'Bạn muốn chọn hoặc so sánh những model nào? Nếu nhắc máy trước đó, tôi cần một danh sách đã xác định.'}
            return finish(messages[action],action)
        try:
            if action=='search':
                old=prior if plan['continuation'] else {}
                ceiling=plan['budget_max_vnd']+int(plan['budget_inclusive']) if plan['budget_max_vnd'] else old.get('max_price_exclusive')
                if not ceiling:return finish('Bạn muốn ngân sách tối đa bao nhiêu cho mỗi máy?','clarify')
                if plan['unsupported_filters']:
                    return finish('Bộ lọc này chưa được kết nối đầy đủ; tôi chưa thể bỏ qua điều kiện đó để đưa danh sách đúng yêu cầu.','deferred')
                arguments=dict(max_price_exclusive=ceiling,limit=plan['limit'] or old.get('limit',5),
                               category=plan['category'] or old.get('category','laptop'),
                               brand=None if plan['clear_brand'] else (plan['brand'] or old.get('brand')))
                evidence=self.tools.execute(principal_role,'catalog.search',arguments)
                products=evidence['data']['products'];base['rows']=products
                data=evidence['data']
                if (type(data.get('total_matching')) is not int or data['total_matching']<0
                        or data.get('requested_count')!=arguments['limit']
                        or data.get('returned_count')!=len(products)
                        or len(products)!=min(arguments['limit'],data['total_matching'])
                        or len({p['id'] for p in products})!=len(products)):
                    base['rows']=[]
                    raise ValueError('Catalog result violates requested count/identity contract')
                base['result_contract']=dict(requested_count=arguments['limit'],returned_count=len(products),
                    total_matching=data['total_matching'],shortage=len(products)<arguments['limit'],passed=True)
                inverse={p['id']:ref for ref,p in self.lookup.items()}
                profile['catalog_context']=dict(revision=self.revision,filters=arguments,last_selection=[inverse[p['id']] for p in products])
                lines=[f"Tìm thấy {len(products)}/{arguments['limit']} sản phẩm được yêu cầu, theo giá tăng dần:",'']
                for i,p in enumerate(products):
                    v=p['variant'];price=f"{v['price']:,}".replace(',','.')
                    lines.append(f"{i+1}. {p['name']} — {v['name']} — {price} đ; số lượng khả dụng {v['available_qty']}.")
                lines.extend(['','Chưa có permalink sản phẩm được cấu hình; tôi không tự tạo link trang mua hàng.'])
            else:
                if plan['unsupported_filters']:
                    return finish('Yêu cầu so sánh chứa điều kiện chưa được hỗ trợ đầy đủ.','deferred')
                if len(refs)!=2 or refs[0]==refs[1]:return finish('Bạn chọn hai model khác nhau để tôi so sánh nhé.','clarify')
                arguments=dict(product_ids=[self.lookup[r]['id'] for r in refs])
                evidence=self.tools.execute(principal_role,'catalog.compare',arguments)
                profile['catalog_context']=dict(revision=self.revision,filters=prior,last_selection=list(refs))
                labels={'variant_price_vnd':'Giá biến thể (VND)','cpu_model':'CPU','gpu_model':'GPU','ram_gb':'RAM (GB)',
                        'ram_type':'Loại RAM','storage_gb':'Ổ lưu trữ (GB)','storage_type':'Loại ổ','panel':'Tấm nền',
                        'resolution':'Độ phân giải','refresh_hz':'Tần số quét (Hz)','weight_kg':'Khối lượng (kg)',
                        'battery_wh':'Pin (Wh)','warranty_months':'Bảo hành (tháng)'}
                names=[p['name'] for p in evidence['data']['products']]
                safe=lambda v:str(v).replace('|','/').replace('\n',' ') if v is not None else 'Chưa có thông tin'
                lines=['| Thuộc tính | '+safe(names[0])+' | '+safe(names[1])+' |','|---|---|---|']
                for row in evidence['data']['comparison']:lines.append('| '+labels[row['field']]+' | '+' | '.join(safe(v) for v in row['values'])+' |')
                lines.extend(['','Chưa xếp hạng thắng thua: cần nhu cầu và benchmark phù hợp; Wh không phải số giờ pin.'])
            label='Dữ liệu mô phỏng' if evidence['data_kind']=='simulation' else 'Dữ liệu snapshot'
            lines.extend(['',label+' tại '+evidence['snapshot_captured_at']+'. Thông số là bản ghi sản phẩm, chưa xác minh mọi biến thể; giá/tồn chưa phải dữ liệu trực tiếp của shop.'])
            return finish('\n'.join(lines),'answer','products' if action=='search' else 'compare',evidence)
        except (ValueError,TypeError,KeyError):
            return finish('Chưa xác định được đúng dữ liệu hoặc biến thể. Bạn nêu model và phiên bản cụ thể giúp tôi nhé.','clarify')
