"""Keep numeric/product/ACL regressions separate from the new RAG rubric.

The old document grader demanded whole chunks verbatim. Do not weaken it or
misrepresent smaller source-owned answer spans as failing factual retrieval.
"""
import audit_chatbot_questions as audit

original=audit.bank


def bank():
    return [g for g in original() if all(t['check']!='document' for t in g['turns'])]


if __name__=='__main__':
    audit.bank=bank
    audit.main()
