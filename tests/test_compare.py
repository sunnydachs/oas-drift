import pytest

from oas_drift.compare import compare
from oas_drift.spec import extract_endpoints
from oas_drift.routes import extract_routes


def _spec(paths: dict) -> dict:
    return extract_endpoints({"paths": paths})


def _routes(routes: list) -> list:
    out = []
    for path, method in routes:
        out.append({"path": path, "method": method,
                    "file": "a.py", "line": 1})
    return out


SPEC = _spec({
    "/items": {"get": {}, "post": {}},
    "/users/{id}": {"get": {}},
})


def test_ok_when_aligned():
    routes = _routes([("/items", "get"), ("/items", "post"), ("/users/{id}", "get")])
    r = compare(SPEC, routes)
    assert r["findings"] == []
    assert r["ok_count"] == 2  # /items (get+post で1、/users/{id} で1)


def test_spec_only_detected():
    routes = _routes([("/items", "get")])
    r = compare(SPEC, routes)
    statuses = {f["path"]: f["status"] for f in r["findings"]}
    assert statuses["/items"] == "method_mismatch"     # post が未実装
    assert statuses["/users/{id}"] == "spec_only"      # code に無い


def test_code_only_detected():
    routes = _routes([("/items", "get"), ("/items", "post"),
                      ("/users/{id}", "get"), ("/extra", "delete")])
    r = compare(SPEC, routes)
    co = [f for f in r["findings"] if f["status"] == "code_only"]
    assert len(co) == 1
    assert co[0]["path"] == "/extra"


def test_method_mismatch_detected():
    routes = _routes([("/items", "put")])   # spec は get+post、code は put のみ
    r = compare(SPEC, routes)
    mm = [f for f in r["findings"] if f["status"] == "method_mismatch"]
    assert len(mm) == 1
    assert "POST" in mm[0]["detail"]


def test_empty_spec_all_code_only():
    routes = _routes([("/x", "get")])
    r = compare({}, routes)
    assert r["findings"][0]["status"] == "code_only"


def test_empty_code_all_spec_only():
    r = compare(SPEC, [])
    assert all(f["status"] == "spec_only" for f in r["findings"])
    assert len(r["findings"]) == 2  # /items, /users/{id}
