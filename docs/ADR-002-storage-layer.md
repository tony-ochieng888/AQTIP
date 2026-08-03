# ADR-002: Persistent Storage Layer

## Status

Accepted

## Context

AQTIP requires a reliable and efficient way to persist validated market data for:

- Backtesting
- Feature Engineering
- Machine Learning
- Strategy Development

CSV files are simple but inefficient for analytical workloads.

## Decision

Store validated datasets using Apache Parquet.

Storage responsibilities are isolated inside the `storage` package.

The storage layer determines sensible default filenames from the application configuration, reducing duplication and improving consistency.

## Consequences

Advantages

- Efficient storage
- Faster loading
- Smaller file sizes
- Preserves data types
- Easy integration with pandas

Trade-offs

- Requires the `pyarrow` dependency.
- Binary format is not directly human-readable.