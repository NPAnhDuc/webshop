"""Shared input contract for a learned metric controller; no financial facts."""
import re
import unicodedata

LABELS=['revenue','units','gross_profit','operating_profit','inherit','unspecified','clarify']
EXPLICIT_METRICS=set(LABELS[:4])
BASE_MODEL='dangvantuan/vietnamese-embedding'
BASE_REVISION='4ab46e46ba5902328ba0742e489e75f787932f2b'
CONTRACT_VERSION='metric-v4.1'


def metric_text(question,memory=None,intent='top_products'):
    memory=memory or {}
    has_metric=memory.get('active_intent')==intent and memory.get('active_metric') in EXPLICIT_METRICS
    # Amounts, SKU digits and calendar numbers are not the target being learned.
    question=re.sub(r'\d+(?:[.,/]\d+)*','N',unicodedata.normalize('NFC',question))
    return ('Câu hiện tại: '+question+'\nTác vụ: '+intent+
            '\nĐã có tiêu chí của tác vụ này: '+('có' if has_metric else 'chưa có'))
