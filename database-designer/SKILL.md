---
name: database-designer
description: "Database schema design, normalization (1NF–BCNF), index optimization, migration strategies, partitioning, and database selection guide. Use when designing schemas, optimizing queries, or planning database architecture."
---

# Database Designer

Expert-level database design covering schema analysis, index optimization, migrations, and architecture decisions.

---

## Normalization

### First Normal Form (1NF)
- Atomic values in each column (no comma-separated lists)
- Unique column names, uniform data types
- No duplicate rows

```sql
-- BAD: multiple values in one column
CREATE TABLE contacts (id INT PRIMARY KEY, phones VARCHAR(200)); -- "123, 456"

-- GOOD: separate table
CREATE TABLE contact_phones (
    id INT PRIMARY KEY,
    contact_id INT REFERENCES contacts(id),
    phone_number VARCHAR(20)
);
```

### Second Normal Form (2NF)
- Satisfies 1NF
- No partial dependencies on composite keys

### Third Normal Form (3NF)
- Satisfies 2NF
- No transitive dependencies (non-key → non-key)

### When to Denormalize

| Scenario | Pattern |
|----------|---------|
| Read-heavy workloads | Redundant storage (cache customer_name in orders) |
| Frequent aggregations | Materialized aggregates (pre-computed summary tables) |
| Performance bottlenecks from joins | Controlled denormalization + triggers for sync |

---

## Index Strategies

### B-Tree (Default)
Best for: range queries, sorting, equality. Most selective columns first in composite indexes.

```sql
-- Composite: match query WHERE + ORDER pattern
CREATE INDEX idx_task_status_date ON tasks (status, created_date, priority DESC);
```

### Covering Index
```sql
-- Avoid table lookups by including extra columns
CREATE INDEX idx_user_email_cover ON users (email) INCLUDE (first_name, last_name, status);
```

### Partial Index
```sql
-- Index only relevant subset
CREATE INDEX idx_active_users ON users (email) WHERE status = 'active';
CREATE INDEX idx_recent_orders ON orders (customer_id, created_at)
    WHERE created_at > CURRENT_DATE - INTERVAL '30 days';
```

### Index Selection Checklist
1. Identify WHERE clause columns
2. Most selective column first
3. Consider JOIN conditions
4. Include ORDER BY columns if possible
5. Check for existing overlapping indexes

---

## Data Modeling Patterns

### Star Schema (Warehousing)
```sql
CREATE TABLE sales_facts (
    sale_id BIGINT PRIMARY KEY,
    product_id INT REFERENCES products(id),
    customer_id INT REFERENCES customers(id),
    date_id INT REFERENCES date_dimension(id),
    quantity INT, total_amount DECIMAL(10,2)
);
```

### JSON Document Model
```sql
CREATE TABLE documents (
    id UUID PRIMARY KEY,
    document_type VARCHAR(50),
    data JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_doc_user ON documents USING GIN ((data->>'user_id'));
```

### Hierarchical Data
```sql
-- Materialized path pattern
CREATE TABLE categories (
    id INT PRIMARY KEY, name VARCHAR(100),
    parent_id INT REFERENCES categories(id),
    path VARCHAR(500)  -- "/1/5/12/"
);
```

---

## Migration Strategies

### Zero-Downtime (Expand-Contract)

**Phase 1 — Expand:**
```sql
ALTER TABLE users ADD COLUMN new_email VARCHAR(255);
-- Backfill in batches
UPDATE users SET new_email = email WHERE id BETWEEN 1 AND 1000;
-- Add constraints after backfill
ALTER TABLE users ADD CONSTRAINT users_new_email_unique UNIQUE (new_email);
```

**Phase 2 — Contract:**
```sql
-- After app updated to use new column:
ALTER TABLE users DROP COLUMN email;
ALTER TABLE users RENAME COLUMN new_email TO email;
```

---

## Partitioning

### Range (by date)
```sql
CREATE TABLE sales_2024 PARTITION OF sales
    FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');
```

### Hash (by user)
```sql
CREATE TABLE user_data_0 PARTITION OF user_data
    FOR VALUES WITH (MODULUS 4, REMAINDER 0);
```

---

## Database Selection Guide

| Type | Options | Best For |
|------|---------|----------|
| Relational | PostgreSQL, MySQL | OLTP, complex queries, ACID |
| Document | MongoDB, CouchDB | Flexible schema, catalogs |
| Key-Value | Redis, DynamoDB | Sessions, caching, leaderboards |
| Column-Family | Cassandra | Write-heavy, time-series |
| Graph | Neo4j, Neptune | Social networks, recommendations |
| Distributed SQL | CockroachDB, TiDB | Global apps needing ACID + scale |

---

## Connection Management

- **Pool size:** CPU cores × 2 + effective spindle count
- **Connection lifetime:** Rotate to prevent resource leaks
- **Read replicas:** Route reads to replicas, writes to primary
- **Consistent reads:** Route to primary when needed (e.g., after insert)

---

## Design Checklist

- [ ] Normalization appropriate for workload (normalize first, denormalize with evidence)
- [ ] Indexes cover common query patterns
- [ ] No redundant or overlapping indexes
- [ ] Foreign keys defined for all relationships
- [ ] Migration strategy supports zero-downtime
- [ ] Partitioning considered for tables >10M rows
- [ ] Connection pooling configured
