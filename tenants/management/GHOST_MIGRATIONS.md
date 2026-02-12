# Zero-Downtime "Ghost Migration" Strategy for 10k+ Tenants ⚡🏛️

When scaling to 10,000+ tenants with multi-terabyte databases, standard `migrate` commands become dangerous because they lock tables. 

## The Strategy: Copy-and-Swap (Ghost)

### 1. The Shadow Column Pattern
Instead of `ALTER TABLE ... RENAME`, we use:
- Add a NEW column (nullable).
- Dual-write to both OLD and NEW columns via application logic/triggers.
- Backfill the NEW column from OLD data in background batches.
- Switch reads to the NEW column.
- Drop the OLD column.

### 2. Schema Isolation Benefits
Because we use **Physical Isolation (Schemas)** for enterprise clients, we can migrate them sequentially instead of all at once:
- **Canary Tenants**: Migrate a small group of low-risk tenants first.
- **Batched Execution**: Orchestrate migrations in chunks of 100 schemas to prevent DB contention.

### 3. Ghost Tables (The pt-online-schema-change approach)
For massive table changes:
1. Create a `_new` table with the desired schema.
2. Create triggers to sync writes from `current` -> `_new`.
3. Copy data from `current` -> `_new` in small transaction chunks.
4. Rename `current` to `_old` and `_new` to `current` inside a single transaction.

## Implementation Tooling
I recommend integrating `django-pg-zero-downtime-migrations` for automated safety checks that prevent blocking SQL operations from being committed to the codebase. ⚡🏛️🚀
