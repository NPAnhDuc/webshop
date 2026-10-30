"""Align already selected monthly metric evidence to each explicit user part.

No search, model call, fact generation or arithmetic. Only a selected fragment
with the same typed metric can move between parts; unknown/missing stays empty.
"""
import re
from .retrieval import normalize
from .rag_scope import resolve_scope
from .rag_metrics import METRICS


def metrics(text):
    value=normalize(text)
    found={m[0] for m in METRICS if re.search(m[1],value)}
    if re.search(r'\bsan pham hoan tra\b',value):found.add('returned_units')
    return found


def source_month(fragment):
    source=fragment['source']
    if source.get('doc_type')!='monthly_report':return None
    identifier=source.get('document_id','').removeprefix('monthly-report-')
    period=source.get('period') or identifier
    if not re.fullmatch(r'20\d{2}-(?:0[1-9]|1[0-2])',period):return None
    if re.fullmatch(r'20\d{2}-\d{2}',identifier) and identifier!=period:return None
    return period


def bind_monthly_parts(question,parts,answers,fragments,scope,today):
    result={key:list(ids) for key,ids in answers.items()};trace=[]
    if re.search(r'\b(?:vi sao|tai sao|nguyen nhan|giai thich|nghia la|la gi|cach tinh|huong dan|y nghia|muc tieu|ke hoach)\b',normalize(question)):
        return result,trace
    shared=metrics(question)
    pool=list(dict.fromkeys(i for ids in answers.values() for i in ids))
    for key,part in parts.items():
        local=resolve_scope(part,today)
        expected=local['months']
        if len(expected)!=1 or local['quarters']:continue
        # A bare "tháng12" inherits the confirmed query year only when the
        # same month number identifies exactly one period in the query scope.
        if not re.search(r'\b20\d{2}\b',part):
            candidates=[m for m in scope.get('months',[]) if m[-2:]==expected[0][-2:]]
            if len(candidates)!=1:continue
            expected=candidates
        wanted=metrics(part)
        if not wanted and len(shared)==1:wanted=shared
        if len(wanted)!=1:continue
        wanted=next(iter(wanted));month=expected[0]
        # Rebinding is limited to the typed numeric field, never an arbitrary
        # related sentence in the right report. This also prevents moving a
        # cost figure into a revenue part in a mixed-metric question.
        def matches(identifier):
            fragment=fragments[identifier]
            label,separator,value=fragment['text'].partition(':')
            return (source_month(fragment)==month and separator and metrics(label)=={wanted}
                    and re.fullmatch(r'\s*-?\d[\d.,]*(?:\s*(?:VND|đơn))?\s*\.?',value,re.I))
        kept=[i for i in result[key] if matches(i)]
        if not kept:kept=[i for i in pool if matches(i)][:3]
        result[key]=kept
        trace.append(dict(part_id=key,period=month,metric=wanted,
                          original_ids=list(answers[key]),bound_ids=kept,
                          added_ids=[i for i in kept if i not in answers[key]],
                          rejected_ids=[i for i in answers[key] if i not in kept]))
    return result,trace
