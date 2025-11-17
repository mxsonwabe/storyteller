# DECISIONS

## Heuristic and ranking
- I used the weighting to order events, and differentiated by minutes so that the
  highlights are ordered correctly.

## Data handling (duplicates, missing fields, out‑of‑order minutes)
- I exclude values that are `null` to ensure the are no missing values, and use
  a set to ensure no duplicates are stored.

## Pack structure and invariants
- Pack is organised according to the schema given, and the different objects are
  modeled as base models.

## What I would do with 2 more hours
- Clean-up the UI to add a bit more styling and animation.
