"""Draw the report's figures into Bao_Cao/hinh/ (PNG, 200 dpi)."""
import math
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Polygon, Circle, FancyArrowPatch, Arc

sys.stdout.reconfigure(encoding="utf8")
OUT = Path(__file__).resolve().parent.parent / "hinh"
OUT.mkdir(parents=True, exist_ok=True)
plt.rcParams["font.family"] = "Arial"

C = {
    "data": ("#E8F1FB", "#2F6DB5"),
    "proc": ("#E9F6EC", "#2E8B57"),
    "model": ("#FDF0E3", "#C46A1B"),
    "ext": ("#F1F1F1", "#6B6B6B"),
    "warn": ("#FDEBEC", "#B83A3A"),
    "key": ("#FFF7D6", "#B08900"),
}


def canvas(w, h):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(0, w)
    ax.set_ylim(0, h)
    ax.set_aspect("equal")
    ax.axis("off")
    return fig, ax


def box(ax, x, y, w, h, text, kind="proc", size=10, bold=False, align="center"):
    face, edge = C[kind]
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.12",
                                fc=face, ec=edge, lw=1.4))
    ha = "center" if align == "center" else "left"
    tx = x + w / 2 if align == "center" else x + 0.15
    ax.text(tx, y + h / 2, text, ha=ha, va="center", fontsize=size, color="#1E1E1E",
            fontweight="bold" if bold else "normal", linespacing=1.35)
    return (x, y, w, h)


def diamond(ax, cx, cy, w, h, text, size=9):
    face, edge = C["key"]
    ax.add_patch(Polygon([(cx, cy + h / 2), (cx + w / 2, cy), (cx, cy - h / 2), (cx - w / 2, cy)],
                         closed=True, fc=face, ec=edge, lw=1.4))
    ax.text(cx, cy, text, ha="center", va="center", fontsize=size, linespacing=1.3)


def arrow(ax, p, q, label=None, color="#444444", style="-|>", rad=0.0, size=8.5, lw=1.3, ls="-", label_offset=(0, 0.12)):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle=style, mutation_scale=13, color=color, lw=lw,
                                 connectionstyle=f"arc3,rad={rad}", linestyle=ls, shrinkA=2, shrinkB=2))
    if label:
        mx, my = (p[0] + q[0]) / 2 + label_offset[0], (p[1] + q[1]) / 2 + label_offset[1]
        ax.text(mx, my, label, ha="center", va="bottom", fontsize=size, color="#333333",
                bbox=dict(fc="white", ec="none", pad=0.6, alpha=0.9))


def title(ax, w, h, text):
    ax.text(w / 2, h - 0.25, text, ha="center", va="top", fontsize=12.5, fontweight="bold", color="#1E1E1E")


def save(fig, name):
    fig.savefig(OUT / name, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("saved", name)


def right(b):
    return (b[0] + b[2], b[1] + b[3] / 2)


def left(b):
    return (b[0], b[1] + b[3] / 2)


def top(b):
    return (b[0] + b[2] / 2, b[1] + b[3])


def bottom(b):
    return (b[0] + b[2] / 2, b[1])


# ---------- Chapter 1 ----------

def fig_dw_architecture():
    w, h = 14, 6.6
    fig, ax = canvas(w, h)
    title(ax, w, h, "Kiến trúc kho dữ liệu nhiều tầng")
    ax.text(1.25, 5.65, "Nguồn dữ liệu", ha="center", fontsize=10, fontweight="bold")
    srcs = ["CSDL bán hàng\n(OLTP)", "File Excel / CSV", "Web, API\nđối tác", "Nhật ký (log)\nwebsite"]
    sb = [box(ax, 0.2, 4.45 - i * 1.15, 2.1, 0.9, s, "ext", 9) for i, s in enumerate(srcs)]
    etl = box(ax, 3.0, 2.0, 1.9, 2.3, "ETL\n\nTrích xuất\nBiến đổi\nNạp", "proc", 9.5, True)
    for b in sb:
        arrow(ax, right(b), left(etl))
    stg = box(ax, 5.5, 2.45, 1.7, 1.4, "Vùng tạm\n(Staging)", "data", 9.5)
    arrow(ax, right(etl), left(stg))
    dw = box(ax, 7.8, 1.85, 2.2, 2.6, "KHO DỮ LIỆU\n\ntích hợp\ntheo chủ đề\ncó lịch sử\nít thay đổi", "data", 9.5, True)
    arrow(ax, right(stg), left(dw))
    meta = box(ax, 7.8, 0.35, 2.2, 0.95, "Siêu dữ liệu\n(metadata)", "ext", 9)
    arrow(ax, top(meta), bottom(dw), style="<|-|>")
    ax.text(11.45, 5.65, "Data mart", ha="center", fontsize=10, fontweight="bold")
    marts = ["Bán hàng", "Kho hàng", "Tài chính"]
    mb = [box(ax, 10.65, 4.55 - i * 1.0, 1.6, 0.75, m, "data", 9) for i, m in enumerate(marts)]
    for b in mb:
        arrow(ax, right(dw), left(b))
    ax.text(13.25, 5.65, "Người dùng", ha="center", fontsize=10, fontweight="bold")
    users = ["Báo cáo, BI", "Phân tích\nOLAP", "Khai phá\ndữ liệu", "Chatbot\nhỏi đáp"]
    ub = [box(ax, 12.55, 4.6 - i * 1.15, 1.4, 0.85, u, "model", 8.5) for i, u in enumerate(users)]
    for b in ub:
        arrow(ax, (12.25, 3.5), left(b), color="#999999", lw=1.0)
    save(fig, "h1_1_kien_truc_kho_du_lieu.png")


def fig_star_schema():
    w, h = 12, 7.4
    fig, ax = canvas(w, h)
    title(ax, w, h, "Lược đồ hình sao (star schema): một bảng sự kiện, nhiều bảng chiều")
    fact = box(ax, 4.3, 2.4, 3.4, 2.7, "FACT_BAN_HANG\n─────────────\nma_ngay (FK)\nma_san_pham (FK)\nma_khach_hang (FK)\nma_cua_hang (FK)\n─────────────\nso_luong\ndoanh_thu\ngia_von", "key", 9.5, True)
    dims = [
        (0.3, 4.6, "DIM_NGAY\n────────\nma_ngay (PK)\nngay, thang\nquy, nam\nngay_le"),
        (8.6, 4.6, "DIM_SAN_PHAM\n────────\nma_san_pham (PK)\nten, hang\ndanh_muc\ngia_niem_yet"),
        (0.3, 0.5, "DIM_KHACH_HANG\n────────\nma_khach_hang (PK)\nphan_khuc\ntinh_thanh"),
        (8.6, 0.5, "DIM_CUA_HANG\n────────\nma_cua_hang (PK)\nkenh_ban\nkhu_vuc"),
    ]
    for x, y, t in dims:
        b = box(ax, x, y, 3.1, 2.1, t, "data", 9)
        cx, cy = b[0] + b[2] / 2, b[1] + b[3] / 2
        fx = 4.3 if x < 4 else 7.7
        fy = 4.4 if y > 3 else 3.1
        arrow(ax, (fx, fy), (b[0] + (b[2] if x < 4 else 0), cy), style="-", lw=1.4)
    ax.text(6.0, 1.75, "FK = khóa ngoại trỏ sang bảng chiều; PK = khóa chính", ha="center", fontsize=8.5, color="#555555")
    save(fig, "h1_2_luoc_do_hinh_sao.png")


def fig_kdd():
    w, h = 15, 4.6
    fig, ax = canvas(w, h)
    title(ax, w, h, "Quy trình khám phá tri thức (KDD) theo Fayyad và cộng sự (1996)")
    names = ["Dữ liệu\nthô", "Dữ liệu\nmục tiêu", "Dữ liệu\nđã làm sạch", "Dữ liệu\nđã biến đổi", "Mẫu\n(pattern)", "Tri thức"]
    kinds = ["ext", "data", "data", "data", "model", "key"]
    steps = ["1. Chọn lọc", "2. Tiền xử lý", "3. Biến đổi", "4. Khai phá", "5. Diễn giải,\nđánh giá"]
    bs = [box(ax, 0.3 + i * 2.5, 1.5, 1.8, 1.25, n, k, 9.5, i in (5,)) for i, (n, k) in enumerate(zip(names, kinds))]
    for i in range(5):
        arrow(ax, right(bs[i]), left(bs[i + 1]))
        ax.text((bs[i][0] + bs[i][2] + bs[i + 1][0]) / 2, 2.95, steps[i], ha="center", va="bottom", fontsize=8.6, color="#2E8B57", fontweight="bold")
    arrow(ax, (bs[5][0] + 0.9, 1.5), (bs[1][0] + 0.9, 1.5), rad=-0.18, color="#B83A3A", ls="--", label=None)
    ax.text(7.5, 0.25, "Có thể quay lại bước trước bất cứ lúc nào (lặp)", ha="center", fontsize=8.8, color="#B83A3A")
    save(fig, "h1_3_quy_trinh_kdd.png")


def fig_crisp():
    w, h = 9, 8.4
    fig, ax = canvas(w, h)
    title(ax, w, h, "Mô hình CRISP-DM: 6 giai đoạn lặp vòng")
    cx, cy, r = 4.5, 3.9, 2.85
    names = ["1. Hiểu bài toán\nkinh doanh", "2. Hiểu\ndữ liệu", "3. Chuẩn bị\ndữ liệu", "4. Xây dựng\nmô hình", "5. Đánh giá", "6. Triển khai"]
    angles = [90, 30, -30, -90, -150, 150]
    pts = []
    for n, a in zip(names, angles):
        x, y = cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a))
        b = box(ax, x - 1.05, y - 0.5, 2.1, 1.0, n, "proc", 9.2)
        pts.append((x, y))
    for i in range(6):
        a1, a2 = angles[i], angles[(i + 1) % 6]
        p = (cx + r * math.cos(math.radians(a1 - 17)), cy + r * math.sin(math.radians(a1 - 17)))
        q = (cx + r * math.cos(math.radians(a2 + 17)), cy + r * math.sin(math.radians(a2 + 17)))
        arrow(ax, p, q, rad=-0.25, color="#2E8B57")
    ax.add_patch(Circle((cx, cy), 1.0, fc=C["data"][0], ec=C["data"][1], lw=1.4))
    ax.text(cx, cy, "Dữ liệu", ha="center", va="center", fontsize=11, fontweight="bold")
    arrow(ax, (pts[1][0] - 0.5, pts[1][1] - 0.2), (pts[0][0] + 0.5, pts[0][1] - 0.55), rad=0.3, color="#888888", ls="--")
    arrow(ax, (pts[3][0] + 0.3, pts[3][1] + 0.5), (pts[2][0] - 0.6, pts[2][1] - 0.3), rad=0.3, color="#888888", ls="--")
    arrow(ax, (pts[4][0] + 0.5, pts[4][1] + 0.5), (pts[0][0] - 0.4, pts[0][1] - 0.55), rad=-0.15, color="#888888", ls="--")
    ax.text(cx, 0.15, "Nét đứt: các bước quay lại thường gặp", ha="center", fontsize=8.6, color="#666666")
    save(fig, "h1_4_crisp_dm.png")


def fig_taxonomy():
    w, h = 15, 7.6
    fig, ax = canvas(w, h)
    title(ax, w, h, "Phân loại các bài toán khai phá dữ liệu theo mục đích")
    root = box(ax, 6.0, 5.8, 3.0, 0.85, "Khai phá dữ liệu", "key", 11, True)
    pred = box(ax, 1.4, 4.3, 3.6, 0.85, "Dự đoán (predictive)\ncó nhãn, đoán giá trị mới", "proc", 9.5, True)
    desc = box(ax, 10.0, 4.3, 3.6, 0.85, "Mô tả (descriptive)\nkhông nhãn, tìm cấu trúc", "proc", 9.5, True)
    arrow(ax, bottom(root), top(pred))
    arrow(ax, bottom(root), top(desc))
    pl = ["Phân lớp\n(classification)", "Hồi quy\n(regression)", "Dự báo chuỗi\nthời gian"]
    dl = ["Phân cụm\n(clustering)", "Luật kết hợp\n(association)", "Phát hiện\nbất thường"]
    for i, t in enumerate(pl):
        b = box(ax, 0.1 + i * 2.05, 2.55, 1.9, 0.95, t, "data", 8.8)
        arrow(ax, bottom(pred), top(b), lw=1.0)
    for i, t in enumerate(dl):
        b = box(ax, 8.8 + i * 2.05, 2.55, 1.9, 0.95, t, "data", 8.8)
        arrow(ax, bottom(desc), top(b), lw=1.0)
    tm = box(ax, 5.55, 0.15, 3.9, 1.6, "Khai phá văn bản và\ntruy xuất thông tin\n(nhánh của đề tài)\nphân lớp ý định + xếp hạng\ntài liệu theo độ tương tự", "warn", 9, True)
    arrow(ax, (1.05, 2.55), (5.55, 1.2), color="#B83A3A", ls="--")
    arrow(ax, (9.75, 2.55), (9.45, 1.2), color="#B83A3A", ls="--")
    ax.text(3.0, 1.55, "phân lớp ý định", fontsize=8.5, color="#B83A3A", rotation=-15)
    ax.text(9.7, 1.95, "gom nhóm, tương tự", fontsize=8.5, color="#B83A3A")
    save(fig, "h1_5_phan_loai_khai_pha.png")


# ---------- Chapter 2 ----------

def fig_text_pipeline():
    w, h = 15.5, 3.9
    fig, ax = canvas(w, h)
    title(ax, w, h, "Các bước khai phá văn bản dùng trong truy xuất thông tin")
    steps = [("Văn bản thô\n\"Bảo hành\nlaptop?\"", "ext"), ("Chuẩn hóa\nchữ thường,\nbỏ dấu", "proc"), ("Tách từ\n(token)", "proc"),
             ("Biểu diễn\nTF-IDF, BM25,\nvector nhúng", "model"), ("Đo độ\ntương tự\ncosine", "proc"), ("Xếp hạng,\nlấy top-k", "proc"), ("Đoạn văn\nliên quan\nnhất", "data")]
    bs = [box(ax, 0.2 + i * 2.2, 0.6, 1.85, 2.1, t, k, 9.2) for i, (t, k) in enumerate(steps)]
    for i in range(len(bs) - 1):
        arrow(ax, right(bs[i]), left(bs[i + 1]))
    save(fig, "h2_1_quy_trinh_khai_pha_van_ban.png")


def fig_vector_space():
    fig, ax = plt.subplots(figsize=(6.4, 5.2))
    ax.set_xlim(0, 1.05)
    ax.set_ylim(0, 1.05)
    ax.set_xlabel('trọng số từ "bảo hành"', fontsize=10)
    ax.set_ylabel('trọng số từ "gaming"', fontsize=10)
    vecs = {"Câu hỏi q": ((0.9, 0.25), "#B83A3A", (0.78, 0.29)), "D2: chính sách bảo hành": ((0.85, 0.12), "#2E8B57", (0.6, 0.155)),
            "D1: laptop gaming": ((0.15, 0.9), "#2F6DB5", (0.16, 0.93))}
    for name, ((x, y), col, (lx, ly)) in vecs.items():
        ax.annotate("", xy=(x, y), xytext=(0, 0), arrowprops=dict(arrowstyle="-|>", color=col, lw=2))
        ax.text(lx, ly, name, color=col, fontsize=9.5, fontweight="bold")
    a1 = math.degrees(math.atan2(0.25, 0.9))
    a2 = math.degrees(math.atan2(0.12, 0.85))
    a3 = math.degrees(math.atan2(0.9, 0.15))
    ax.add_patch(Arc((0, 0), 0.6, 0.6, theta1=a2, theta2=a1, color="#2E8B57", lw=1.5))
    ax.add_patch(Arc((0, 0), 0.35, 0.35, theta1=a1, theta2=a3, color="#2F6DB5", lw=1.5))
    ax.text(0.36, 0.005, "θ nhỏ → giống", color="#2E8B57", fontsize=9)
    ax.text(0.11, 0.22, "θ lớn → khác", color="#2F6DB5", fontsize=9)
    ax.set_title("Mô hình không gian vector: góc càng nhỏ, hai văn bản càng giống", fontsize=11, fontweight="bold")
    ax.grid(alpha=0.25)
    save(fig, "h2_2_khong_gian_vector.png")


def fig_knn():
    import random
    rnd = random.Random(7)
    fig, ax = plt.subplots(figsize=(6.4, 5.2))
    a = [(rnd.gauss(0.32, 0.12), rnd.gauss(0.62, 0.12)) for _ in range(18)]
    b = [(rnd.gauss(0.68, 0.12), rnd.gauss(0.36, 0.12)) for _ in range(18)]
    ax.scatter(*zip(*a), c="#2F6DB5", s=45, label='Nhãn "hỏi sản phẩm"')
    ax.scatter(*zip(*b), marker="s", c="#C46A1B", s=45, label='Nhãn "hỏi chính sách"')
    q = (0.47, 0.5)
    pts = [(p, "a") for p in a] + [(p, "b") for p in b]
    near = sorted(pts, key=lambda t: math.dist(t[0], q))[:5]
    rad = math.dist(near[-1][0], q)
    ax.add_patch(Circle(q, rad, fill=False, ls="--", ec="#444444"))
    ax.scatter([q[0]], [q[1]], marker="*", s=260, c="#B83A3A", label="Câu hỏi mới (chưa có nhãn)", zorder=5)
    na = sum(1 for _, l in near if l == "a")
    ax.set_title(f"kNN với k = 5: {na} láng giềng xanh, {5 - na} láng giềng cam → chọn nhãn đa số", fontsize=10.5, fontweight="bold")
    ax.legend(fontsize=8.5, loc="upper right")
    ax.set_xticks([]); ax.set_yticks([])
    ax.set_aspect("equal")
    save(fig, "h2_3_knn.png")


def fig_encoders():
    w, h = 12, 6.2
    fig, ax = canvas(w, h)
    title(ax, w, h, "Bi-encoder (mã hóa riêng) và cross-encoder (mã hóa chung)")
    ax.text(3.0, 5.3, "Bi-encoder: nhanh, dùng để tìm", ha="center", fontsize=10.5, fontweight="bold", color="#2F6DB5")
    q = box(ax, 0.6, 0.4, 1.9, 0.8, "Câu hỏi", "ext", 9.5)
    d = box(ax, 3.5, 0.4, 1.9, 0.8, "Đoạn văn", "ext", 9.5)
    e1 = box(ax, 0.6, 1.8, 1.9, 0.9, "Bộ mã hóa\n(PhoBERT)", "model", 9)
    e2 = box(ax, 3.5, 1.8, 1.9, 0.9, "Bộ mã hóa\n(cùng trọng số)", "model", 9)
    v1 = box(ax, 0.6, 3.2, 1.9, 0.7, "vector u (768)", "data", 9)
    v2 = box(ax, 3.5, 3.2, 1.9, 0.7, "vector v (768)", "data", 9)
    s = box(ax, 2.0, 4.3, 2.0, 0.65, "cos(u, v)", "key", 9.5, True)
    for a_, b_ in ((q, e1), (d, e2), (e1, v1), (e2, v2)):
        arrow(ax, top(a_), bottom(b_))
    arrow(ax, top(v1), (2.6, 4.3)); arrow(ax, top(v2), (3.4, 4.3))
    ax.text(9.0, 5.3, "Cross-encoder: chậm, chính xác, dùng để xếp lại", ha="center", fontsize=10.5, fontweight="bold", color="#C46A1B")
    qd = box(ax, 7.6, 0.4, 2.8, 0.8, "[Câu hỏi] + [Đoạn văn]", "ext", 9.5)
    e3 = box(ax, 7.6, 1.8, 2.8, 1.1, "Bộ mã hóa đọc cả hai\n(chú ý chéo giữa từng từ)", "model", 9)
    s2 = box(ax, 7.9, 3.4, 2.2, 0.75, "điểm liên quan\n0 … 1", "key", 9.5, True)
    arrow(ax, top(qd), bottom(e3)); arrow(ax, top(e3), bottom(s2))
    ax.plot([6.0, 6.0], [0.3, 5.0], color="#BBBBBB", lw=1, ls=":")
    save(fig, "h2_4_bi_cross_encoder.png")


def fig_rrf():
    w, h = 13, 5.6
    fig, ax = canvas(w, h)
    title(ax, w, h, "Trộn thứ hạng RRF (k = 60): đoạn nào được nhiều cách xếp cao thì lên đầu")
    lists = {"TF-IDF": ["A", "B", "C", "D"], "BM25": ["B", "A", "D", "C"], "Vector nhúng": ["C", "B", "A", "D"]}
    for j, (name, r) in enumerate(lists.items()):
        x = 0.4 + j * 2.6
        ax.text(x + 1.0, 4.75, name, ha="center", fontsize=10, fontweight="bold")
        for i, item in enumerate(r):
            box(ax, x, 3.85 - i * 0.85, 2.0, 0.65, f"hạng {i + 1}: đoạn {item}", "data", 9)
    rrf = box(ax, 8.2, 1.95, 1.4, 1.5, "RRF\nΣ 1/(60+hạng)", "key", 9.5, True)
    ax.plot([7.75, 7.75], [1.3, 4.5], color="#444444", lw=1.3)
    for y in (4.17, 3.32, 2.47, 1.62):
        ax.plot([7.6, 7.75], [y, y], color="#444444", lw=1.0)
    arrow(ax, (7.75, 2.7), left(rrf))
    fused = [("B", 0.04865), ("A", 0.04840), ("C", 0.04789), ("D", 0.04712)]
    ax.text(11.6, 4.75, "Kết quả trộn", ha="center", fontsize=10, fontweight="bold")
    for i, (item, s) in enumerate(fused):
        box(ax, 10.3, 3.85 - i * 0.85, 2.6, 0.65, f"{i + 1}. đoạn {item}  ({s:.5f})", "proc", 9)
    arrow(ax, right(rrf), (10.3, 2.7))
    save(fig, "h2_5_tron_thu_hang_rrf.png")


def fig_lora():
    w, h = 11, 5.4
    fig, ax = canvas(w, h)
    title(ax, w, h, "LoRA: giữ nguyên ma trận gốc W, chỉ học hai ma trận nhỏ A và B")
    x_in = box(ax, 0.3, 2.1, 1.4, 0.9, "đầu vào x", "ext", 9.5)
    W = box(ax, 2.6, 3.0, 2.6, 1.4, "W (d × d)\nđóng băng\nkhông cập nhật", "data", 9.5, True)
    A = box(ax, 2.6, 0.5, 1.15, 1.6, "A\n(r × d)\nhọc", "model", 9.5, True)
    B = box(ax, 4.05, 0.5, 1.15, 1.6, "B\n(d × r)\nhọc", "model", 9.5, True)
    plus = Circle((6.6, 2.55), 0.35, fc="white", ec="#444444", lw=1.4)
    ax.add_patch(plus); ax.text(6.6, 2.55, "+", ha="center", va="center", fontsize=16)
    out = box(ax, 7.6, 2.1, 2.9, 0.9, "h = W·x + (α/r)·B·A·x", "key", 9.5, True)
    arrow(ax, right(x_in), left(W)); arrow(ax, right(x_in), left(A))
    arrow(ax, right(A), left(B))
    arrow(ax, right(W), (6.35, 2.8)); arrow(ax, right(B), (6.35, 2.3))
    arrow(ax, (6.95, 2.55), left(out))
    ax.text(5.5, 0.05, "Đề tài: r = 16, α = 32, gắn vào 7 lớp chiếu của Qwen3 4B (q, k, v, o, gate, up, down)", ha="center", fontsize=8.8, color="#555555")
    save(fig, "h2_6_lora.png")


# ---------- Chapter 3 ----------

def fig_system():
    w, h = 15, 7.6
    fig, ax = canvas(w, h)
    title(ax, w, h, "Kiến trúc tổng thể hệ thống TechStore")
    u1 = box(ax, 0.2, 5.3, 2.0, 0.9, "Khách mua\n(trình duyệt)", "ext", 9.5)
    u2 = box(ax, 0.2, 3.7, 2.0, 0.9, "Quản trị viên\n(trình duyệt)", "ext", 9.5)
    fe = box(ax, 2.9, 5.3, 2.3, 0.9, "Web bán hàng\nReact (frontend)", "proc", 9.2)
    ad = box(ax, 2.9, 3.7, 2.3, 0.9, "Trang quản trị\nReact (admin)", "proc", 9.2)
    be = box(ax, 6.0, 4.3, 2.4, 1.4, "Backend\nNode.js + Express\n(Render)", "proc", 9.2, True)
    fb = box(ax, 6.0, 2.4, 2.4, 1.1, "Bộ luật dự phòng\n(khi AI không\ntrả lời kịp)", "warn", 8.6)
    arrow(ax, right(u1), left(fe)); arrow(ax, right(u2), left(ad))
    arrow(ax, right(fe), (6.0, 5.2)); arrow(ax, right(ad), (6.0, 4.7))
    arrow(ax, bottom(be), top(fb), label="lỗi / quá 90 giây", size=8)
    ai = box(ax, 9.3, 3.7, 2.4, 2.6, "Dịch vụ AI\nFastAPI\n\n/api/chat/customer\n/api/chat/admin", "model", 9.2, True)
    arrow(ax, right(be), (9.3, 5.0), label="AI_SERVICE_URL", size=8)
    ol = box(ax, 12.5, 5.6, 2.3, 1.0, "Ollama\nQwen3 4B + LoRA", "model", 9)
    em = box(ax, 12.5, 4.3, 2.3, 1.0, "Dịch vụ vector\nvietnamese-\nembedding", "model", 8.8)
    db = box(ax, 12.5, 2.9, 2.3, 1.0, "shop.sqlite\n(dữ liệu shop)", "data", 9)
    dc = box(ax, 12.5, 1.5, 2.3, 1.0, "259 tài liệu\n(manifest.json)", "data", 9)
    for b in (ol, em, db, dc):
        arrow(ax, (11.7, 5.0), left(b), lw=1.0)
    ax.text(7.5, 0.5, "Web chạy trên Render; dịch vụ AI chạy riêng (máy cá nhân hoặc cloud GPU), web gọi qua biến AI_SERVICE_URL.", ha="center", fontsize=8.8, color="#555555")
    save(fig, "h3_1_kien_truc_he_thong.png")


def fig_sources():
    w, h = 15, 8.0
    fig, ax = canvas(w, h)
    title(ax, w, h, "Bản đồ nguồn dữ liệu của đề tài")
    s = [("Trang chính thức của hãng\n(Intel, Kingston, Lenovo…)", 6.2), ("docyx/pc-part-dataset\n(GitHub, MIT)", 5.1), ("Ryans laptop\n(Kaggle, Apache 2.0)", 4.1),
         ("Bộ dữ liệu sàn TMĐT\n(Kaggle, UCI)", 2.7), ("Trang hãng và\nnhà bán lẻ (ảnh)", 1.4), ("Hugging Face\n(Qwen3, PhoBERT)", 0.3)]
    sb = [box(ax, 0.2, y, 3.3, 0.8, t, "ext", 8.8) for t, y in s]
    docs = box(ax, 9.0, 5.6, 2.9, 1.3, "259 tài liệu RAG\n201 catalog, 43 kỹ thuật,\n10 sổ tay, 5 chính sách", "data", 8.8, True)
    ps = box(ax, 5.0, 4.3, 2.9, 1.4, "products.sqlite\n67 sản phẩm\n(48 linh kiện + 19 laptop)", "data", 8.8, True)
    sim = box(ax, 5.0, 2.5, 2.9, 1.3, "Bộ mô phỏng (simulator)\nchỉ lấy phân phối\nthống kê", "proc", 8.8)
    sc = box(ax, 9.0, 2.5, 2.9, 1.3, "shop.sqlite (MÔ PHỎNG)\n1.427 đơn, 365 ngày tồn\n99 khoản chi", "data", 8.8, True)
    img = box(ax, 5.0, 1.25, 2.9, 1.1, "Ảnh sản phẩm\n(chưa có quyền\nthương mại)", "warn", 8.8)
    mdl = box(ax, 9.0, 0.2, 2.9, 1.1, "Model nền\nApache 2.0", "model", 8.8)
    bot = box(ax, 12.8, 2.6, 2.0, 2.4, "Chatbot\nTechStore", "key", 10.5, True)
    arrow(ax, right(sb[0]), (9.0, 6.4), label="tóm tắt, có link", size=8)
    arrow(ax, right(sb[1]), (5.0, 5.15)); arrow(ax, right(sb[2]), (5.0, 4.85))
    arrow(ax, right(ps), (9.0, 5.9), label="sinh catalog", size=8)
    arrow(ax, (6.45, 4.3), (6.45, 3.8), label=None)
    arrow(ax, right(sb[3]), left(sim)); arrow(ax, right(sim), left(sc))
    arrow(ax, right(sb[4]), left(img)); arrow(ax, right(sb[5]), left(mdl))
    arrow(ax, right(docs), (12.8, 4.7), lw=1.0); arrow(ax, right(sc), (12.8, 3.3), lw=1.0); arrow(ax, right(mdl), (12.8, 2.75), lw=1.0)
    ax.text(6.45, 0.95, "hiển thị trên web, bot không dùng", ha="center", fontsize=8.2, color="#B83A3A")
    save(fig, "h3_2_ban_do_nguon_du_lieu.png")


def fig_shop_schema():
    w, h = 15, 8.4
    fig, ax = canvas(w, h)
    title(ax, w, h, "Lược đồ dữ liệu shop.sqlite: bảng sự kiện (vàng) và bảng chiều (xanh)")
    prod = box(ax, 5.9, 3.4, 3.2, 1.7, "products (67)\n──────────\nsku (PK), name, category\nprice, stock\n+ product_facts", "data", 8.8, True)
    facts = [
        (0.2, 6.2, "order_items (1.717)\nsku, quantity, list_price\ndiscount, revenue, cost"),
        (5.9, 6.2, "financial_ledger (1.748)\nday, sku, quantity\nrevenue, cost, kind"),
        (11.4, 6.2, "inventory_daily (24.455)\nday, sku, quantity, value"),
        (11.4, 3.5, "inventory_moves (2.126)\nday, sku, delta\ncost_delta, kind"),
        (11.4, 0.8, "returns (31)\nsku, quantity, refund\ncost_reversal, reason"),
        (5.9, 0.8, "purchase_lines (320)\n+ receipts (317)\nsku, quantity, unit_cost"),
    ]
    for x, y, t in facts:
        b = box(ax, x, y, 3.3, 1.35, t, "key", 8.6)
        arrow(ax, (b[0] + b[2] / 2, b[1] if y > 4 else b[1] + b[3]) if x == 5.9 else ((b[0] if x > 9 else b[0] + b[2]), b[1] + b[3] / 2),
              ((7.5, 5.1) if y > 4 else (7.5, 3.4)) if x == 5.9 else ((9.1 if x > 9 else 5.9), 4.25), style="-", lw=1.2)
    dims = [(0.2, 3.9, "orders (1.427)\nday, channel\ncustomer_id, campaign_id"), (0.2, 1.9, "customers (1.200)\nsegment"),
            (0.2, 0.2, "campaigns (3), suppliers (2)\noperating_expenses (99)\nmonthly_targets (12)")]
    for x, y, t in dims:
        box(ax, x, y, 3.3, 1.2 if y > 1 else 1.3, t, "data", 8.4)
    arrow(ax, (1.85, 6.2), (1.85, 5.1), style="-", lw=1.2)
    arrow(ax, (1.85, 3.9), (1.85, 3.1), style="-", lw=1.2)
    ax.text(4.6, 2.55, "VIEW monthly_pnl:\ndoanh thu thuần, giá vốn,\nlãi gộp, chi phí, mục tiêu\ntheo tháng (tính bằng SQL)", ha="center", fontsize=8.4,
            bbox=dict(fc="#F3ECFA", ec="#7B4FA8", boxstyle="round,pad=0.4"))
    save(fig, "h3_3_luoc_do_shop_sqlite.png")


def fig_etl():
    w, h = 15, 4.6
    fig, ax = canvas(w, h)
    title(ax, w, h, "Đường đi của dữ liệu trong dự án (ETL và làm mới hằng tháng)")
    steps = [("Nguồn gốc\nCSV, JSON,\nSQLite", "ext"), ("Chụp bản thô\n(de_snapshot)\ncó checksum", "proc"), ("Kiểm toán\n(de_audit)\nchỉ đọc", "proc"),
             ("Đối soát\n(de_reconcile)\nFIFO, tồn kho", "proc"), ("Bản tổng hợp\n(de_curated)\ncho admin", "data"), ("Làm mới tháng\n(monthly)\ntài liệu + chỉ mục", "proc"), ("Chatbot\ntruy xuất", "key")]
    bs = [box(ax, 0.2 + i * 2.12, 1.1, 1.85, 1.9, t, k, 8.8) for i, (t, k) in enumerate(steps)]
    for i in range(len(bs) - 1):
        arrow(ax, right(bs[i]), left(bs[i + 1]))
    ax.text(7.5, 0.35, "Nguyên tắc: mỗi bước chỉ đọc bước trước, không ghi đè dữ liệu đang chạy; sai một kiểm tra thì dừng (fail-closed).", ha="center", fontsize=8.8, color="#555555")
    save(fig, "h3_4_luong_du_lieu_etl.png")


def fig_question_flow():
    w, h = 13, 13.2
    fig, ax = canvas(w, h)
    title(ax, w, h, "Luồng xử lý một câu hỏi trong grounded_rag.answer")
    q = box(ax, 4.6, 11.7, 3.8, 0.8, "Câu hỏi + vai trò (khách / admin)\n+ lịch sử hội thoại", "ext", 9.2, True)
    d1 = (6.5, 10.65)
    diamond(ax, *d1, 4.6, 1.1, "Hỏi dữ liệu nội bộ,\nđòi sửa dữ liệu?")
    arrow(ax, bottom(q), (6.5, 11.2))
    r1 = box(ax, 10.0, 10.25, 2.7, 0.8, "Từ chối (denied)", "warn", 9)
    arrow(ax, (8.8, 10.65), left(r1), label="có", size=8)
    d2 = (6.5, 9.15)
    diamond(ax, *d2, 4.6, 1.1, "Admin hỏi phép tính\nrõ ràng? (shop_calc)")
    arrow(ax, (6.5, 10.1), (6.5, 9.7), label=None)
    r2 = box(ax, 10.0, 8.75, 2.7, 0.8, "Tính bằng SQL,\ntrả số + nguồn", "data", 8.8)
    arrow(ax, (8.8, 9.15), left(r2), label="có", size=8)
    d3 = (6.5, 7.65)
    diamond(ax, *d3, 4.6, 1.1, "Luật chặn (route_guard)\nnhận ra trường hợp rõ?")
    arrow(ax, (6.5, 8.6), (6.5, 8.2))
    r3 = box(ax, 10.0, 6.95, 2.7, 1.4, "đặt hàng → live_product\ngặp nhân viên → handoff\n\"con đó\" → clarify\nhãng lạ → unknown", "warn", 8.3)
    arrow(ax, (8.8, 7.65), left(r3), label="có", size=8)
    d4 = (6.5, 6.15)
    diamond(ax, *d4, 4.6, 1.1, "Tư vấn ngân sách /\ntra cứu sản phẩm?")
    arrow(ax, (6.5, 7.1), (6.5, 6.7))
    r4 = box(ax, 10.0, 5.75, 2.7, 0.8, "Lọc catalog trong\nshop.sqlite", "data", 8.8)
    arrow(ax, (8.8, 6.15), left(r4), label="có", size=8)
    rt = box(ax, 4.6, 4.25, 3.8, 0.9, "Router: Qwen3 4B + LoRA chọn hành động\n(answer, clarify, outside, deferred …)", "model", 8.8, True)
    arrow(ax, (6.5, 5.3), top(rt))
    ot = box(ax, 0.2, 4.25, 3.5, 0.9, "outside / clarify / deferred\n→ câu trả lời mẫu an toàn", "warn", 8.6)
    arrow(ax, left(rt), right(ot))
    rv = box(ax, 4.6, 2.65, 3.8, 0.95, "Truy xuất lai: TF-IDF + BM25 + vector\n→ trộn RRF → lọc theo vai trò, kỳ", "proc", 8.8, True)
    arrow(ax, bottom(rt), top(rv), label="answer", size=8)
    sel = box(ax, 4.6, 1.15, 3.8, 0.95, "Chọn câu bằng chứng (selector)\nchỉ trích nguyên văn tài liệu", "model", 8.8)
    arrow(ax, bottom(rv), top(sel))
    fin = box(ax, 4.6, 0.0, 3.8, 0.7, "Trả lời + nguồn trích dẫn", "key", 9.2, True)
    arrow(ax, bottom(sel), top(fin))
    for d in (d1, d2, d3, d4):
        ax.text(d[0] - 0.15, d[1] - 0.72, "không", fontsize=8, color="#555555", ha="right", va="center")
    save(fig, "h3_5_luong_xu_ly_cau_hoi.png")


def fig_hybrid():
    w, h = 15, 5.8
    fig, ax = canvas(w, h)
    title(ax, w, h, "Truy xuất lai (hybrid retrieval) trong retrieval.search")
    d = box(ax, 0.2, 2.2, 2.1, 1.4, "Tài liệu được\nphép xem\n(lọc vai trò, kỳ)", "data", 8.8)
    ch = box(ax, 2.9, 2.2, 2.0, 1.4, "Chia đoạn\n100 hoặc 180 từ\ngiữ tiêu đề", "proc", 8.8)
    arrow(ax, right(d), left(ch))
    sc = [("TF-IDF 1–2 từ\n+ cosine", 4.15), ("BM25\nk1 = 1,2; b = 0,75", 2.55), ("Vector nhúng\nPhoBERT 768 chiều", 0.95)]
    sb = []
    for t, y in sc:
        b = box(ax, 5.6, y, 2.4, 1.05, t, "model", 8.8)
        arrow(ax, right(ch), left(b))
        sb.append(b)
    rrf = box(ax, 8.8, 2.2, 1.9, 1.4, "RRF\nk = 60", "key", 10, True)
    for b in sb:
        arrow(ax, right(b), left(rrf))
    th = box(ax, 11.3, 2.2, 1.7, 1.4, "Ngưỡng:\nTF-IDF > 0,08\nhoặc vector\n> 0,45", "proc", 8.4)
    arrow(ax, right(rrf), left(th))
    tk = box(ax, 13.5, 2.2, 1.3, 1.4, "top-k\n(tối đa 12)", "data", 8.8, True)
    arrow(ax, right(th), left(tk))
    ax.text(7.5, 0.25, "Không có dịch vụ vector thì chỉ dùng TF-IDF (chế độ dự phòng).", ha="center", fontsize=8.8, color="#555555")
    save(fig, "h3_6_truy_xuat_lai.png")


def fig_train_eval():
    w, h = 16, 5.6
    fig, ax = canvas(w, h)
    title(ax, w, h, "Vòng huấn luyện và đánh giá trên Kaggle")
    steps = [("Sinh dữ liệu\ntừ đặc tả + DB\n(không dùng câu\nđánh giá)", "data"), ("Tách train /\ndev\n1.263 / 229", "data"), ("Fine-tune LoRA\nQwen3 4B\nKaggle T4", "model"),
             ("Xuất GGUF\nnạp Ollama", "model"), ("Chạy các bộ đề\n2 lần\n(base vs mới)", "proc")]
    bs = [box(ax, 0.2 + i * 2.55, 2.5, 2.2, 1.8, t, k, 8.8) for i, (t, k) in enumerate(steps)]
    for i in range(len(bs) - 1):
        arrow(ax, right(bs[i]), left(bs[i + 1]))
    diamond(ax, 14.4, 3.4, 2.6, 2.0, "Có câu\nđạt → trượt\nở mọi lần?", 8.6)
    arrow(ax, right(bs[-1]), (13.1, 3.4))
    ok = box(ax, 13.3, 0.4, 2.2, 0.9, "Không: dùng\nbản mới", "proc", 8.8, True)
    no = box(ax, 8.0, 0.4, 3.4, 0.9, "Có: giữ bản cũ,\nsửa lỗi rồi chạy lại", "warn", 8.8, True)
    arrow(ax, (14.4, 2.4), top(ok), label="không", size=8)
    arrow(ax, (13.75, 2.75), right(no), rad=-0.2, label="có", size=8)
    arrow(ax, left(no), bottom(bs[0]), rad=-0.25, ls="--", color="#B83A3A")
    save(fig, "h3_7_vong_huan_luyen_danh_gia.png")


def fig_results():
    banks = [("natural2\n(120 câu)", 101, 120), ("natural\n(120 câu)", 106, 120), ("policy\n(31 câu)", 29, 31),
             ("kb3 dev\n(479 câu)", 425, 479), ("kb3 val\n(121 câu)", 106, 121), ("expansion dev\n(354 câu)", 326, 354),
             ("expansion val\n(185 câu)", 142, 185), ("ngoài phạm vi\n(80 câu)", 57, 80)]
    fig, ax = plt.subplots(figsize=(11, 4.8))
    names = [b[0] for b in banks]
    pct = [b[1] / b[2] * 100 for b in banks]
    bars = ax.bar(names, pct, color=["#2F6DB5"] * 7 + ["#C46A1B"], width=0.62)
    for bar, (n, p, t) in zip(bars, banks):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1.2, f"{p}/{t}\n{p * 1000 // t / 10 + (0.1 if p * 1000 % t * 2 >= t else 0):.1f}%", ha="center", fontsize=8.6)
    ax.set_ylim(0, 112)
    ax.set_ylabel("tỉ lệ câu đạt (%)")
    ax.set_title("Kết quả bản đánh giá 19 trên Kaggle (natural2 chấm theo cách chấm mới)", fontsize=11.5, fontweight="bold")
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(axis="x", labelsize=8.6)
    ax.grid(axis="y", alpha=0.25)
    save(fig, "h3_8_ket_qua_ban_19.png")


for f in [fig_dw_architecture, fig_star_schema, fig_kdd, fig_crisp, fig_taxonomy, fig_text_pipeline, fig_vector_space, fig_knn,
          fig_encoders, fig_rrf, fig_lora, fig_system, fig_sources, fig_shop_schema, fig_etl, fig_question_flow, fig_hybrid,
          fig_train_eval, fig_results]:
    f()
