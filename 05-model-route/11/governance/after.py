from dataclasses import dataclass, field
from typing import List


@dataclass
class FeedbackRecord:
    query: str
    answer: str
    user_rating: int  # 1~5
    flagged_hallucination: bool


@dataclass
class AfterAudit:
    records: List[FeedbackRecord] = field(default_factory=list)

    def log_feedback(self, record: FeedbackRecord) -> None:
        self.records.append(record)

    def hallucination_rate(self) -> float:
        if not self.records:
            return 0.0
        flagged = sum(1 for r in self.records if r.flagged_hallucination)
        return round(flagged / len(self.records) * 100, 2)

    def needs_review(self, threshold_pct: float = 5.0) -> bool:
        return self.hallucination_rate() >= threshold_pct
