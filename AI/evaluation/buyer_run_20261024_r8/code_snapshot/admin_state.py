"""Deterministic binding of a literal metric-only follow-up to confirmed shop state.

This is operand/reference resolution, not a general natural-language router.
Unknown words, new periods, scope changes and unsupported requests go to planning.
"""
import re
import unicodedata
from datetime import date

ALIASES={
    'doanh thu':'revenue','doanh thu thuan':'revenue',
    'gia von':'cost','gia von hang da ban':'cost',
    'lai gop':'gross_profit','loi nhuan gop':'gross_profit',
    'bien lai gop':'gross_margin_pct','chi phi van hanh':'expenses','chi phi van hanh shop':'expenses',
    'lai hoat dong':'operating_profit','lai hoat dong truoc lai vay va thue':'operating_profit',
    'so don':'orders','tien hoan':'refunds','tien hoan khach':'refunds',
}


def _valid_period(period):
    if not isinstance(period,dict) or period.get('unit') not in ('month','quarter','year'):return False
    try:
        start=date.fromisoformat(period['start']);end=date.fromisoformat(period['end'])
        return start<end and start.isoformat()==period['start'] and end.isoformat()==period['end'] and isinstance(period.get('label'),str)
    except (ValueError,KeyError,TypeError):return False


def metric_reference_plan(question,state):
    if (not isinstance(state,dict) or state.get('pending') or state.get('entity','shop')!='shop'
            or state.get('operation') not in ('finance','compare','chart')
            or not _valid_period(state.get('active_period'))):return None
    q=''.join(c for c in unicodedata.normalize('NFD',question.casefold().replace('đ','d')) if unicodedata.category(c)!='Mn')
    q=re.sub(r'\s+',' ',q).strip(' ?!.')
    aliases='|'.join(re.escape(key) for key in sorted(ALIASES,key=len,reverse=True))
    match=re.fullmatch(r'(?:con )?('+aliases+r')(?: (thang do|quy do|nam do|ky do))?(?: (?:thi sao|the nao|bao nhieu))?(?: (?:nhe|a))?',q)
    if not match:return None
    referenced={'thang do':'month','quy do':'quarter','nam do':'year'}.get(match[2])
    if referenced and referenced!=state['active_period']['unit']:return None
    if state['operation']=='compare':
        periods=state.get('comparison_periods')
        if (not isinstance(periods,list) or len(periods)!=2 or not all(_valid_period(p) for p in periods)
                or periods[0]==periods[1] or periods[-1]!=state['active_period']):return None
    return dict(operation=state['operation'],metric=ALIASES[match[1]],time_mode='same_period',period_unit='none')
