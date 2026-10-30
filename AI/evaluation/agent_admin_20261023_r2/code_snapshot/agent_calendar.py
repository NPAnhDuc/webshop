"""Whitespace normalization only; calendar arithmetic remains in conversation.py."""
import re
import unicodedata


def calendar_question(question):
    question=unicodedata.normalize('NFC',question)
    return re.sub(r'\b(tháng|thang|quý|quy|năm|nam)(?=\d)',r'\1 ',question,flags=re.I)
