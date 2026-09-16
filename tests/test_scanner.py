"""scanner / CLI 結合テスト（tmp リポジトリで完結・オフライン）。"""
import json

from oas_drift.cli import main
from oas_drift import scanner
from oas_drift.spec import load_spec


def _make_project(tmp_path):
    (tmp_path / "main.py").write_text(
        "from fastapi import FastAPI\n"
        "app = FastAPI()\n\n"
        "@app.get('/items')\n"
        "def list_items():\n    pass\n\n"
        "@app.post('/items')\n"
        "def create_item():\n    pass\n\n"
        "@app.get('/items/{item_id}')\n"
        "def read_item(item_id: int):\n    pass\n\n"
        "@app.delete('/items/{item_id}')\n"
        "def delete_item(item_id: int):\n    pass\n"
    )
    plan = tmp_path / "openapi.json"
    plan.write_text(json.dumps({
        "openapi": "3.1.0",
        "paths": {
            "/items": {"get": {}, "post": {}},
            "/items/{item_id}": {"get": {}, "delete": {}},
        },
    }))
    return plan


def test_scan_clean(tmp_path):
    _make_project(tmp_path)
    r = scanner.scan(tmp_path / "openapi.json", tmp_path)
    assert r["findings"] == []
    assert r["ok_count"] == 2  # /items, /items/{item_id}


def test_cli_main_json(tmp_path, capsys):
    _make_project(tmp_path)
    rc = main(["--spec", str(tmp_path / "openapi.json"), str(tmp_path), "--json"])
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert data["ok_count"] == 2
    assert data["findings"] == []
