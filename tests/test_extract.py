import pytest

from oas_drift.spec import extract_endpoints, load_spec
from oas_drift.routes import extract_routes


def test_extract_endpoints_basic():
    spec = {"paths": {
        "/items": {"get": {"summary": "List"}, "post": {"summary": "Create"}},
        "/items/{id}": {"get": {"summary": "Read"}, "parameters": []},
        "/non-method-key": {"summary": "not an endpoint", "parameters": []},
    }}
    r = extract_endpoints(spec)
    assert r == {"/items": {"get", "post"}, "/items/{id}": {"get"}}
    assert "/non-method-key" not in r


def test_extract_endpoints_empty():
    assert extract_endpoints({}) == {}
    assert extract_endpoints({"paths": {}}) == {}


def test_extract_routes_fastapi():
    src = '''
from fastapi import FastAPI
app = FastAPI()

@app.get("/items/{item_id}")
def read_item(item_id: int):
    pass

@app.post("/items")
def create_item():
    pass
'''
    routes = extract_routes(src, "main.py")
    assert len(routes) == 2
    assert routes[0]["path"] == "/items/{item_id}"
    assert routes[0]["method"] == "get"
    assert routes[1]["method"] == "post"


def test_extract_routes_flask_style():
    src = '''
@app.route("/users", methods=["GET", "POST"])
def users():
    pass
'''
    routes = extract_routes(src)
    assert len(routes) == 2
    assert {(r["path"], r["method"]) for r in routes} == {("/users", "get"), ("/users", "post")}


def test_extract_routes_router_prefix():
    src = '''
@router.get("/items")
def list_items():
    pass
'''
    routes = extract_routes(src)
    assert routes[0]["path"] == "/items"
    assert routes[0]["method"] == "get"


def test_extract_routes_non_route_decorator_ignored():
    src = '''
@app.cache_result
def cached_fn():
    pass

@app.get("/real")
def real_route():
    pass
'''
    routes = extract_routes(src)
    assert len(routes) == 1
    assert routes[0]["method"] == "get"


def test_extract_routes_syntax_error():
    assert extract_routes("def broken(:\n") == []
