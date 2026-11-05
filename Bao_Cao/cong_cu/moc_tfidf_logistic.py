"""Bảng 2.12, 2.13, 3.11: mốc TF-IDF + hồi quy logistic so với cả hệ thống, trên cùng các câu hỏi.

Chạy: python moc_tfidf_logistic.py <thư mục kết quả Kaggle bản 22, có các file *__kaggle_base14a_*.zip>

Học từ câu router của AI/data/finetune_qwen_20261029_v5/train.jsonl (private_request -> denied).
Kiểm tra trên các câu development của natural, natural2, policy, kb3, ngoài phạm vi (bỏ expansion: bộ khóa),
và in số tổng (không in câu) trên phần validation. facts/unknown/semantic được tính là answer.
"""
import json
import sys
import zipfile
from collections import Counter
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score
from sklearn.pipeline import make_pipeline, make_union

sys.stdout.reconfigure(encoding="utf8")
AI = Path(__file__).resolve().parents[2] / "AI"
sys.path.insert(0, str(AI))
from shopbot.retrieval import normalize

RESULTS = Path(sys.argv[1])
ANSWER = {"facts", "unknown", "semantic"}


def train_set():
    X, y = [], []
    for line in open(AI / "data/finetune_qwen_20261029_v5/train.jsonl", encoding="utf8"):
        r = json.loads(line)
        if r["task"] != "router":
            continue
        target = json.loads(r["messages"][2]["content"])
        X.append(json.loads(r["messages"][1]["content"])["question"])
        y.append("denied" if target.get("private_request") else target["action"])
    return X, y


def eval_set(validation):
    X, y, system = [], [], []
    for z in sorted(RESULTS.glob("*base14a*.zip")):
        bank = z.stem.split("__")[0]
        if bank.startswith("expansion") and not validation:
            continue
        cases = {c["id"]: c for c in json.loads((AI / "evaluation" / bank / "bank.json").read_text(encoding="utf8"))}
        for r in json.loads(zipfile.ZipFile(z).read("results.json")):
            if (r.get("split") == "validation") != validation:
                continue
            expected = cases[r["id"]]["expected_behavior"]
            if expected == "catalog_pick":
                continue
            X.append(cases[r["id"]]["question"])
            y.append("answer" if expected in ANSWER else expected)
            system.append(r["result"]["basic_action"])
    return X, y, system


X, y = train_set()
Xd, yd, sd = eval_set(False)
Xv, yv, sv = eval_set(True)
labels = sorted(set(y) | set(yd))
score = lambda t, p: (round(accuracy_score(t, p), 3), round(f1_score(t, p, labels=labels, average="macro", zero_division=0), 3))
print("train", len(X), Counter(y).most_common())
print("development", len(Xd), Counter(yd).most_common())
print("always answer (development): acc, macro-F1 =", score(yd, ["answer"] * len(yd)))
for weight in (None, "balanced"):
    model = make_pipeline(
        make_union(TfidfVectorizer(preprocessor=normalize, ngram_range=(1, 2)),
                   TfidfVectorizer(preprocessor=normalize, analyzer="char_wb", ngram_range=(2, 4))),
        LogisticRegression(max_iter=2000, class_weight=weight, C=10))
    model.fit(X, y)
    print(f"TF-IDF + LR class_weight={weight} (development): acc, macro-F1 =", score(yd, model.predict(Xd)))
print("labels", labels)
print("confusion, TF-IDF + LR balanced (development, rows = true):")
print(confusion_matrix(yd, model.predict(Xd), labels=labels))
print("whole system (development): acc, macro-F1 =", score(yd, sd))
print("validation", len(Xv), "(totals only)")
print("TF-IDF + LR balanced (validation): acc, macro-F1 =", score(yv, model.predict(Xv)))
print("whole system (validation): acc, macro-F1 =", score(yv, sv))
