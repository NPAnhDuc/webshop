from shopbot.quality_eval import grade


CASE=dict(role='admin',expected_behavior='facts',required=[dict(document_id='monthly-report-2026-02',version=1,quote='Giá vốn: 529597000 VND.')])


def sql_result(text,period='2026-02'):
    return dict(basic_action='answer',sources=[dict(chunk_id='sql-financial-ledger',text=text,document_id='sql-financial-ledger',version='live')],
                rag=dict(claims=[dict(text=text,evidence=[dict(chunk_id='sql-financial-ledger',quotes=[text],period=period)])]))


def test_sql_answer_with_the_report_figure_passes():
    assert grade(CASE,sql_result('Giá vốn hàng bán kỳ 2026-02: 529.597.000 VND.'))['status']=='PASS_CHECKS'


def test_small_counts_compare_as_numbers():
    case=dict(CASE,required=[dict(document_id='monthly-report-2026-02',version=1,quote='Đơn hàng: 65.')])
    assert grade(case,sql_result('Số đơn hàng kỳ 2026-02: 65 đơn.'))['status']=='PASS_CHECKS'
    assert grade(case,sql_result('Số đơn hàng kỳ 2026-02: 650 đơn.'))['status']=='FAIL_CHECKS'


def test_negative_figures_compare_with_their_sign():
    case=dict(CASE,required=[dict(document_id='monthly-report-2026-02',version=1,quote='Lợi nhuận hoạt động trước lãi vay và thuế: -1390044 VND.')])
    assert grade(case,sql_result('Lợi nhuận hoạt động trước lãi vay và thuế kỳ 2026-02: -1.390.044 VND.'))['status']=='PASS_CHECKS'
    assert grade(case,sql_result('Lợi nhuận hoạt động trước lãi vay và thuế kỳ 2026-02: 1.390.044 VND.'))['status']=='FAIL_CHECKS'


def test_sql_answer_with_another_figure_fails():
    assert grade(CASE,sql_result('Giá vốn hàng bán kỳ 2026-02: 529.597.001 VND.'))['status']=='FAIL_CHECKS'


def test_same_figure_from_another_month_fails():
    assert grade(CASE,sql_result('Giá vốn hàng bán kỳ 2026-03: 529.597.000 VND.',period='2026-03'))['status']=='FAIL_CHECKS'


def test_every_required_figure_must_be_present():
    case=dict(CASE,required=[*CASE['required'],dict(document_id='monthly-report-2026-02',version=1,quote='Đơn hàng: 65.')])
    assert grade(case,sql_result('Giá vốn hàng bán kỳ 2026-02: 529.597.000 VND.'))['status']=='FAIL_CHECKS'


def test_non_report_gold_still_needs_its_own_source():
    case=dict(CASE,required=[dict(document_id='sales-plan-2026-Q1',version=1,quote='Mục tiêu: 529597000 VND.')])
    assert grade(case,sql_result('Giá vốn hàng bán kỳ 2026-02: 529.597.000 VND.'))['status']=='FAIL_CHECKS'
