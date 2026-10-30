"""Admin-only monthly publishing controls."""
import hashlib
import json
import re
from datetime import timedelta
import streamlit as st
from .monthly import MonthlyUpdater, atomic_json, month_bounds, read_json, local_today
from .retrieval import extract
from .validation import validate
from .store import connect


def render_monthly_controls(db_path):
    with connect(db_path,readonly=True) as con:
        simulation=con.execute("SELECT 1 FROM sqlite_master WHERE name='financial_ledger' AND type='table'").fetchone()
    if simulation:
        with st.expander('Dữ liệu mô phỏng đã đối soát'):
            st.caption('67 SKU dùng chung cho bán, nhập, hoàn trả và tồn kho. Kỳ 10/2025–09/2026. Không phải doanh thu thật.')
            st.info('Gói này là một phiên bản kiểm thử cố định. Không nhập lô JSON bán hàng đơn giản vào sổ FIFO. Khi có dữ liệu thật cần ETL đầy đủ đơn, nhập, hoàn và chi phí; cập nhật tri thức không đồng nghĩa huấn luyện model.')
        return
    updater=MonthlyUpdater(db_path)
    previous=(local_today().replace(day=1)-timedelta(days=1)).strftime('%Y-%m')
    with st.expander('Dữ liệu và tri thức theo tháng'):
        st.caption('Tự động cập nhật SQL và kho tra cứu. Không huấn luyện lại trọng số model.')
        month=st.text_input('Tháng dữ liệu (YYYY-MM)',value=previous,key='monthly_period')
        try: first,last=month_bounds(month)
        except ValueError:
            st.error('Tháng phải có dạng YYYY-MM.');return
        if first>local_today():
            st.error('Không nhận tháng tương lai.');return
        sales=st.file_uploader('Số liệu bán hàng JSON',type=['json'],key='monthly_sales')
        if sales and st.button('Lưu lô số liệu tháng'):
            try:
                if sales.size>20*1024*1024:raise ValueError('Tối đa 20 MB')
                payload=json.loads(sales.getvalue().decode('utf-8-sig'))
                validate(payload)
                if payload.get('month')!=month or payload.get('data_kind')!=updater.kind:
                    raise ValueError('month/data_kind không khớp tháng đã chọn và database đang dùng')
                payload['ready']=True
                target=updater.structured/'monthly'/month/'shop.json'
                old=target.read_bytes() if target.exists() else None
                atomic_json(target,payload)
                try:updater._batch(month,allow_current=True)
                except Exception:
                    if old is not None:target.write_bytes(old)
                    else:target.unlink(missing_ok=True)
                    raise
                digest=hashlib.sha256(json.dumps(payload,sort_keys=True).encode()).hexdigest()
                atomic_json(target.parent/'revisions'/(digest+'.json'),payload)
                st.success('Đã lưu. Worker sẽ nạp tháng đã chốt; tháng hiện tại cần chọn nạp tháng chưa chốt.')
            except Exception as exc:st.error(str(exc))
        st.markdown('**Tài liệu của tháng**')
        document=st.file_uploader('Tài liệu MD, TXT, PDF có chữ, DOCX',type=['md','txt','pdf','docx'],key='monthly_document')
        identifier=st.text_input('Mã tài liệu ổn định (dùng lại mã khi thay phiên bản)',key='document_identifier')
        version=st.number_input('Phiên bản tài liệu',min_value=1,value=1,step=1)
        audience=st.selectbox('Ai được đọc?', ['Chủ shop','Người mua'])
        effective=st.date_input('Có hiệu lực từ',value=first)
        approved=st.checkbox('Tôi đã kiểm tra và duyệt tài liệu này',value=False)
        if document and st.button('Lưu tài liệu tháng'):
            target=None
            manifest_path=updater.unstructured/'monthly'/month/f'manifest-{updater.kind}.json'
            previous_manifest=manifest_path.read_bytes() if manifest_path.exists() else None
            created=False
            try:
                if not re.fullmatch(r'[\w-]{1,100}',identifier):raise ValueError('Mã tài liệu chỉ gồm chữ, số, dấu gạch dưới hoặc gạch ngang')
                if document.size>10*1024*1024:raise ValueError('Tối đa 10 MB')
                suffix=document.name.rsplit('.',1)[-1].lower()
                digest=hashlib.sha256(document.getvalue()).hexdigest()[:16]
                target=manifest_path.parent/f'{identifier}-v{int(version)}-{digest}.{suffix}'
                target.parent.mkdir(parents=True,exist_ok=True)
                created=not target.exists()
                target.write_bytes(document.getvalue())
                if not extract(target).strip():raise ValueError('Không đọc được chữ; PDF scan cần OCR')
                manifest=read_json(manifest_path,{'ready':True,'data_kind':updater.kind,'documents':[]})
                entry={'file':target.name,'document_id':identifier,'version':int(version),
                       'audience':'customer' if audience=='Người mua' else 'admin',
                       'effective_from':effective.isoformat(),'effective_to':None,
                       'status':'approved' if approved else 'draft'}
                previous=next((d for d in manifest['documents'] if (d['document_id'],d['version'])==(identifier,int(version))),None)
                if previous and previous.get('status')=='approved' and previous!=entry:
                    raise ValueError('Phiên bản đã duyệt không được sửa; hãy tăng số phiên bản')
                manifest['ready']=True
                manifest['documents']=[d for d in manifest['documents'] if (d['document_id'],d['version'])!=(identifier,int(version))]+[entry]
                atomic_json(manifest_path,manifest)
                updater._documents(month)  # validate this month's versions before publishing
                st.success('Đã lưu tài liệu đã duyệt.' if approved else 'Đã lưu bản nháp; chatbot chưa sử dụng.')
            except Exception as exc:
                if previous_manifest is not None:manifest_path.write_bytes(previous_manifest)
                else:manifest_path.unlink(missing_ok=True)
                if created and target is not None:target.unlink(missing_ok=True)
                st.error(str(exc))
        allow_current=st.checkbox('Nạp cả số liệu tháng hiện tại chưa chốt',value=False)
        if st.button('Cập nhật dữ liệu và tri thức tháng này'):
            try:
                result=updater.process(month,allow_current=allow_current)
                st.success('Đã cập nhật.' if result['status']=='updated' else 'Không có thay đổi; không nhập trùng.')
                st.json(result)
            except Exception as exc:st.error(str(exc))
        status=read_json(updater.runtime/'worker-status.json',{})
        if status:st.caption('Worker tự động đã có lần kiểm tra. Chi tiết nằm trong runtime/monthly.')
