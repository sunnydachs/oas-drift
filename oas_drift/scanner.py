"""scanner — OpenAPI spec + リポジトリ走査から drift レポートを作る（読み取り専用）。"""
from pathlib import Path

from oas_drift.compare import compare
from oas_drift.routes import find_routes
from oas_drift.spec import extract_endpoints, load_spec


def scan(spec_path, root) -> dict:
    """spec_path の OpenAPI spec と root のコードを照合する。

    返り値: {spec_path, root, spec_total, code_total, status_counts,
             findings, ok_count}
    """
    spec = load_spec(spec_path)
    endpoints = extract_endpoints(spec)
    routes = find_routes(root)
    res = compare(endpoints, routes)
    return {
        "spec_path": str(spec_path),
        "root": str(root),
        "spec_total": res["spec_total"],
        "code_total": res["code_total"],
        "status_counts": res["status_counts"],
        "findings": res["findings"],
        "ok_count": res["ok_count"],
    }
