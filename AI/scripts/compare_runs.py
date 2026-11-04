"""Compare evaluation archives and print a concise release-gate report."""

import argparse
import json
import re
import sys
import zipfile
from pathlib import Path


PASS = "PASS_CHECKS"
GROUPS = ("stable_lost", "stable_won", "flaky", "stable_pass", "stable_fail")
ARCHIVE_NAME = re.compile(r"^(?P<bank>.+)__kaggle_(?P<tag>.+)_(?P<split>[^_]+)\.zip$")
ALWAYS_LOCKED = {"validation"}
LOCKED_BANK_PREFIX = "heldout"


class ArchiveError(ValueError):
    """An archive or its results payload does not satisfy the input contract."""


def _read_rows(path):
    path = Path(path)
    try:
        with zipfile.ZipFile(path) as archive:
            try:
                raw = archive.read("results.json")
            except KeyError as exc:
                raise ArchiveError(f"{path}: missing results.json") from exc
    except (OSError, zipfile.BadZipFile) as exc:
        raise ArchiveError(f"{path}: invalid or unreadable zip archive") from exc
    try:
        rows = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ArchiveError(f"{path}: results.json is not valid UTF-8 JSON") from exc
    if not isinstance(rows, list):
        raise ArchiveError(f"{path}: results.json must contain a list")
    return path, rows


def load_run(path):
    """Load one archive as {(split, case_id): passed}, for the legacy API."""
    path, rows = _read_rows(path)
    results = {}
    for index, row in enumerate(rows):
        label = f"{path}: results.json row {index}"
        if not isinstance(row, dict):
            raise ArchiveError(f"{label} must be an object")
        case_id, split = row.get("id"), row.get("split")
        checks = row.get("checks")
        if not isinstance(case_id, str) or not case_id.strip():
            raise ArchiveError(f"{label} has missing or invalid id")
        if not isinstance(split, str) or not split.strip():
            raise ArchiveError(f"{label} has missing or invalid split")
        if not isinstance(checks, dict) or not isinstance(checks.get("status"), str):
            raise ArchiveError(f"{label} has missing or invalid checks.status")
        key = (split, case_id)
        if key in results:
            raise ArchiveError(f"{path}: duplicate split/id entry in results.json")
        results[key] = checks["status"] == PASS
    return results


def _only_deferred_routing(issues):
    """True when the frozen deferred label is the row's sole complaint."""
    return isinstance(issues, list) and bool(issues) and all(
        isinstance(issue, dict)
        and issue.get("cause") == "ROUTING"
        and isinstance(issue.get("detail"), dict)
        and issue["detail"].get("expected") == "deferred"
        for issue in issues
    )


def _load_detailed(path):
    """Load outcomes and only the fields needed for calc_label classification."""
    _, rows = _read_rows(path)
    outcomes = {}
    for index, row in enumerate(rows):
        label = f"{path}: results.json row {index}"
        if not isinstance(row, dict):
            raise ArchiveError(f"{label} must be an object")
        case_id, split = row.get("id"), row.get("split")
        checks = row.get("checks")
        if not isinstance(case_id, str) or not case_id.strip():
            raise ArchiveError(f"{label} has missing or invalid id")
        if not isinstance(split, str) or not split.strip():
            raise ArchiveError(f"{label} has missing or invalid split")
        if not isinstance(checks, dict) or not isinstance(checks.get("status"), str):
            raise ArchiveError(f"{label} has missing or invalid checks.status")
        key = (split, case_id)
        if key in outcomes:
            raise ArchiveError(f"{path}: duplicate split/id entry in results.json")
        rag = (row.get("result") or {}).get("rag", {}) if isinstance(row.get("result"), dict) else {}
        outcomes[key] = {
            "passed": checks["status"] == PASS,
            "calc_label": _only_deferred_routing(checks.get("issues"))
            and isinstance(rag, dict)
            and rag.get("method") == "deterministic SQL calculation",
        }
    return outcomes


def compare(base_runs, candidate_runs, locked_splits=()):
    """Return per-split counts and IDs, with locked IDs omitted by construction."""
    if not base_runs or not candidate_runs:
        raise ValueError("at least one base and one candidate run are required")
    all_runs = list(base_runs) + list(candidate_runs)
    key_union = set().union(*(run.keys() for run in all_runs))
    key_common = set.intersection(*(set(run) for run in all_runs))
    splits = sorted({split for split, _ in key_union})
    locked = set(locked_splits)
    report = {}
    for split in splits:
        keys = {key for key in key_union if key[0] == split}
        common = sorted(key for key in key_common if key[0] == split)
        base_missing = len(keys - set.intersection(*(set(run) for run in base_runs)))
        candidate_missing = len(keys - set.intersection(*(set(run) for run in candidate_runs)))
        counts = {group: 0 for group in GROUPS}
        ids = {group: [] for group in ("stable_lost", "stable_won", "flaky")}
        for key in common:
            before = [run[key] for run in base_runs]
            after = [run[key] for run in candidate_runs]
            if len(set(before)) > 1 or len(set(after)) > 1:
                group = "flaky"
            elif all(before) and not any(after):
                group = "stable_lost"
            elif not any(before) and all(after):
                group = "stable_won"
            elif all(before) and all(after):
                group = "stable_pass"
            else:
                group = "stable_fail"
            counts[group] += 1
            if group in ids:
                ids[group].append(key[1])
        report[split] = {
            "counts": counts,
            "base_missing": base_missing,
            "candidate_missing": candidate_missing,
            "ids": None if split in locked else ids,
        }
    return report


def _directory_runs(directory):
    directory = Path(directory)
    result_dir = directory / "results"
    if not result_dir.is_dir():
        raise ArchiveError(f"{directory}: missing results directory")
    grouped = {}
    for path in sorted(result_dir.glob("*.zip")):
        match = ARCHIVE_NAME.match(path.name)
        if not match:
            continue
        bank, tag, archive_split = match.group("bank", "tag", "split")
        rows = _load_detailed(path)
        by_split = {}
        for key, value in rows.items():
            split = key[0]
            if archive_split != "all" and split != archive_split:
                continue
            by_split.setdefault(split, {})[key] = value
        for split, entries in by_split.items():
            grouped.setdefault((bank, split), []).append((tag, entries))
    return grouped


def _gate_report(base_dir, candidate_dir, locked_splits):
    base = _directory_runs(base_dir)
    candidate = _directory_runs(candidate_dir)
    keys = sorted(set(base) | set(candidate))
    locked = set(locked_splits) | ALWAYS_LOCKED
    sections = []
    blockers = []
    if not set(base) & set(candidate):
        blockers.append("kh\u00f4ng c\u00f3 b\u1ed9 n\u00e0o \u0111\u1ec3 so")
    for bank, split in keys:
        title = f"bank={bank} split={split}"
        name = f"{bank}/{split}"
        if (bank, split) not in base:
            sections.append(f"{title}\n  THI\u1ebeU \u1ede B\u1ea2N G\u1ed0C")
            continue
        if (bank, split) not in candidate:
            sections.append(f"{title}\n  THI\u1ebeU \u1ede \u1ee8NG VI\u00caN")
            blockers.append(f"{name} thi\u1ebfu \u1edf \u1ee9ng vi\u00ean")
            continue
        b_runs = [run for _, run in base[(bank, split)]]
        c_runs = [run for _, run in candidate[(bank, split)]]
        hidden = split in locked or bank.startswith(LOCKED_BANK_PREFIX)
        report = compare(
            [{key: value["passed"] for key, value in run.items()} for run in b_runs],
            [{key: value["passed"] for key, value in run.items()} for run in c_runs],
            (split,) if hidden else (),
        ).get(split)
        if report is None:
            sections.append(f"{title}\n  KH\u00d4NG C\u00d3 H\u00c0NG CHUNG")
            blockers.append(f"{name} kh\u00f4ng c\u00f3 h\u00e0ng chung")
            continue
        calc_ids = []
        common = set.intersection(*(set(run) for run in b_runs + c_runs))
        for key in sorted(common):
            before = [run[key]["passed"] for run in b_runs]
            after = [run[key]["passed"] for run in c_runs]
            if all(before) and not any(after) and all(run[key]["calc_label"] for run in c_runs):
                calc_ids.append(key[1])
        counts = report["counts"]
        remaining_lost = counts["stable_lost"] - len(calc_ids)
        if remaining_lost:
            blockers.append(f"{name} m\u1ea5t {remaining_lost} c\u00e2u")
        if report["candidate_missing"]:
            blockers.append(f"{name} thi\u1ebfu {report['candidate_missing']} c\u00e2u \u1edf \u1ee9ng vi\u00ean")
        lines = [title]
        lines.extend(f"  run {tag}: pass={sum(v['passed'] for v in entries.values())}" for tag, entries in base[(bank, split)])
        lines.extend(f"  run {tag}: pass={sum(v['passed'] for v in entries.values())}" for tag, entries in candidate[(bank, split)])
        lines.extend(f"  {group}: {counts[group]}" for group in ("stable_lost", "stable_won", "flaky"))
        lines.append(f"  calc_label: {len(calc_ids)}")
        lines.append(f"  stable_lost_con_tinh: {remaining_lost}")
        lines.append(f"  missing: base={report['base_missing']}, candidate={report['candidate_missing']}")
        if report["ids"] is not None:
            for group in ("stable_lost", "stable_won", "flaky"):
                lines.append(f"  {group}_ids: {', '.join(report['ids'][group]) or '-'}")
            lines.append(f"  calc_label_ids: {', '.join(calc_ids) or '-'}")
        sections.append("\n".join(lines))
    sections.append("C\u1ed4NG: \u0110\u1ea0T" if not blockers else f"C\u1ed4NG: CH\u01afA \u0110\u1ea0T: {', '.join(blockers)}")
    return "\n\n".join(sections)


def render(report):
    lines = []
    for split, item in report.items():
        lines.append(f"split={split}")
        for group in GROUPS:
            lines.append(f"  {group}: {item['counts'][group]}")
        lines.append(f"  missing: base={item['base_missing']}, candidate={item['candidate_missing']}")
        if item["ids"] is not None:
            for group in ("stable_lost", "stable_won", "flaky"):
                lines.append(f"  {group}_ids: {', '.join(item['ids'][group]) or '-'}")
    return "\n".join(lines)


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", nargs="+", metavar="ZIP")
    parser.add_argument("--base-dir", metavar="DIR")
    parser.add_argument("--candidate-dir", metavar="DIR")
    parser.add_argument("--candidate", nargs="+", metavar="ZIP")
    parser.add_argument("--locked-split", nargs="+", default=[], metavar="SPLIT")
    args = parser.parse_args(argv)
    if (args.base is None) == (args.base_dir is None):
        parser.error("use either --base with --candidate ZIPs or --base-dir with --candidate-dir")
    if bool(args.base_dir) != bool(args.candidate_dir):
        parser.error("--base-dir and --candidate-dir must be used together")
    if args.base is not None and args.candidate is None:
        parser.error("--candidate is required with --base")
    if args.base_dir and args.candidate is not None:
        parser.error("--candidate ZIP cannot be used with --base-dir")
    return args


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    args = parse_args(argv)
    try:
        if args.base_dir:
            output = _gate_report(args.base_dir, args.candidate_dir, args.locked_split)
        else:
            base_runs = [load_run(path) for path in args.base]
            candidate_runs = [load_run(path) for path in args.candidate]
            report = compare(base_runs, candidate_runs, args.locked_split)
            output = render(report)
            lost = sum(item["counts"]["stable_lost"] for item in report.values())
            output += "\n" + ("C\u1ed4NG: \u0110\u1ea0T" if lost == 0 else f"C\u1ed4NG: CH\u01afA \u0110\u1ea0T ({lost} stable_lost c\u00f2n l\u1ea1i)")
    except (ArchiveError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
