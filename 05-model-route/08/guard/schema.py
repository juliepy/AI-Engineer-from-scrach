from typing import Any, Dict


SCHEMAS: Dict[str, Dict[str, Any]] = {
    "search": {
        "type": "object",
        "required": ["q"],
        "properties": {"q": {"type": "string", "minLength": 1, "maxLength": 200}},
    },
    "send_email": {
        "type": "object",
        "required": ["to", "subject"],
        "properties": {
            "to": {"type": "string", "format": "email"},
            "subject": {"type": "string", "maxLength": 100},
        },
    },
}


def validate_args(tool_name: str, args: dict) -> None:
    schema = SCHEMAS.get(tool_name)
    if schema is None:
        raise ValueError(f"no schema for tool '{tool_name}'")

    if not isinstance(args, dict):
        raise TypeError("args must be dict")
    for key in schema.get("required", []):
        if key not in args:
            raise ValueError(f"missing required field: {key}")
    props = schema.get("properties", {})
    for key, val in args.items():
        if key not in props:
            raise ValueError(f"unknown field: {key}")
        spec = props[key]
        if spec.get("type") == "string" and not isinstance(val, str):
            raise TypeError(f"{key} must be string")
        if "maxLength" in spec and len(val) > spec["maxLength"]:
            raise ValueError(f"{key} too long")
        if "minLength" in spec and len(val) < spec["minLength"]:
            raise ValueError(f"{key} too short")
