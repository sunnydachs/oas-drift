"""spec — OpenAPI spec JSON のパースと endpoint 抽出（純関数）。

対応: OpenAPI 3.x JSON ファイル（YAML は将来対応）。
paths オブジェクトから {path: {methods}} を抽出する。
非 HTTP method キー（parameters, summary 等）は無視する。
"""
import json

HTTP_METHODS = {"get", "post", "put", "delete", "patch", "head", "options", "trace"}


def load_spec(path) -> dict:
    return json.loads(open(path, encoding="utf-8").read())


def extract_endpoints(spec: dict) -> dict:
    """OpenAPI spec から {"/path": {"get", "post", ...}} を抽出する（純関数）。

    paths オブジェクトの各キーがパス、各値の HTTP method キーがメソッド。
    非メソッドキー（parameters, summary, description 等）は無視する。
    """
    paths = spec.get("paths") or {}
    out = {}
    for path, methods in paths.items():
        if not isinstance(methods, dict):
            continue
        http = {m for m in methods if m.lower() in HTTP_METHODS}
        if http:
            out[path] = {m.lower() for m in http}
    return out
