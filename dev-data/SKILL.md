---
name: dev-data
description: "Data engineering and analysis guide for orchestrated sub-agents. Data pipelines, ETL/ELT design, data quality validation, SQL optimization, and analysis patterns. Injected when role=data."
---

# Dev-Data — Data Engineering & Analysis Guide

Production-grade data engineering patterns for building reliable data systems.

## When to Activate

- Building data pipelines or ETL/ELT processes
- Processing CSV, JSON, Parquet, or Excel files
- Writing SQL queries or designing database schemas
- Setting up data quality checks or validation
- Performing data analysis, aggregation, or reporting
- Choosing between batch and streaming architectures

---

## 1. Data Processing Principles

Five rules that apply to every data task:

| Principle | What It Means |
|-----------|---------------|
| **Pipeline thinking** | Every pipeline is Extract → Transform → Load. Keep each stage as an independent, testable function. |
| **Schema-first** | Define expected columns, types, and constraints BEFORE writing transformation logic. |
| **Defensive parsing** | External data will have nulls, wrong types, extra columns, missing columns, and encoding issues. Assume all of these. |
| **Idempotent operations** | Running the same pipeline twice on the same input must produce the same output. Use upsert patterns, not blind inserts. |
| **Fail fast, fail loud** | Invalid data must raise errors immediately. Silent failures produce wrong results downstream that are 10x harder to debug. |

---

## 2. Data Ingestion Patterns

### Format-Specific Guidance

| Format | Best For | Watch Out For |
|--------|----------|---------------|
| **CSV** | Simple tabular data, human-readable | Encoding (UTF-8 BOM), delimiter ambiguity, multiline values, inconsistent quoting |
| **JSON** | Nested structures, API responses | Large files (stream, don't load all at once), deeply nested objects, encoding |
| **Parquet** | Large analytical datasets, columnar queries | Requires library support, not human-readable, schema evolution |
| **Excel** | Business user handoffs | Multiple sheets, merged cells, formulas vs. values, date formatting |
| **Database** | Production system access | Connection pooling, query timeouts, use read replicas for analytics |

### Incremental Loading

For large or frequently updated data sources:

1. Use a **watermark column** (e.g., `updated_at`, `id`) to track the last processed record.
2. Store the watermark after successful load. On failure, restart from the last saved watermark.
3. Process in batches (1000-10000 rows), not all-at-once.
4. Validate row counts: `loaded_rows` should equal `source_rows_since_watermark`.

### Schema Validation on Ingest

Before any transformation, validate incoming data:

```
✅ Check: Expected columns exist
✅ Check: Data types match (string, number, date, boolean)
✅ Check: Required fields are not null
✅ Check: Values are within expected ranges
✅ Check: No unexpected duplicate keys
❌ Fail: If any check fails, write to error log with row details. Don't silently drop.
```

---

## 3. ETL/ELT Pipeline Design

### Layer Architecture

```
Raw / Staging        →    Transformation      →    Marts / Output
(exact copy of            (cleaning, joins,         (business-ready
 source data,              deduplication,            aggregations,
 never modified)           type casting)             final tables)
```

**Rules:**
- **Staging is sacrosanct.** Never modify raw data. Copy first, transform in a separate step.
- **One transformation per step.** Don't combine cleaning + joining + aggregating in one function. Chain separate steps.
- **Incremental processing.** Process only new/changed records when possible. Full reloads only when schema changes.

### dbt Integration Patterns

When using dbt for transformations, follow the **staging → intermediate → mart** layer architecture:

```
models/
├── staging/          # 1:1 with source tables, light cleaning only
│   ├── stg_orders.sql
│   └── stg_customers.sql
├── intermediate/     # Business logic, joins, deduplication
│   └── int_order_enriched.sql
└── marts/            # Business-ready facts and dimensions
    ├── fct_daily_revenue.sql
    └── dim_customers.sql
```

**Rules:**
- **Staging models**: rename, cast, filter NULLs — no joins, no business logic
- **Intermediate models**: joins across staging, deduplication, business transforms
- **Mart models**: aggregations, final business entities consumed by BI/analytics
- Every model has a `schema.yml` with tests:

```yaml
models:
  - name: stg_orders
    columns:
      - name: order_id
        tests: [not_null, unique]
      - name: amount
        tests: [not_null]
```

- Run `dbt test` after every `dbt run` — treat test failures as pipeline failures
- Use `dbt source freshness` to monitor upstream data staleness

### Error Handling in Pipelines

| Scenario | Pattern |
|----------|---------|
| **Invalid records** | Write to dead-letter table/file for manual review. Never drop silently. |
| **Source unavailable** | Retry with exponential backoff (1s, 2s, 4s). Alert after 3 failures. |
| **Schema mismatch** | Halt pipeline. Log expected vs. actual schema. Don't attempt partial loads. |
| **Duplicate records** | Use upsert (INSERT ON CONFLICT UPDATE) or deduplicate with window functions. |

### Orchestration Basics

When pipelines have multiple steps with dependencies:

- Define tasks as a **DAG** (Directed Acyclic Graph). Each task depends on its upstream tasks.
- Each task must be **independently retryable**. If step 3 fails, you restart step 3, not step 1.
- Set reasonable retries (2-3) with delay (5 min between attempts).
- Add timeout per task to prevent hung pipelines.
- Alert on failure: email, Slack, or monitoring dashboard.

---

## 4. Data Quality

### Validation Checks

Run these after every pipeline step, not just at the end:

| Check | What It Validates | Example |
|-------|-------------------|---------|
| **Not null** | Required fields have values | `WHERE order_id IS NULL` → 0 rows |
| **Unique** | No duplicates on key columns | `COUNT(*) = COUNT(DISTINCT id)` |
| **Range** | Numeric values within bounds | `amount BETWEEN 0 AND 1,000,000` |
| **Categorical** | Values in allowed set | `status IN ('pending', 'active', 'closed')` |
| **Freshness** | Data is recent enough | `MAX(updated_at) > NOW() - INTERVAL '24 hours'` |
| **Row count** | No unexpected data loss or explosion | Within ±10% of previous run |
| **Referential** | Foreign keys point to existing records | `customer_id EXISTS IN customers` |

### Quality Tool Integration

Use a **layered quality strategy** — different tools at different pipeline stages:

| Stage | Tool | Purpose |
|-------|------|---------|
| **Ingest** | Great Expectations | Validate raw data against expectations before staging |
| **Transform** | dbt tests | Assert model-level quality (not_null, unique, relationships, custom SQL) |
| **Production** | Soda / Monte Carlo | Real-time monitoring, anomaly detection, SLA enforcement |

**Great Expectations pattern:**
```python
validator.expect_column_values_to_not_be_null("order_id")
validator.expect_column_values_to_be_between("amount", min_value=0, max_value=1_000_000)
validator.expect_column_distinct_values_to_be_in_set(
    "status", ["pending", "confirmed", "shipped", "delivered"]
)

results = validator.validate()
if not results.success:
    raise DataQualityError(f"Validation failed: {results.statistics}")
```

**Rule:** Never skip validation because "the data looks fine." Silent quality failures produce wrong downstream results that are 10x harder to debug.

### Data Contracts

For datasets shared between teams, define a contract:

```yaml
contract:
  name: orders_data_contract
  owner: data-team
  version: "1.0"

schema:
  order_id:    { type: string, not_null: true, unique: true }
  customer_id: { type: string, not_null: true }
  amount:      { type: decimal, min: 0, max: 1000000 }
  status:      { type: string, enum: [pending, confirmed, shipped, delivered] }
  created_at:  { type: timestamp, not_null: true }

sla:
  freshness: max_delay_hours: 1
  completeness: min_valid_percentage: 99.9

consumers:
  - analytics-team: "Daily dashboards"
  - ml-team: "Churn prediction model"
```

Changes to a contracted schema require **versioning and consumer notification**.

---

## 5. Analysis & Reporting

### Always Start with Summary Statistics

Before any deep analysis, provide:

| Metric | What to Report |
|--------|----------------|
| Row count | Total records in dataset |
| Column inventory | Name, type, null count per column |
| Numeric summary | min, max, mean, median, std dev |
| Categorical summary | Unique values, top 5 most frequent |
| Time range | Earliest and latest timestamp |
| Data quality | Null percentage, duplicate percentage |

### Output Formats

| Format | When to Use |
|--------|-------------|
| **Markdown tables** | Inline reports, ≤50 rows, quick summaries |
| **JSON** | Programmatic consumption, API responses |
| **CSV export** | Handoff to spreadsheet users, large datasets |
| **HTML + charts** | Dashboards, visual reports (Chart.js, Mermaid diagrams) |

### Statistical Reporting

When analysis involves statistics:
- State the method used and its assumptions.
- Report confidence intervals, not just point estimates.
- Visualize distributions (histograms, box plots), not just averages.
- Distinguish correlation from causation explicitly.

---

## 6. Architecture Decisions

### Batch vs. Streaming

```
Is real-time insight required (latency <1 minute)?
├── YES → Streaming
│   └── Need exactly-once semantics?
│       ├── YES → Kafka + Flink / Spark Structured Streaming
│       └── NO  → Kafka + consumer groups (simpler)
└── NO → Batch
    └── Daily data volume >1TB?
        ├── YES → Distributed processing (Spark, Databricks)
        └── NO  → Single-node processing (SQL, Python, dbt)
```

**Default to batch.** Streaming adds significant complexity in error handling, state management, and debugging. Only use streaming when latency requirements genuinely demand it.

### Streaming Decision Tiers

| Latency Requirement | Framework | Complexity |
|---------------------|-----------|------------|
| <100ms, complex stateful | Apache Flink | High (dedicated cluster) |
| <1s, existing Spark infra | Spark Structured Streaming | Medium |
| <1s, Kafka-centric | Kafka Streams (embedded library) | Low-Medium |
| >1min acceptable | Batch with frequent scheduling | Low |

**Kafka essentials for data engineers:**
- Partition by expected throughput — avoid excessive partitions
- Use Schema Registry for backwards-compatible evolution
- Default to at-least-once delivery + idempotent consumers
- Use exactly-once only for financial/billing (transactional producers + consumers)
- Monitor consumer lag via Prometheus/Grafana

See `references/streaming.md` for Kafka configuration, CDC patterns, and windowing.

### Storage Selection

| Need | Choose |
|------|--------|
| SQL analytics, BI dashboards, structured queries | Data warehouse (Snowflake, BigQuery, PostgreSQL) |
| ML training, unstructured data, large-scale storage | Data lake (S3/GCS + Parquet or Delta format) |
| Both SQL and ML needs | Lakehouse (Delta Lake, Apache Iceberg) |
| Real-time key-value lookups, caching | Redis, DynamoDB |
| Graph relationships | Neo4j, Neptune |

### Tool Selection

| Category | Options |
|----------|---------|
| **Orchestration** | Airflow, Prefect, Dagster |
| **Transformation** | dbt, Spark, plain SQL |
| **Streaming** | Kafka, Kinesis, Pub/Sub |
| **Quality** | Great Expectations, dbt tests, Soda, custom validators |
| **Monitoring** | Prometheus, Grafana, Datadog, Monte Carlo |
| **Local analysis** | DuckDB (in-process SQL), Polars (fast DataFrame), pandas (exploration/ML) |

### Tool Decision Matrix

| Factor | pandas | Polars | DuckDB |
|--------|--------|--------|--------|
| **Best for** | <1GB, exploration, ML prep | >1GB, batch ETL, performance | SQL analytics, ad-hoc queries |
| **Execution** | Single-threaded, eager | Multi-threaded Rust, lazy eval | Vectorized, auto disk spill |
| **Speed (groupby/join)** | Baseline | 5-10x faster | Matches Polars on SQL-native |
| **Memory** | Full load into RAM | Streaming, lazy chains | Spill-to-disk for out-of-core |
| **API style** | DataFrame (imperative) | DataFrame (expression-based) | SQL-first |
| **ML interop** | Excellent (scikit-learn, etc.) | Good (`.to_pandas()`) | Good (`.fetchdf()`) |
| **File format** | CSV, JSON, Excel | CSV, Parquet, Arrow-native | CSV, Parquet, JSON, S3 direct |

**Decision rule:**
```
Data size?
├── <100MB, interactive exploration → pandas
├── >100MB, <10GB batch transforms → Polars
├── SQL-first analytics, any size → DuckDB
└── Blended workflow → Polars transforms → DuckDB aggregations
```

**Interop patterns:**
```python
# Polars → DuckDB (zero-copy via Arrow)
import polars as pl
import duckdb

df = pl.scan_parquet("events/*.parquet").filter(pl.col("status") == "active").collect()
result = duckdb.sql("SELECT user_id, COUNT(*) as cnt FROM df GROUP BY user_id ORDER BY cnt DESC LIMIT 10")

# DuckDB → Polars
arrow_table = duckdb.sql("SELECT * FROM 'data.parquet' WHERE amount > 100").arrow()
df = pl.from_arrow(arrow_table)
```

See `references/tools.md` for full patterns and code examples.

---

## 7. Data Governance & PII

### Data Classification

| Level | Examples | Handling |
|-------|----------|---------|
| **Public** | Aggregated metrics, public reports | No restrictions |
| **Internal** | Business KPIs, operational data | Access controls, no external sharing |
| **Confidential** | Customer data, financial records | Encryption at rest, column-level masking |
| **Restricted** | SSN, payment data, health records | Tokenization, row-level security, audit logging |

### PII Handling Checklist

Before building any pipeline that touches PII:
- [ ] Classify all columns by sensitivity level
- [ ] Apply masking/tokenization for non-production environments (static masking)
- [ ] Implement dynamic masking for production queries (role-based)
- [ ] Set data retention TTL — don't keep PII longer than needed
- [ ] Support right-to-erasure (GDPR Article 17): cascading delete across all pipeline stages
- [ ] Log all PII access for audit trail
- [ ] Never log raw PII values — mask in structured logging

### GDPR/CCPA Quick Reference

| Requirement | Engineering Pattern |
|-------------|---------------------|
| Right to erasure | Soft delete → batch purge → propagate to downstream stores including data lake |
| Data minimization | Collect only necessary fields; TTL on non-essential data |
| Consent tracking | Consent event store with versioned preferences; consent-aware pipeline branches |
| Data portability | Standardized export endpoint (JSON/CSV) per user request |

See `references/governance.md` for detailed implementation patterns, row-level security, and retention policies.

---

## 8. Companion Skills

Data engineering does not exist in isolation. Cross-reference these skills when your pipeline connects to other systems:

| Companion | When to Consult | Key Sections |
|-----------|-----------------|--------------|
| `dev-backend` | Exposing data via API, response envelope shape, pagination | §5 API Response Contract, §2 Layered Architecture |
| `dev-security` | PII handling, data classification, access controls, audit logging | §1 Input Validation, §4 Secrets, §8 Pre-Flight |
| `dev-testing` | Pipeline validation, contract tests for data APIs, CI gates | §2 Backend Patterns, §3 Contract Testing |
| `dev-frontend` | Downstream reporting/dashboard consumers, data format expectations | §8 Backend Contract Alignment |

**Integration patterns:**
- Data APIs serving frontend dashboards must use the standard response envelope (`dev-backend` §4.5)
- PII pipelines must classify columns and apply masking per `dev-security` guidance before this skill's §7 rules
- Data contract changes (§4 Data Contracts) must notify downstream consumers including frontend teams

---

Clean data enables good decisions. Your pipeline is only as trustworthy as your weakest validation check — make every check count.
