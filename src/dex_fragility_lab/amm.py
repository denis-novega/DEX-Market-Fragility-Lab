from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Side = Literal["buy", "sell", "add_liquidity", "remove_liquidity"]


@dataclass(frozen=True)
class PoolEvent:
    """A single local simulation event."""

    step: int
    actor: str
    side: Side
    base_delta: float
    token_delta: float
    price_before: float
    price_after: float
    price_impact_pct: float
    note: str = ""


@dataclass
class AMMPool:
    """Simplified constant-product AMM pool.

    `base_reserve` can be read as the quote asset reserve, while
    `token_reserve` is the simulated token reserve. No network calls are made.
    """

    base_reserve: float
    token_reserve: float
    fee_bps: float = 30.0

    def __post_init__(self) -> None:
        if self.base_reserve <= 0 or self.token_reserve <= 0:
            raise ValueError("Pool reserves must be positive.")
        if self.fee_bps < 0 or self.fee_bps >= 10_000:
            raise ValueError("fee_bps must be between 0 and 10000.")

    @property
    def price(self) -> float:
        """Current token price in units of base asset."""
        return self.base_reserve / self.token_reserve

    @property
    def depth(self) -> float:
        """Approximate pool depth measured as total reserve value in base units."""
        return self.base_reserve * 2

    def _fee_multiplier(self) -> float:
        return 1.0 - self.fee_bps / 10_000.0

    def buy_token(self, base_amount: float) -> tuple[float, float, float]:
        """Swap simulated base asset into token.

        Returns `(token_out, price_before, price_after)`.
        """
        if base_amount <= 0:
            raise ValueError("base_amount must be positive.")

        price_before = self.price
        effective_in = base_amount * self._fee_multiplier()
        token_out = self.token_reserve * effective_in / (self.base_reserve + effective_in)

        self.base_reserve += base_amount
        self.token_reserve -= token_out
        return token_out, price_before, self.price

    def sell_token(self, token_amount: float) -> tuple[float, float, float]:
        """Swap simulated token into base asset.

        Returns `(base_out, price_before, price_after)`.
        """
        if token_amount <= 0:
            raise ValueError("token_amount must be positive.")

        price_before = self.price
        effective_in = token_amount * self._fee_multiplier()
        base_out = self.base_reserve * effective_in / (self.token_reserve + effective_in)

        self.token_reserve += token_amount
        self.base_reserve -= base_out
        return base_out, price_before, self.price

    def add_liquidity(self, base_amount: float, token_amount: float) -> tuple[float, float]:
        """Add local simulated liquidity."""
        if base_amount <= 0 or token_amount <= 0:
            raise ValueError("Liquidity amounts must be positive.")
        before = self.price
        self.base_reserve += base_amount
        self.token_reserve += token_amount
        return before, self.price

    def remove_liquidity_fraction(self, fraction: float) -> tuple[float, float, float, float]:
        """Remove a fraction of simulated pool liquidity.

        Returns `(base_out, token_out, price_before, price_after)`.
        """
        if fraction <= 0 or fraction >= 1:
            raise ValueError("fraction must be between 0 and 1.")
        price_before = self.price
        base_out = self.base_reserve * fraction
        token_out = self.token_reserve * fraction
        self.base_reserve -= base_out
        self.token_reserve -= token_out
        return base_out, token_out, price_before, self.price


def price_impact_pct(before: float, after: float) -> float:
    if before == 0:
        return 0.0
    return ((after - before) / before) * 100.0
