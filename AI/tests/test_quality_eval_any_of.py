from shopbot.quality_eval import grade


def make_case(any_of=True):
    required = {"document_id": "primary", "version": 1, "quote": "The DDR notch prevents a mismatch."}
    if any_of:
        required["any_of"] = [{"document_id": "alternate", "version": 1, "quote": "DDR4 memory does not fit DDR5 slots."}]
    return {"role": "customer", "expected_behavior": "facts", "required": [required]}


def make_result(document_id, quote, version=1):
    source = {"document_id": document_id, "version": version, "chunk_id": "chunk-1", "text": quote, "audience": "customer"}
    return {"basic_action": "answer", "sources": [source], "rag": {
        "answerability": "full", "claims": [{"text": quote, "evidence": [{"chunk_id": "chunk-1", "quotes": [quote]}]}],
        "available_fields": [{"document_id": document_id}],
    }}


def test_any_of_accepts_primary_or_alternative_source_quote():
    case = make_case()
    assert grade(case, make_result("primary", "The DDR notch prevents a mismatch."))["status"] == "PASS_CHECKS"
    assert grade(case, make_result("alternate", "DDR4 memory does not fit DDR5 slots."))["status"] == "PASS_CHECKS"


def test_any_of_rejects_wrong_source_and_wrong_version():
    case = make_case()
    assert grade(case, make_result("other", "The DDR notch prevents a mismatch."))["status"] == "FAIL_CHECKS"
    assert grade(case, make_result("alternate", "DDR4 memory does not fit DDR5 slots.", version=2))["status"] == "FAIL_CHECKS"


def test_required_without_any_of_keeps_single_quote_behavior():
    case = make_case(any_of=False)
    assert grade(case, make_result("primary", "The DDR notch prevents a mismatch."))["status"] == "PASS_CHECKS"
    assert grade(case, make_result("alternate", "DDR4 memory does not fit DDR5 slots."))["status"] == "FAIL_CHECKS"
