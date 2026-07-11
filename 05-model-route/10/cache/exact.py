def exact_key(system: str, user: str, model: str) -> str:
    return f"{model}|{system}|{user}"


class ExactCache:
    def __init__(self):
        self._store: dict[str, str] = {}

    def get(self, system: str, user: str, model: str) -> str | None:
        return self._store.get(exact_key(system, user, model))

    def set(self, system: str, user: str, model: str, value: str) -> None:
        self._store[exact_key(system, user, model)] = value
