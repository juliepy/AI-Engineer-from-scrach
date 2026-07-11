import re


def _normalize(text: str) -> set[str]:
    return set(re.findall(r"[\w\u4e00-\u9fff]+", text.lower()))


def jaccard(a: str, b: str) -> float:
    sa, sb = _normalize(a), _normalize(b)
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


class SemanticCache:
    """演示用语义缓存：Jaccard 相似度 > 阈值即命中（生产用向量 + 阈值 + TTL）。"""

    def __init__(self, threshold: float = 0.85):
        self.threshold = threshold
        self._entries: list[tuple[str, str]] = []

    def get(self, query: str) -> tuple[str | None, float, str | None]:
        best_score = 0.0
        best_answer = None
        best_query = None
        for cached_q, ans in self._entries:
            score = jaccard(query, cached_q)
            if score > best_score:
                best_score = score
                best_answer = ans
                best_query = cached_q
        if best_score >= self.threshold:
            return best_answer, best_score, best_query
        return None, best_score, best_query

    def set(self, query: str, answer: str) -> None:
        self._entries.append((query, answer))
