"""Versioned document CRUD, independent from financial ingestion and its worker."""
import hashlib
import re
from datetime import date
from pathlib import Path
from .store import ROOT,dataset_source,connect
from .monthly import read_json,atomic_json,atomic_text,exclusive,local_today

TYPES=['product','glossary','buying_guide','policy','promotion','store_info','shopping_guide',
       'strategy','sales_plan','marketing','monthly_report','procedure','meeting']


def namespace(db):return hashlib.sha256(str(Path(db).resolve()).encode()).hexdigest()[:16]


class KnowledgeStore:
    def __init__(self,db,root=None):
        self.db=Path(db).resolve()
        self.root=Path(root or ROOT).resolve()
        self.folder=self.root/'data/unstructured/managed'/namespace(db)
        self.manifest=self.folder/'manifest.json'
        self.kind='demo' if dataset_source(db)=='demo' else 'shop'

    def records(self):return read_json(self.manifest,[])

    def all_records(self):
        baseline=[]
        with connect(self.db,readonly=True) as con:
            if con.execute("SELECT 1 FROM sqlite_master WHERE name='metadata'").fetchone():
                entry=con.execute("SELECT value FROM metadata WHERE key='knowledge_dir'").fetchone()
                if entry:
                    folder=(self.root/entry[0]).resolve()
                    if not folder.is_relative_to(self.root/'data'):raise ValueError('Kho tài liệu nền nằm ngoài data')
                    baseline=read_json(folder/'manifest.json',[])
        return baseline+self.records()

    def save(self,identifier,text,*,role,title,doc_type,audience='admin',approved=False,
             effective_from=None,effective_to=None,category='all',expected_version=None,authority='shop_document'):
        if role!='admin':raise PermissionError('Admin required')
        if not re.fullmatch(r'[\w-]{1,100}',identifier):raise ValueError('Mã tài liệu không hợp lệ')
        if not isinstance(text,str) or not text.strip() or len(text.encode('utf8'))>10*1024*1024:raise ValueError('Tài liệu cần có chữ, tối đa 10 MB')
        if doc_type not in TYPES or audience not in ('customer','admin'):raise ValueError('Loại hoặc quyền tài liệu không hợp lệ')
        from .conversation import CATEGORIES
        if category not in CATEGORIES:raise ValueError('Nhóm hàng không hợp lệ')
        start=date.fromisoformat(effective_from or local_today().isoformat()).isoformat()
        until=date.fromisoformat(effective_to).isoformat() if effective_to else None
        if until and until<start:raise ValueError('Ngày kết thúc trước ngày bắt đầu')
        if doc_type=='promotion' and approved and not until:raise ValueError('Khuyến mãi đã duyệt cần ngày hết hiệu lực để tránh dùng ưu đãi cũ')
        if not isinstance(title,str) or not 0<len(title.strip())<=200:raise ValueError('Tiêu đề cần 1–200 ký tự')
        with exclusive(self.folder/'write.lock'):
            docs=self.records();latest=max([d['version'] for d in self.all_records() if d['document_id']==identifier],default=0)
            if expected_version is not None and latest!=expected_version:raise ValueError('Tài liệu đã thay đổi; hãy tải lại trước khi lưu')
            version=latest+1
            source=f'{identifier}-v{version}.md'
            record=dict(document_id=identifier,title=title.strip(),source=source,version=version,
                text=text.strip(),doc_type=doc_type,category=category,audience=audience,
                effective_from=start,effective_to=until,status='approved' if approved else 'draft',
                data_kind=self.kind,authority=authority,sha256=hashlib.sha256(text.strip().encode('utf8')).hexdigest())
            atomic_text(self.folder/source,text.strip())
            atomic_json(self.manifest,docs+[record])
            return record

    def delete(self,identifier,*,role,expected_version=None):
        if role!='admin':raise PermissionError('Admin required')
        with exclusive(self.folder/'write.lock'):
            docs=self.records();versions=[d for d in self.all_records() if d['document_id']==identifier]
            if not versions:raise ValueError('Không tìm thấy tài liệu')
            previous=max(versions,key=lambda d:d['version'])
            if expected_version is not None and previous['version']!=expected_version:raise ValueError('Tài liệu đã thay đổi; hãy tải lại')
            tombstone=dict(previous,version=previous['version']+1,status='deleted',text='',effective_from=local_today().isoformat(),effective_to=None)
            atomic_json(self.manifest,docs+[tombstone])
            return tombstone
