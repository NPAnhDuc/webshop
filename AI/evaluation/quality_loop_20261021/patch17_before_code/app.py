import hashlib
import hmac
import os
from pathlib import Path
import streamlit as st
import pandas as pd
from dotenv import load_dotenv
from shopbot.store import ROOT, initialize, dataset_source, connect
from shopbot.engine import Engine
from shopbot.retrieval import extract

load_dotenv(ROOT / '.env')
os.environ.setdefault('CHATBOT_MODE','basic_rag')
st.set_page_config(page_title='Shop AI · Trợ lý điện tử',page_icon='💬',layout='wide')
db_path=(ROOT/os.getenv("SHOP_DATABASE","data/structured/shop.db")).resolve()
if not db_path.is_relative_to((ROOT/"data").resolve()):
    st.error("SHOP_DATABASE phải nằm trong AI/data")
    st.stop()
initialize(db_path)
st.title('Shop AI · Trợ lý cửa hàng điện tử')
st.caption('Bản thử nghiệm local · '+('dữ liệu mô phỏng' if dataset_source(db_path)=='demo' else 'dữ liệu shop đã nhập')+' · chính sách mẫu cần chủ shop duyệt')
if os.getenv('RAG_SYNTHESIS','0')=='1':
    st.caption('Tài liệu: tổng hợp bằng chứng từ nhiều nguồn, dẫn mục và phiên bản; thông tin còn thiếu sẽ được nêu rõ.')
scenario_active=False
with connect(db_path,readonly=True) as con:
    if con.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='product_facts'").fetchone():
        scenario_active=True
        st.caption('Bộ mô phỏng 67 SKU · 10/2025–09/2026 · nhập, bán, hoàn trả và tồn kho cùng mã sản phẩm · chưa phải số liệu shop thật')

def logout_admin():
    st.session_state['admin_password']=''
    st.session_state.pop('messages_admin',None)
    st.session_state.pop('profile_admin',None)

with st.sidebar:
    st.header('Không gian hỏi đáp')
    area=st.radio('Bạn là', ['Người mua','Chủ shop'])
    role='customer'
    if area=='Chủ shop':
        expected=os.getenv('ADMIN_PASSWORD','')
        if not expected:
            st.warning('Chưa bật admin. Cấu hình ADMIN_PASSWORD trong AI/.env rồi khởi động lại.')
            st.stop()
        password=st.text_input('Mật khẩu chủ shop',type='password',key='admin_password')
        if not hmac.compare_digest(password.encode(),expected.encode()):
            st.info('Đăng nhập để đọc số liệu nội bộ.')
            st.stop()
        role='admin'
        st.button('Đăng xuất',on_click=logout_admin)
    st.write('Model:',os.getenv('OLLAMA_MODEL','chưa cấu hình'))
    st.caption('Hiểu hội thoại: '+('model local · bộ nhớ 6 lượt gần nhất' if os.getenv('CONVERSATION_MODE')=='semantic' else 'bản định tuyến cũ'))
    st.caption('Tìm tài liệu: '+('embedding tiếng Việt local + từ khóa' if os.getenv('VI_EMBEDDING_URL') else 'từ khóa'))
    active=st.session_state.get(f'profile_{role}',{}).get('active_period')
    if active: st.caption('Kỳ đang xem: '+active['label'])
    if st.button('Cuộc trò chuyện mới'):
        st.session_state[f'messages_{role}']=[]
        st.session_state[f'profile_{role}']={}
        st.rerun()
    st.markdown('**Thử hỏi**')
    examples=['OLED là gì?','Chính sách bảo hành thế nào?','Laptop học tập nên chọn cấu hình gì?'] if role=='customer' else ['Tóm tắt kế hoạch quý 3 năm 2026','Theo báo cáo tháng 9 năm 2026, doanh thu là bao nhiêu?','Quy trình duyệt khuyến mãi thế nào?']
    if scenario_active and role=='customer':
        examples=['OLED là gì?','Lenovo LOQ Gaming 15IRH8 dùng RAM gì?','Chính sách bảo hành của shop thế nào?']
    for example in examples:
        st.caption(example)
    if role=='admin':
        from shopbot.knowledge_ui import render_knowledge_controls
        render_knowledge_controls(db_path)
        from shopbot.monthly_ui import render_monthly_controls
        if os.getenv('CHATBOT_MODE')!='basic_rag':render_monthly_controls(db_path)

key=f'messages_{role}'
pkey=f'profile_{role}'
if key not in st.session_state: st.session_state[key]=[]
if pkey not in st.session_state: st.session_state[pkey]={}

def render(result,render_key):
    st.markdown(result['answer'])
    rows=result.get('rows',[])
    if rows:
        frame=pd.DataFrame(rows)
        st.dataframe(frame,hide_index=True,use_container_width=True)
        if role=='admin' and result.get('analysis'):
            st.bar_chart(frame.set_index('sku')[['revenue','gross_profit']])
            monthly=pd.DataFrame(result['analysis']['monthly'])
            if not monthly.empty:
                st.line_chart(monthly.set_index('month')[['revenue','gross_profit']])
            financial=result['analysis'].get('financial')
            if financial and financial.get('channels'):
                st.caption('Theo kênh bán — doanh thu đã trừ hoàn trả, gắn về kênh của đơn gốc')
                st.dataframe(pd.DataFrame(financial['channels']),hide_index=True,use_container_width=True)
            with st.expander('Ảnh báo cáo và sơ đồ tải xuống',expanded=bool(result.get('visualization'))):
                from shopbot.reporting import render_report_png, report_fingerprint, explain_visual
                options={'Báo cáo tổng quan':'overview','Sơ đồ lời/lỗ':'financial_flow'}
                initial=1 if result.get('visualization')=='financial_flow' else 0
                choice=st.selectbox('Loại ảnh',list(options),index=initial,key='report-kind-'+render_key)
                png=render_report_png(result['analysis'],options[choice])
                st.image(png,caption='Ảnh lấy từ cùng dữ liệu SQL với phần phân tích phía trên. Không suy đoán số từ ảnh.')
                st.markdown(explain_visual(result['analysis'],options[choice]))
                name='bao-cao-'+report_fingerprint(result['analysis'])[:12]+'-'+options[choice]+'.png'
                st.download_button('Tải ảnh PNG',png,file_name=name,mime='image/png',key='download-png-'+render_key)
        elif role=='admin' and {'month','revenue','profit'}.issubset(frame.columns):
            st.bar_chart(frame.set_index('month')[['revenue','profit']])
    with st.expander('Nguồn và bước xử lý'):
        st.caption(result.get('mode','demo'))
        st.json(result.get('sources',[]))
        st.write(result.get('trace',[]))
        if result.get('rag'):
            st.caption('Nhận định và trích dẫn dùng để kiểm chứng. Bộ kiểm chứng bằng model vẫn có thể sai.')
            st.json(result['rag'])

for index,message in enumerate(st.session_state[key]):
    with st.chat_message(message['role']):
        if message['role']=='assistant': render(message['result'],f'{role}-{index}')
        else: st.markdown(message['content'])
question=st.chat_input('Nhập câu hỏi bằng tiếng Việt…',max_chars=4000)
if question:
    st.session_state[key].append({'role':'user','content':question})
    with st.chat_message('user'): st.markdown(question)
    with st.chat_message('assistant'):
        with st.spinner('Đang kiểm tra dữ liệu…'):
            result=Engine(db_path).ask(question,role,st.session_state[pkey])
        render(result,f'{role}-{len(st.session_state[key])}')
    st.session_state[pkey]=result['profile']
    st.session_state[key].append({'role':'assistant','result':result})
