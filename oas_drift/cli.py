"""cli — oas-drift コマンドライン入口（読み取り専用・dry-run のみ）。

usage:
  oas-drift --spec openapi.json [ROOT]    # spec と実装を照合（既定: .）
  oas-drift --spec openapi.json . --json  # 機械可読出力
"""
import argparse
import json

from oas_drift import scanner

MARK = {
    "spec_only": "⬜ SPEC ONLY",
    "code_only": "➕ CODE ONLY",
    "method_mismatch": "⚠️ METHOD MISMATCH",
}


def render(report: dict, json_output: bool) -> str:
    if json_output:
        return json.dumps(report, ensure_ascii=False, indent=2)

    lines = [
        f"oas-drift — scanned {report['root']}",
        f"  spec: {report['spec_total']} endpoint(s) | code: {report['code_total']} route(s)",
        "",
    ]
    if not report["findings"]:
        lines.append("no drift detected: spec and implementation are aligned.")
    for f in report["findings"]:
        lines.append(f"{f['path']}  {MARK.get(f['status'], f['status'])}")
        lines.append(f"    {f['detail']}")
    lines.append("")
    lines.append(f"summary: {json.dumps(report['status_counts'], ensure_ascii=False)} "
                 f"| ok: {report['ok_count']}")
    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="oas-drift",
        description="Detect drift between OpenAPI spec and the implementation. Read-only.")
    ap.add_argument("--spec", required=True, help="OpenAPI spec JSON file")
    ap.add_argument("root", nargs="?", default=".", help="repository root (default: .)")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args(argv)

    report = scanner.scan(args.spec, args.root)
    print(render(report, json_output=args.json))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
