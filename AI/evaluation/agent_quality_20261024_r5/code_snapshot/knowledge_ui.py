"""Small authenticated Streamlit document editor; no React changes."""
import streamlit as st
from .knowledge import KnowledgeStore,TYPES
from .monthly import local_today
from .retrieval import extract


def render_knowledge_controls(db):
    store=KnowledgeStore(db)
    with st.expander('Quản lý tài liệu RAG — tải, sửa, gỡ'):
        st.caption('Tài liệu mới được đọc ở lượt hỏi tiếp theo. Bản nháp không được dùng; gỡ sẽ ngừng truy xuất và giữ lịch sử kiểm toán.')
        docs=store.all_records();latest={}
        for d in docs:
            if d['version']>latest.get(d['document_id'],{}).get('version',0):latest[d['document_id']]=d
        selected=st.selectbox('Tài liệu', ['Tạo tài liệu mới',*sorted(latest)],key='kb_select')
        old=latest.get(selected,{})
        with st.form('kb_edit'):
            identifier=st.text_input('Mã tài liệu',value=old.get('document_id',''),disabled=bool(old))
            title=st.text_input('Tên tài liệu',value=old.get('title',''))
            kinds=TYPES
            kind=st.selectbox('Loại tài liệu',kinds,index=kinds.index(old.get('doc_type','policy')))
            audience=st.selectbox('Quyền đọc',['admin','customer'],index=1 if old.get('audience')=='customer' else 0)
            from .conversation import CATEGORIES
            category=st.selectbox('Nhóm hàng',CATEGORIES,index=CATEGORIES.index(old.get('category','all')))
            start=st.date_input('Hiệu lực từ',value=local_today())
            end=st.text_input('Ngày hết hiệu lực (YYYY-MM-DD, bỏ trống nếu không có)',value=old.get('effective_to') or '')
            uploaded=st.file_uploader('Nạp MD, TXT, PDF có chữ hoặc DOCX',type=['md','txt','pdf','docx'],key='kb_upload')
            text=st.text_area('Nội dung (file tải lên được ưu tiên nếu có)',value=old.get('text',''),height=180)
            approved=st.checkbox('Đã kiểm tra nguồn, nội dung và duyệt phiên bản này',value=False)
            submitted=st.form_submit_button('Lưu phiên bản mới')
        if submitted:
            temporary=None
            try:
                if uploaded:
                    if uploaded.size>10*1024*1024:raise ValueError('Tối đa 10 MB')
                    import tempfile
                    from pathlib import Path
                    with tempfile.NamedTemporaryFile(suffix=Path(uploaded.name).suffix,delete=False) as stream:
                        temporary=Path(stream.name);stream.write(uploaded.getvalue())
                    text=extract(temporary)
                store.save(identifier,text,role='admin',title=title,doc_type=kind,audience=audience,
                    category=category,approved=approved,effective_from=start.isoformat(),effective_to=end or None,
                    expected_version=old.get('version',0))
                st.success('Đã lưu phiên bản mới. Nhấn tải lại danh sách để chọn phiên bản vừa lưu.')
            except Exception as exc:st.error('Không đọc hoặc lưu được tài liệu: '+str(exc)[:300])
            finally:
                if temporary:temporary.unlink(missing_ok=True)
        if old and st.button('Gỡ tài liệu khỏi kho truy xuất',key='kb_delete'):
            try:
                store.delete(old['document_id'],role='admin',expected_version=old['version'])
                st.success('Đã gỡ khỏi truy xuất. Phiên bản cũ không tự xuất hiện lại.')
            except (ValueError,OSError) as exc:st.error(str(exc))
        if st.button('Tải lại danh sách tài liệu',key='kb_refresh'):st.rerun()
    with st.expander('Câu chưa trả lời được — tìm khoảng trống tài liệu'):
        from .store import ROOT
        from .knowledge import namespace
        import json
        log=ROOT/'runtime/rag-basic'/namespace(db)/'turns.jsonl'
        if log.exists():
            records=[]
            for line in log.read_text(encoding='utf8').splitlines()[-200:]:
                try:r=json.loads(line)
                except ValueError:continue
                if r.get('status') in ('none','partial','unverified'):
                    records.append({k:r.get(k) for k in ('time','origin','role','question','status','doc_types')})
            st.dataframe(records,hide_index=True)
        else:st.caption('Chưa có log RAG cơ bản trong phiên bản dữ liệu này.')
