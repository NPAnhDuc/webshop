"""Server capability contracts; registration never implies implementation or authority."""
import copy


_REGISTRY={
    'catalog.search':dict(roles=('customer','admin'),status='enabled',required=('max_price_exclusive',),optional=('limit','category','brand'),source='server catalog snapshot'),
    'catalog.compare':dict(roles=('customer','admin'),status='enabled',required=('product_ids',),optional=('variant_ids',),source='server catalog snapshot'),
    'catalog.product_facts':dict(roles=('customer','admin'),status='enabled',required=('product_id','fields'),optional=(),source='server catalog snapshot'),
    'admin.finance':dict(roles=('admin',),status='enabled',required=('start','end'),optional=(),source='server financial database'),
    'admin.finance_chart':dict(roles=('admin',),status='enabled',required=('start','end'),optional=('metric',),source='server financial database'),
    'admin.data_quality':dict(roles=('admin',),status='enabled',required=(),optional=(),source='server-pinned curated revision'),
    'documents.answer':dict(roles=('customer','admin'),status='disabled',required=('question',),optional=(),source='role-filtered knowledge corpus; not connected',
        reason='Câu này cần nguồn kiến thức/chính sách; nhánh tài liệu chưa được kết nối với chế độ công cụ thử nghiệm.'),
    'file.transform':dict(roles=('admin',),status='unsupported',required=('question',),optional=(),source='new input file; importer not implemented',
        reason='Chưa hỗ trợ nhập/làm sạch/chuẩn hóa/ghi dữ liệu file. Kiểm nguồn cũ không thay được yêu cầu xử lý file mới.'),
    'sales.rank':dict(roles=('admin',),status='unsupported',required=('question',),optional=(),source='sales by SKU; conversational tool not implemented',
        reason='Chưa nối công cụ xếp hạng bán hàng theo SKU. Đếm SKU trong danh mục không phải xếp hạng doanh số.'),
}


def describe(role):
    if role not in ('customer','admin'):raise PermissionError('Unknown authenticated principal')
    return [dict(name=name,**copy.deepcopy(spec)) for name,spec in _REGISTRY.items() if role in spec['roles']]


def validate_call(role,name,arguments):
    if role not in ('customer','admin'):raise PermissionError('Unknown authenticated principal')
    if name not in _REGISTRY:raise ValueError('Unknown tool')
    spec=_REGISTRY[name]
    if role not in spec['roles']:raise PermissionError('Internal capability requires admin')
    if not isinstance(arguments,dict):raise ValueError('Tool arguments must be an object')
    if set(arguments)-set(spec['required'])-set(spec['optional']):
        raise ValueError('Unknown tool arguments; no SQL/code/path/role execution')
    if set(spec['required'])-set(arguments):raise ValueError('Missing required tool arguments')
    if 'question' in spec['required'] and (not isinstance(arguments['question'],str) or not 1<=len(arguments['question'].strip())<=4000):
        raise ValueError('Nonempty bounded question required')
    return dict(name=name,**copy.deepcopy(spec))
