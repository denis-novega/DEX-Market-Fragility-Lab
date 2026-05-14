# Research notes

## Core observation

DEX markets are transparent at the transaction layer but can still be fragile at the market-structure layer. Thin liquidity, concentrated control, and synthetic-looking activity can produce misleading signals.

## What the local model illustrates

1. **Price impact sensitivity** — shallow reserves amplify the effect of small trades.
2. **Apparent volume risk** — repeated activity can look like demand without representing broad market participation.
3. **Liquidity shock risk** — sudden liquidity removal reduces depth and makes later price movements more extreme.
4. **Metric ambiguity** — on-chain visibility provides data, but interpretation remains difficult.

## Responsible framing

The public project should be framed as a defensive and educational demonstration. It should not include live execution paths, exchange connectors, automated trading logic, or operational instructions for real token markets.
