"""Whitespace normalization only; calendar arithmetic remains in conversation.py."""
import re
import unicodedata
from .conversation import explicit_periods,resolve_time
from .retrieval import normalize


def calendar_question(question):
    question=unicodedata.normalize('NFC',question)
    return re.sub(r'\b(tháng|thang|quý|quy|năm|nam)(?=\d)',r'\1 ',question,flags=re.I)


def admin_periods(question,plan,state,today):
    """A model-selected time mode needs a real calendar operand or server context."""
    active=state.get('active_period')
    periods=explicit_periods(question,today,active)
    if periods:return periods
    q=normalize(question)
    relative=re.search(r'\b(thang|quy|nam)\s+(truoc|vua roi|nay|hien tai)\b',q)
    contextual=re.search(r'\b(?:so voi|lui|truoc do|vua xem|vua hoi)\b',q)
    if relative:
        unit={'thang':'month','quy':'quarter','nam':'year'}[relative[1]]
        if relative[2] in ('truoc','vua roi'):
            mode='previous_period' if contextual else {'month':'last_month','quarter':'last_quarter','year':'last_year'}[unit]
        else:mode={'month':'current_month','quarter':'current_quarter','year':'current_year'}[unit]
        return resolve_time(question,dict(time_mode=mode,period_unit=unit),dict(active_period=active),today)
    if re.search(r'\b(?:lui|ky truoc|truoc do)\b',q):
        return resolve_time(question,dict(time_mode='previous_period',period_unit='none'),dict(active_period=active),today)
    reference=re.search(r'\b(thang|quy|nam)\s+(?:do|vua xem|dang xem)\b',q)
    if reference and active and active['unit']!={'thang':'month','quy':'quarter','nam':'year'}[reference[1]]:
        return []
    # No actual temporal operand: retain confirmed context, never invent last_month.
    if plan['operation']=='compare' and state.get('comparison_periods'):
        return [dict(p) for p in state['comparison_periods']]
    return [dict(active)] if active else []
