# DEX Market Fragility Lab

A local-only research bench for demonstrating why thin-liquidity decentralized exchange markets can be fragile, noisy, and easy to misread.

The project models a simplified automated market maker (AMM), synthetic wallets, price impact, apparent volume, liquidity changes, and basic risk indicators. It is designed for education, risk analysis, and personal portfolio documentation — not for trading automation or real-market activity.

## Research purpose

Decentralized markets often look transparent because every transaction is visible on-chain. This project demonstrates the opposite risk: visibility does not guarantee that the activity is organic, economically meaningful, or resistant to coordinated behavior. In low-liquidity pools, small coordinated actions can distort price, volume, and perceived demand.

The goal of the repository is to show an approximate process behind market distortion in a controlled simulation, so that readers understand why many DEX token markets are structurally vulnerable and why trading them can be highly unreliable.

## Safety and scope

This repository intentionally contains no live-chain execution code:

- no RPC endpoints;
- no private keys or wallet files;
- no token deployment scripts;
- no exchange/router integration;
- no automated buy/sell bot;
- no instructions for operating on real DEX markets.

Everything runs locally with synthetic balances and a toy AMM model. The repository is meant to support research communication, responsible education, and risk awareness.

## What the simulation includes

- constant-product AMM model;
- synthetic wallet cohort;
- liquidity addition and withdrawal events;
- local-only swaps against simulated pool reserves;
- price impact and volume tracking;
- risk flags for low liquidity, high concentration, and abnormal activity.

## Repository structure

```text
.
├── assets/                  # static assets for the project page
├── data/                    # generated local outputs, ignored by Git
├── docs/                    # website copy and research notes
├── examples/                # runnable local examples
├── src/dex_fragility_lab/   # local simulation package
├── .gitignore
├── LICENSE
├── MIGRATION_NOTES.md
├── README.md
├── pyproject.toml
└── requirements.txt
```

## Run the local demo

Python 3.10+ is recommended.

```bash
python examples/run_scenario.py
```

The script prints a compact event log and saves a CSV report to `data/scenario_report.csv`.

## Interpretation

The simulation should be read as a risk demonstration, not as a market strategy. It shows how price and volume can be shaped by liquidity depth and synthetic activity, especially when a pool has shallow reserves. In such environments, on-chain metrics can be technically public but economically misleading.

P.S - if interested in live scripts - contact
