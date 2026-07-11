from dataclasses import dataclass, field
from typing import List


PRICE_PER_1M = {
    "gpt-4o-pro": 10.0,
    "gpt-4o": 5.0,
    "gpt-4o-mini": 0.5,
    "static-template": 0.0,
}


@dataclass
class BillRecord:
    model: str
    prompt_tokens: int
    completion_tokens: int
    cost_usd: float
    degraded: bool


@dataclass
class BillingLedger:
    records: List[BillRecord] = field(default_factory=list)

    def record(
        self,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
        degraded: bool = False,
    ) -> BillRecord:
        rate = PRICE_PER_1M.get(model, 1.0)
        total = prompt_tokens + completion_tokens
        cost = round(total / 1_000_000 * rate, 6)
        entry = BillRecord(model, prompt_tokens, completion_tokens, cost, degraded)
        self.records.append(entry)
        return entry

    def total_cost(self) -> float:
        return round(sum(r.cost_usd for r in self.records), 6)
