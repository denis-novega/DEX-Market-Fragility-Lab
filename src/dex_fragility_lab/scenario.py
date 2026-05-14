from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import csv
import random
from typing import Iterable

from .amm import AMMPool, PoolEvent, price_impact_pct


@dataclass
class Wallet:
    """Synthetic local wallet used only inside the simulator."""

    name: str
    base_balance: float
    token_balance: float = 0.0


class ScenarioRunner:
    """Runs local-only stress scenarios against a toy AMM pool."""

    def __init__(self, pool: AMMPool, wallets: Iterable[Wallet], seed: int = 7) -> None:
        self.pool = pool
        self.wallets = list(wallets)
        self.random = random.Random(seed)
        self.events: list[PoolEvent] = []
        self._step = 0

    def _record(
        self,
        actor: str,
        side: str,
        base_delta: float,
        token_delta: float,
        price_before: float,
        price_after: float,
        note: str = "",
    ) -> None:
        self._step += 1
        self.events.append(
            PoolEvent(
                step=self._step,
                actor=actor,
                side=side,  # type: ignore[arg-type]
                base_delta=base_delta,
                token_delta=token_delta,
                price_before=price_before,
                price_after=price_after,
                price_impact_pct=price_impact_pct(price_before, price_after),
                note=note,
            )
        )

    def coordinated_buy_phase(self, participants: int, base_amount_range: tuple[float, float]) -> None:
        """Synthetic buy pressure phase in a local pool."""
        for wallet in self.wallets[:participants]:
            amount = min(wallet.base_balance, self.random.uniform(*base_amount_range))
            if amount <= 0:
                continue
            token_out, before, after = self.pool.buy_token(amount)
            wallet.base_balance -= amount
            wallet.token_balance += token_out
            self._record(wallet.name, "buy", -amount, token_out, before, after, "synthetic local buy")

    def churn_phase(self, rounds: int, max_base_amount: float) -> None:
        """Alternates small local buys and sells to illustrate noisy apparent activity."""
        for _ in range(rounds):
            wallet = self.random.choice(self.wallets)
            if self.random.random() < 0.55 and wallet.base_balance > 0:
                amount = min(wallet.base_balance, self.random.uniform(0.01, max_base_amount))
                token_out, before, after = self.pool.buy_token(amount)
                wallet.base_balance -= amount
                wallet.token_balance += token_out
                self._record(wallet.name, "buy", -amount, token_out, before, after, "synthetic churn")
            elif wallet.token_balance > 0:
                amount = min(wallet.token_balance, wallet.token_balance * self.random.uniform(0.05, 0.30))
                base_out, before, after = self.pool.sell_token(amount)
                wallet.token_balance -= amount
                wallet.base_balance += base_out
                self._record(wallet.name, "sell", base_out, -amount, before, after, "synthetic churn")

    def liquidity_shock(self, fraction: float) -> None:
        """Removes local simulated liquidity to show depth fragility."""
        base_out, token_out, before, after = self.pool.remove_liquidity_fraction(fraction)
        self._record("pool_operator", "remove_liquidity", -base_out, -token_out, before, after, "local liquidity shock")

    def risk_summary(self) -> dict[str, float | int]:
        volume_base = sum(abs(event.base_delta) for event in self.events if event.side in {"buy", "sell"})
        max_abs_impact = max((abs(event.price_impact_pct) for event in self.events), default=0.0)
        event_count = len(self.events)
        low_depth_flag = 1 if self.pool.depth < 50 else 0
        high_impact_flag = 1 if max_abs_impact > 10 else 0
        return {
            "event_count": event_count,
            "final_price": round(self.pool.price, 8),
            "final_depth_base_units": round(self.pool.depth, 4),
            "apparent_volume_base_units": round(volume_base, 4),
            "max_abs_price_impact_pct": round(max_abs_impact, 4),
            "low_depth_flag": low_depth_flag,
            "high_impact_flag": high_impact_flag,
        }

    def write_csv(self, path: str | Path) -> None:
        output = Path(path)
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(PoolEvent.__dataclass_fields__.keys()))
            writer.writeheader()
            for event in self.events:
                writer.writerow(event.__dict__)
