from typing import Any


def api_response(data: Any, *, meta: dict[str, Any] | None = None) -> dict[str, Any]:
    result: dict[str, Any] = {"data": data}
    if meta is not None:
        result["meta"] = meta
    return result
