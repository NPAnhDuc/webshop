"""A part asking for a percentage is not answered by a sentence without one.

The selector usually finds the right document but the wrong sentence, so only
sentences of the documents it already picked may replace its choice.
"""

import re

from .retrieval import normalize

ASKED = re.compile(r"\b(?:bao nhieu|may)\s*(?:phan tram|%)")
STATED = re.compile(r"\d\s*%")
WORD = re.compile(r"[a-z0-9-]+")


def bind_percent(part_ids, answers, fragments):
    bound, bindings = dict(answers), []
    for key, part in part_ids.items():
        picked = answers.get(key) or []
        asked = normalize(part)
        if not picked or not ASKED.search(asked):
            continue
        if any(STATED.search(fragments[i]["text"]) for i in picked):
            continue
        owners = {fragments[i]["source"].get("document_id") for i in picked}
        stated = [i for i, value in fragments.items()
                  if value["source"].get("document_id") in owners and STATED.search(value["text"])]
        if not stated:
            continue
        words = set(WORD.findall(asked))
        best = max(stated, key=lambda i: len(words & set(WORD.findall(normalize(fragments[i]["text"])))))
        bound[key] = [best]
        bindings.append(dict(part=key, picked=list(picked), bound=best))
    return bound, bindings
