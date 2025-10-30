"""Fallback implementations mimicking the subset of Pydantic used in tests."""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional

__all__ = ["BaseModel", "Field", "validator"]


class _UnsetType:
    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return "<UNSET>"


_UNSET = _UnsetType()


class _FieldInfo:
    def __init__(self, *, default: Any = _UNSET, default_factory: Optional[Callable[[], Any]] = None):
        self.default = default
        self.default_factory = default_factory


def Field(default: Any = _UNSET, *, default_factory: Optional[Callable[[], Any]] = None) -> _FieldInfo:
    return _FieldInfo(default=default, default_factory=default_factory)


def validator(*fields: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        setattr(func, "_pydantic_validator_fields", fields)
        return func

    return decorator


class BaseModelMeta(type):
    def __new__(mcls, name: str, bases: tuple[type, ...], namespace: Dict[str, Any]):
        annotations: Dict[str, Any] = namespace.get("__annotations__", {})

        fields: Dict[str, _FieldInfo] = {}
        validators: Dict[str, List[Callable[..., Any]]] = {}
        for base in bases:
            fields.update(getattr(base, "__fields__", {}))
            for key, funcs in getattr(base, "__validators__", {}).items():
                validators.setdefault(key, []).extend(funcs)

        new_namespace = dict(namespace)

        for attr_name, attr_value in namespace.items():
            if callable(attr_value) and hasattr(attr_value, "_pydantic_validator_fields"):
                for field_name in getattr(attr_value, "_pydantic_validator_fields"):
                    validators.setdefault(field_name, []).append(attr_value)

        for field_name in annotations:
            if field_name in namespace:
                attr_value = namespace[field_name]
                if isinstance(attr_value, _FieldInfo):
                    fields[field_name] = attr_value
                    new_namespace.pop(field_name)
                else:
                    fields[field_name] = _FieldInfo(default=attr_value)
                    new_namespace.pop(field_name)
            elif field_name not in fields:
                fields[field_name] = _FieldInfo()

        new_namespace["__fields__"] = fields
        new_namespace["__validators__"] = validators
        return super().__new__(mcls, name, bases, new_namespace)


class BaseModel(metaclass=BaseModelMeta):
    __fields__: Dict[str, _FieldInfo]
    __validators__: Dict[str, List[Callable[..., Any]]]

    def __init__(self, **data: Any) -> None:
        values: Dict[str, Any] = {}
        remaining = dict(data)
        for name, info in self.__class__.__fields__.items():
            if name in remaining:
                value = remaining.pop(name)
            elif info.default is not _UNSET:
                value = info.default
            elif info.default_factory is not None:
                value = info.default_factory()
            elif hasattr(self.__class__, name):
                value = getattr(self.__class__, name)
            else:
                raise ValueError(f"Missing required field '{name}' for {self.__class__.__name__}")

            for validator_func in self.__class__.__validators__.get(name, []):
                value = validator_func(self.__class__, value)
            setattr(self, name, value)
            values[name] = value

        for key, value in remaining.items():
            setattr(self, key, value)
            values[key] = value

        self.__dict__.update(values)

    def model_dump(self) -> Dict[str, Any]:  # pragma: no cover - helper used in debugging
        return {name: getattr(self, name) for name in self.__class__.__fields__}

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        fields = ", ".join(f"{key}={getattr(self, key)!r}" for key in self.__class__.__fields__)
        return f"{self.__class__.__name__}({fields})"
