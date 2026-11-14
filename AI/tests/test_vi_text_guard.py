import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "AI" / "scripts" / "check_vi_text.py"


def scan(path, *options):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *options, str(path)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


def test_detects_question_mark_between_letters(tmp_path):
    sample = tmp_path / "bad.txt"
    sample.write_text("vi?c\n", encoding="utf-8")
    result = scan(sample)
    assert result.returncode == 1
    assert "question mark before a letter" in result.stdout
    assert ":1:" in result.stdout


def test_detects_replacement_character(tmp_path):
    sample = tmp_path / "bad.txt"
    sample.write_text("Tên thư mục: �\n", encoding="utf-8")
    result = scan(sample)
    assert result.returncode == 1
    assert "U+FFFD" in result.stdout


def test_detects_cp1252_mojibake(tmp_path):
    sample = tmp_path / "bad.txt"
    sample.write_text("Bán hàng bã mã: bÃ¡n\n", encoding="utf-8")
    result = scan(sample)
    assert result.returncode == 1
    assert "mojibake" in result.stdout


def test_detects_question_mark_at_the_start_of_a_word(tmp_path):
    sample = tmp_path / "bad.txt"
    sample.write_text("dòng cuối ?ã qua, ?ọc file ?ược rồi, ?ường đi\n", encoding="utf-8")
    result = scan(sample)
    assert result.returncode == 1
    assert result.stdout.count("question mark before a letter") == 4
    for damaged in ("?ã", "?ọc", "?ược", "?ường"):
        assert damaged in result.stdout


def test_detects_only_mojibake_pairs(tmp_path):
    sample = tmp_path / "bad.txt"
    sample.write_text("tiáº¿ng Ä‘Ã£ Viá»‡t\n", encoding="utf-8")
    result = scan(sample)
    assert result.returncode == 1
    assert "possible UTF-8/cp1252 mojibake pair" in result.stdout
    for damaged in ("áº", "Ä‘", "Ã£", "á»"):
        assert damaged in result.stdout


def test_valid_uppercase_vietnamese_and_question_sentences_are_not_mojibake(tmp_path):
    sample = tmp_path / "good.txt"
    sample.write_text(
        "ĐÃ CÓ BÁO CÁO, CÂU HỎI, XÂY DỰNG. Bao nhiêu? Còn hàng không?\n"
        "https://x.vn/a?id=3&v=2 ?id=3 ?v=2\n",
        encoding="utf-8",
    )
    result = scan(sample)
    assert result.returncode == 0, result.stdout + result.stderr


def test_ascii_question_field_checks_lost_accent_words(tmp_path):
    sample = tmp_path / "bad.json"
    sample.write_text(json.dumps({"question": "kh?ng hieu thong tin"}), encoding="utf-8")
    result = scan(sample)
    assert result.returncode == 1
    assert "$.question" in result.stdout
    assert "lost-accent word" in result.stdout


def test_valid_vietnamese_plain_chat_terminal_question_and_url_are_clean(tmp_path):
    sample = tmp_path / "good.json"
    sample.write_text(
        json.dumps(
            {
                "question": "Máy này dùng ổn không?",
                "examples": ["toi ko biet bn oi?", "https://shop.test/search?query=ram"],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    result = scan(sample)
    assert result.returncode == 0, result.stdout + result.stderr


def test_json_checks_every_string_and_jsonl_checks_each_line(tmp_path):
    sample_json = tmp_path / "nested.json"
    sample_json.write_text(json.dumps({"metadata": {"note": "bÃ¡n"}}), encoding="utf-8")
    result = scan(sample_json)
    assert result.returncode == 1
    assert "$.metadata.note" in result.stdout

    sample_jsonl = tmp_path / "items.jsonl"
    sample_jsonl.write_text(
        '{"question":"Máy tốt?"}\n{"question":"vi?c nay"}\n',
        encoding="utf-8",
    )
    result = scan(sample_jsonl)
    assert result.returncode == 1
    assert ":2:$.question" in result.stdout


def test_tail_limits_line_oriented_scan_and_reports_original_line_number(tmp_path):
    sample = tmp_path / "tail.txt"
    sample.write_text("bad vi?c\nclean\nlast\n", encoding="utf-8")
    result = scan(sample, "--tail", "2")
    assert result.returncode == 0, result.stdout + result.stderr

    result = scan(sample, "--tail", "3")
    assert result.returncode == 1
    assert ":1:" in result.stdout


def test_existing_question_datasets_are_clean():
    paths = [
        ROOT / "AI/data/v6_questions/questions.json",
        ROOT / "AI/data/v7_selector/questions.json",
        ROOT / "AI/data/v8_router_questions/questions.json",
    ]
    result = subprocess.run(
        [sys.executable, str(SCRIPT), *(str(path) for path in paths)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    assert result.returncode == 0, result.stdout + result.stderr
