from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from dex_fragility_lab import AMMPool, ScenarioRunner, Wallet


def main() -> None:
    pool = AMMPool(base_reserve=12.0, token_reserve=120_000.0, fee_bps=30)
    wallets = [Wallet(name=f"synthetic_wallet_{i:02d}", base_balance=0.6) for i in range(1, 16)]

    runner = ScenarioRunner(pool=pool, wallets=wallets, seed=42)
    runner.coordinated_buy_phase(participants=8, base_amount_range=(0.10, 0.45))
    runner.churn_phase(rounds=30, max_base_amount=0.08)
    runner.liquidity_shock(fraction=0.35)
    runner.churn_phase(rounds=15, max_base_amount=0.05)

    for event in runner.events[:8]:
        print(
            f"#{event.step:02d} {event.actor:<20} {event.side:<16} "
            f"price {event.price_before:.8f} -> {event.price_after:.8f} "
            f"impact={event.price_impact_pct:+.2f}%"
        )

    if len(runner.events) > 8:
        print(f"... {len(runner.events) - 8} more events")

    print("\nRisk summary")
    for key, value in runner.risk_summary().items():
        print(f"- {key}: {value}")

    report_path = ROOT / "data" / "scenario_report.csv"
    runner.write_csv(report_path)
    print(f"\nCSV report written to: {report_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
