"""Read-only tool foundation for the next customer/admin agents.

No model-generated SQL/Python and no automatic writes to shop records. The caller
must obtain principal_role from server authentication, never from model arguments.
The existing RAG engine is deliberately not switched to this prototype.
"""
import copy
import hashlib
import json
from datetime import date
from pathlib import Path
from urllib.parse import quote
from .business_analysis import analyze_business

SPEC_FIELDS = {
    'cpu_brand','cpu_model','cpu_generation','cores','ram_gb','ram_type','ram_upgradable',
    'storage_gb','storage_type','gpu_type','gpu_model','screen_inch','resolution','panel',
    'refresh_hz','brightness_nits','color_gamut','touch','weight_kg','battery_wh',
    'warranty_months','demand','socket','chipset','has_igpu','tdp_w','tgp_w','psu_watt',
    'form_factor','supported_form_factors','ram_slots','ram_max_gb','ram_max_speed',
    'ram_speed_mhz','vram_gb','length_mm','max_gpu_length_mm','height_mm',
    'max_cooler_height_mm','supported_sockets','interface','power_connectors','modular','certification'
}


# Fields a buyer may ask about. Some (connection, recommended_psu_w) are not yet
# captured, so asking returns an explicit "missing" instead of a guess.
FACT_FIELDS = SPEC_FIELDS|{'connection','recommended_psu_w'}


def public_catalog(state):
    """Project a trusted server snapshot; private keys never enter tool evidence."""
    inventory=state.get('inventory',{})
    result=[];seen=set()
    for product in state['products']:
        if product['id'] in seen:raise ValueError('Duplicate product ID')
        seen.add(product['id'])
        variants=[]
        for v in product.get('variants',[]):
            price=v.get('price')
            if type(price) is not int or price<=0:raise ValueError('Invalid integer VND price')
            inv=inventory.get(v['id'])
            available=None
            if inv is not None:
                if inv.get('productId')!=product['id']:raise ValueError('Inventory product mismatch')
                on_hand,reserved=inv.get('qtyOnHand'),inv.get('qtyReserved')
                if any(type(n) is not int or n<0 for n in [on_hand,reserved]):raise ValueError('Invalid stock quantity')
                if reserved>on_hand:raise ValueError('Reserved quantity exceeds stock; reconcile before recommendation')
                available=on_hand-reserved
            variants.append(dict(id=v['id'],sku=v.get('sku'),name=v.get('name'),price=price,
                                 status=v.get('status'),available_qty=available))
        result.append(dict(id=product['id'],name=product['name'],slug=product['slug'],
                           category=product.get('categorySlug'),brand=product.get('brandName'),
                           status=product.get('status'),variants=variants,
                           specs={k:copy.deepcopy(v) for k,v in product.get('specs',{}).items() if k in SPEC_FIELDS},
                           api_path='/api/products/'+quote(product['slug'],safe=''),
                           product_page_url=None,link_status='storefront_permalink_not_configured'))
    return result


class CatalogTools:
    def __init__(self,snapshot):
        if snapshot.get('schema')!='agent-catalog-v1':raise ValueError('Unknown catalog contract')
        self.snapshot=copy.deepcopy(snapshot)
        self.products={p['id']:p for p in self.snapshot['products']}
        if len(self.products)!=len(self.snapshot['products']):raise ValueError('Duplicate product ID')

    def _envelope(self,data):
        return dict(data=data,data_kind=self.snapshot['data_kind'],
                    snapshot_captured_at=self.snapshot['captured_at'],source=self.snapshot['source'],
                    price_basis='variant price in captured snapshot; not verified live shop pricing',
                    spec_basis='product record; not independently verified for every variant',
                    link_status='product_page_url unavailable until storefront permalink is configured')

    def search(self,max_price_exclusive,limit=5,category='laptop',brand=None):
        if type(max_price_exclusive) is not int or max_price_exclusive<=0:raise ValueError('Positive integer VND budget required')
        if type(limit) is not int or not 1<=limit<=20:raise ValueError('Limit must be 1..20')
        found=[]
        for p in self.products.values():
            if p['status']!='active' or p['category']!=category or (brand and (p.get('brand') or '').casefold()!=brand.casefold()):continue
            choices=[v for v in p['variants'] if v['status']=='active' and v.get('available_qty') is not None
                     and v['available_qty']>0 and 0<v['price']<max_price_exclusive]
            if choices:
                variant=min(choices,key=lambda v:(v['price'],v['id']))
                found.append(dict(id=p['id'],name=p['name'],slug=p['slug'],specs=p['specs'],
                                  variant=variant,api_path=p['api_path'],product_page_url=p['product_page_url']))
        found.sort(key=lambda p:(p['variant']['price'],p['id']))
        return self._envelope(dict(products=copy.deepcopy(found[:limit]),total_matching=len(found),
                                   requested_count=limit,returned_count=min(limit,len(found)),
                                   ordering='price_ascending; not a suitability or performance ranking'))

    def product_facts(self,product_id,fields):
        """Requested spec fields of one exact product; absent fields are reported, never filled."""
        if product_id not in self.products or self.products[product_id]['status']!='active':raise ValueError('Unknown or inactive product; clarify model')
        if (not isinstance(fields,list) or not 1<=len(fields)<=5 or len(set(fields))!=len(fields)
                or any(f not in FACT_FIELDS for f in fields)):raise ValueError('Choose 1..5 known spec fields')
        p=self.products[product_id]
        values=[dict(field=f,value=copy.deepcopy(p['specs'].get(f)),missing=p['specs'].get(f) is None) for f in fields]
        return self._envelope(dict(product=dict(id=p['id'],name=p['name'],category=p['category'],
                                                api_path=p['api_path'],product_page_url=p['product_page_url']),
                                   facts=values,
                                   limitations=['Missing means absent from the captured record, not that the product lacks the feature.']))

    def compare(self,product_ids,variant_ids=None):
        if not isinstance(product_ids,list) or len(product_ids)!=2 or len(set(product_ids))!=2:raise ValueError('Choose two distinct exact product IDs')
        if any(k not in self.products or self.products[k]['status']!='active' for k in product_ids):raise ValueError('Unknown or inactive product; clarify model')
        products=[self.products[k] for k in product_ids]
        if variant_ids is not None and (not isinstance(variant_ids,list) or len(variant_ids)!=2):raise ValueError('Choose one exact variant per product')
        variants=[]
        for i,p in enumerate(products):
            choices=[v for v in p['variants'] if v['status']=='active' and (variant_ids is None or v['id']==variant_ids[i])]
            if len(choices)!=1:raise ValueError('Variant is ambiguous or unknown; choose an exact variant ID')
            variants.append(choices[0])
        fields=['cpu_model','gpu_model','ram_gb','ram_type','storage_gb','storage_type','panel',
                'resolution','refresh_hz','weight_kg','battery_wh','warranty_months']
        rows=[]
        rows.append(dict(field='variant_price_vnd',values=[v['price'] for v in variants],missing=[False,False],
                         second_minus_first=variants[1]['price']-variants[0]['price']))
        for field in fields:
            a,b=[p['specs'].get(field) for p in products]
            numeric=type(a) in (int,float) and type(b) in (int,float)
            rows.append(dict(field=field,values=[a,b],missing=[v is None for v in [a,b]],
                             second_minus_first=round(b-a,6) if numeric else None))
        return self._envelope(dict(products=[dict(id=p['id'],name=p['name'],variant=copy.deepcopy(v),api_path=p['api_path'],product_page_url=p['product_page_url']) for p,v in zip(products,variants)],
                                   comparison=rows,winner=None,
                                   limitations=['Different CPU/GPU names do not prove benchmark superiority.',
                                                'Battery Wh is not measured battery runtime.',
                                                'Preference weights require the buyer workload; no universal winner.']))


class AgentTools:
    """Allowlisted tools; principal_role is trusted caller context, not an LLM slot."""
    def __init__(self,catalog,financial_database,report_directory=None,*,curated_reader=None):
        self.catalog=catalog
        self.financial_database=financial_database
        self.report_directory=Path(report_directory).resolve() if report_directory is not None else None
        self.curated_reader=curated_reader
        from contextvars import ContextVar
        self._captured_calls=ContextVar('agent_tool_calls',default=None)

    def capture_calls(self):
        from contextlib import contextmanager
        @contextmanager
        def capture():
            calls=[];token=self._captured_calls.set(calls)
            try:yield calls
            finally:self._captured_calls.reset(token)
        return capture()

    def execute(self,principal_role,tool,arguments):
        calls=self._captured_calls.get()
        if calls is None:return self._execute(principal_role,tool,arguments)
        from time import perf_counter
        started=perf_counter()
        record=dict(tool=tool,arguments=copy.deepcopy(arguments),principal_role=principal_role)
        try:
            result=self._execute(principal_role,tool,arguments)
            record.update(status=result['status'] if result.get('executed') is False else 'success',output=copy.deepcopy(result))
            return result
        except Exception as exc:
            record.update(status='denied' if isinstance(exc,PermissionError) else 'error',error_type=type(exc).__name__)
            raise
        finally:
            record['seconds']=perf_counter()-started;calls.append(record)

    def _execute(self,principal_role,tool,arguments):
        from .capabilities import validate_call
        spec=validate_call(principal_role,tool,arguments)
        if spec['status']!='enabled':
            return dict(tool=tool,status=spec['status'],executed=False,sources=[],reason=spec['reason'])
        handlers={
            'catalog.search':lambda **args:self.catalog.search(**args),
            'catalog.compare':lambda **args:self.catalog.compare(**args),
            'catalog.product_facts':lambda **args:self.catalog.product_facts(**args),
            'admin.finance':self._finance,
            'admin.finance_chart':self._finance_chart,
            'admin.data_quality':self._data_quality,
        }
        return handlers[tool](**arguments)

    def capabilities(self,principal_role):
        from .capabilities import describe
        result=describe(principal_role)
        for item in result:
            item['configured']=(self.curated_reader is not None if item['name']=='admin.data_quality'
                else self.report_directory is not None if item['name']=='admin.finance_chart'
                else self.financial_database is not None if item['name']=='admin.finance'
                else self.catalog is not None if item['name'].startswith('catalog.')
                else False)
        return result

    def _data_quality(self):
        if self.curated_reader is None:raise ValueError('Curated reader is not configured by server')
        return self.curated_reader.quality()

    def _finance(self,start,end):
        a,b=date.fromisoformat(start),date.fromisoformat(end)
        if a>=b:raise ValueError('Start must precede exclusive end')
        result=analyze_business(self.financial_database,a.isoformat(),b.isoformat())
        result['tool']='admin.finance'
        result['source_database']=str(self.financial_database)
        result['generated_by']='SQL and deterministic Python; not LLM arithmetic'
        return result

    def _finance_chart(self,start,end,metric='overview'):
        if self.report_directory is None:raise ValueError('Report artifact directory not configured by server')
        fields={'revenue':('Net revenue','totals','revenue','Million VND'),
                'cost':('Cost of goods sold','totals','cost','Million VND'),
                'gross_profit':('Gross profit','totals','gross_profit','Million VND'),
                'gross_margin_pct':('Gross margin','totals','gross_margin_pct','Percent'),
                'expenses':('Operating expenses','financial','operating_expenses','Million VND'),
                'operating_profit':('Operating profit before interest/tax','financial','operating_profit_before_interest_tax','Million VND'),
                'orders':('Orders','financial','orders','Orders'),
                'refunds':('Refunds','financial','refunds','Million VND')}
        if metric not in (*fields,'overview'):raise ValueError('Unsupported chart metric')
        report=self._finance(start,end)
        if not report.get('monthly'):return dict(artifact=None,report=report,metric=metric,chart_data=[],generated_by='No observations; no chart generated')
        selected=['revenue','gross_profit'] if metric=='overview' else [metric]
        chart_data=[]
        for row in report['monthly']:
            a=date.fromisoformat(row['month']+'-01')
            b=date(a.year+1,1,1) if a.month==12 else date(a.year,a.month+1,1)
            monthly=self._finance(max(start,a.isoformat()),min(end,b.isoformat()))
            values={key:(monthly.get(fields[key][1]) or {}).get(fields[key][2]) for key in selected}
            if any(v is None for v in values.values()):raise ValueError('Requested chart metric has no source data')
            chart_data.append(dict(month=row['month'],values=values))
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        digest=hashlib.sha256(json.dumps(dict(report=report,metric=metric,chart_data=chart_data),sort_keys=True,ensure_ascii=False).encode()).hexdigest()[:16]
        self.report_directory.mkdir(parents=True,exist_ok=True)
        path=self.report_directory/f'finance-{start}-{end}-{digest}.png'
        if not path.exists():
            fig,ax=plt.subplots(figsize=(9,4.8))
            positions=list(range(len(chart_data)))
            for i,key in enumerate(selected):
                unit=fields[key][3];scale=1e6 if unit=='Million VND' else 1
                offset=(i-(len(selected)-1)/2)*.36
                ax.bar([p+offset for p in positions],[r['values'][key]/scale for r in chart_data],.36,label=fields[key][0])
            ax.set_xticks(positions,[r['month'] for r in chart_data])
            ax.set_ylabel(fields[selected[0]][3]);ax.legend()
            ax.set_title('Monthly finance | '+('SIMULATED' if report['data_source']=='demo' else report['data_source']))
            fig.text(.02,.02,f'SQL ledger; {start} inclusive to {end} exclusive. Gross profit is not net profit.',fontsize=8)
            fig.tight_layout(rect=(0,.05,1,1));fig.savefig(path,dpi=150);plt.close(fig)
        return dict(artifact=str(path),report=report,metric=metric,chart_data=chart_data,generated_by='deterministic chart from SQL result')
