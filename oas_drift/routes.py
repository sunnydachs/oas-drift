from pathlib import Path
"""routes — Python ソースから route decorator を抽出する（純関数）。

対応するデコレータ形式（FastAPI / Flask 系）:
  @app.get("/items/{item_id}")          # FastAPI style
  @router.post("/items")                # router prefix
  @app.route("/path", methods=["GET"])  # Flask style
  @api_v1.get("/path")                  # 変数レシーバ

抽出方法: ast で decorator を走査し、
  - func が Attribute で attr が HTTP method 名 → FastAPI style
  - func が Attribute で attr == "route" → Flask style（methods kw から抽出）
"""
import ast

HTTP_DECORATORS = {"get", "post", "put", "delete", "patch", "head", "options", "trace"}


def _literal_str(node) -> str | None:
    if node is not None and isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def extract_routes(py_source: str, source_path: str = "<text>") -> list:
    """Python ソースから route 定義を抽出する（純関数）。

    返り値: [{path, method, file, line}]
    """
    out = []
    try:
        tree = ast.parse(py_source)
    except SyntaxError:
        return out

    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for dec in node.decorator_list:
            if not isinstance(dec, ast.Call):
                continue
            func = dec.func
            if not isinstance(func, ast.Attribute):
                continue

            # FastAPI style: @app.get("/path") / @router.post("/path")
            if func.attr in HTTP_DECORATORS:
                path = _literal_str(dec.args[0]) if dec.args else None
                if path:
                    out.append({"path": path, "method": func.attr.lower(),
                                "file": source_path, "line": dec.lineno})

            # Flask style: @app.route("/path", methods=["GET"])
            elif func.attr == "route":
                path = _literal_str(dec.args[0]) if dec.args else None
                if path:
                    methods_kw = [kw.value for kw in dec.keywords if kw.arg == "methods"]
                    if methods_kw and isinstance(methods_kw[0], (ast.List, ast.Tuple)):
                        for elt in methods_kw[0].elts:
                            s = _literal_str(elt)
                            if s:
                                out.append({"path": path, "method": s.lower(),
                                            "file": source_path, "line": dec.lineno})
                    else:
                        out.append({"path": path, "method": "get",
                                    "file": source_path, "line": dec.lineno})
    return out


def find_python_files(root: Path, max_files: int = 3000) -> list:
    skip = {".git", ".venv", "venv", "node_modules", "__pycache__",
            "build", "dist", ".tox", ".mypy_cache", ".pytest_cache"}
    out = []
    for p in sorted(Path(root).rglob("*.py")):
        if any(part in skip for part in p.parts):
            continue
        out.append(p)
        if len(out) >= max_files:
            break
    return out


def find_routes(root: Path, max_files: int = 3000) -> list:
    """リポジトリ全体から route 定義を収集する。"""
    routes = []
    for p in find_python_files(root, max_files):
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        routes.extend(extract_routes(text, source_path=p.as_posix()))
    return routes
