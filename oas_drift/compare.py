"""compare — OpenAPI spec と実装 route の照合（純関数）。

検出する drift（元スコープどおり）:
  spec_only    — spec に定義されているが実装コードに route が無い
  code_only    — 実装コードに route があるが spec に定義されていない
  method_mismatch — path は一致するが HTTP method が異なる
"""
from collections import Counter
from collections import defaultdict


def compare(spec_endpoints: dict, code_routes: list) -> dict:
    """spec endpoints と code routes を比較する（純関数）。

    spec_endpoints: {"/path": {"get", "post", ...}} — spec.extract_endpoints の出力
    code_routes: [{path, method, file, line}] — routes.extract_routes の出力
    返り値: {status_counts, findings, ok_count}
    findings の status: spec_only | code_only | method_mismatch
    """
    # code routes を path → {methods} に集約
    code_by_path = defaultdict(set)
    route_locations = defaultdict(list)
    for r in code_routes:
        code_by_path[r["path"]].add(r["method"])
        route_locations[r["path"]].append(r)

    spec_paths = set(spec_endpoints)
    code_paths = set(code_by_path)

    findings = []

    # spec にのみ存在（未実装）
    for path in sorted(spec_paths - code_paths):
        methods = ", ".join(sorted(m.upper() for m in spec_endpoints[path]))
        findings.append({
            "status": "spec_only", "path": path,
            "detail": f"defined in spec ({methods}) but no matching route in codebase",
        })

    # code にのみ存在（spec 未定義）
    for path in sorted(code_paths - spec_paths):
        methods = ", ".join(sorted(m.upper() for m in code_by_path[path]))
        locs = ", ".join(f"{r['file']}:{r['line']}" for r in route_locations[path][:2])
        findings.append({
            "status": "code_only", "path": path,
            "detail": f"route implemented ({methods}) but not defined in spec — {locs}",
        })

    # path は一致するが method が異なる
    for path in sorted(spec_paths & code_paths):
        spec_methods = spec_endpoints[path]
        code_methods = code_by_path[path]
        only_spec = spec_methods - code_methods
        only_code = code_methods - spec_methods
        if only_spec or only_code:
            bits = []
            if only_spec:
                bits.append(f"in spec but not implemented: {', '.join(sorted(m.upper() for m in only_spec))}")
            if only_code:
                bits.append(f"implemented but not in spec: {', '.join(sorted(m.upper() for m in only_code))}")
            locs = ", ".join(f"{r['file']}:{r['line']}" for r in route_locations[path][:2])
            findings.append({
                "status": "method_mismatch", "path": path,
                "detail": f"{path}: " + "; ".join(bits) + f" — {locs}",
            })

    # ok のカウント
    ok_paths = spec_paths & code_paths
    ok_count = 0
    for path in ok_paths:
        if spec_endpoints[path] & code_by_path[path]:
            ok_count += 1

    findings.sort(key=lambda f: (f["status"], f["path"]))
    status_counts = dict(Counter(f["status"] for f in findings))
    return {
        "status_counts": status_counts,
        "findings": findings,
        "ok_count": ok_count,
        "spec_total": len(spec_paths),
        "code_total": len(code_paths),
    }

