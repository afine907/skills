# Batch Data Migration Guide

## Why Batch?

Large data migrations (millions of rows) cannot run as single transactions:
- Lock contention blocks production traffic
- Transaction log fills up
- Replication lag increases
- Timeout risk

## Basic Batch Pattern

### PostgreSQL

```sql
-- Process in batches of 10,000
DO $$
DECLARE
  batch_size INT := 10000;
  rows_affected INT;
BEGIN
  LOOP
    UPDATE users
    SET status = 'active'
    WHERE status IS NULL
    AND id IN (
      SELECT id FROM users
      WHERE status IS NULL
      LIMIT batch_size
      FOR UPDATE SKIP LOCKED
    );

    GET DIAGNOSTICS rows_affected = ROW_COUNT;
    EXIT WHEN rows_affected = 0;

    RAISE NOTICE 'Updated % rows', rows_affected;
    PERFORM pg_sleep(0.1);  -- Brief pause to reduce load
    COMMIT;
  END LOOP;
END $$;
```

### Python (SQLAlchemy)

```python
async def batch_migrate(db, batch_size=10000, sleep_seconds=0.5):
    """Migrate data in batches with progress tracking."""
    total = await db.execute(select(func.count()).where(User.status.is_(None)))
    processed = 0

    while True:
        # Fetch a batch of IDs
        result = await db.execute(
            select(User.id)
            .where(User.status.is_(None))
            .limit(batch_size)
            .with_for_update(skip_locked=True)
        )
        ids = result.scalars().all()

        if not ids:
            break

        # Update the batch
        await db.execute(
            update(User)
            .where(User.id.in_(ids))
            .values(status='active')
        )
        await db.commit()

        processed += len(ids)
        logger.info(f"Progress: {processed}/{total} ({processed/total*100:.1f}%)")

        await asyncio.sleep(sleep_seconds)

    logger.info(f"Migration complete. Total: {processed}")
```

## Cursor-Based Batching

Better for large tables - avoids OFFSET performance degradation.

```python
async def cursor_batch_migrate(db, batch_size=10000):
    """Use cursor (ID-based) pagination for efficient batching."""
    last_id = 0

    while True:
        result = await db.execute(
            select(User.id, User.name)
            .where(User.id > last_id)
            .where(User.status.is_(None))
            .order_by(User.id)
            .limit(batch_size)
        )
        rows = result.all()

        if not rows:
            break

        # Process batch
        for row in rows:
            await db.execute(
                update(User)
                .where(User.id == row.id)
                .values(
                    status='active',
                    display_name=row.name.strip().title(),
                )
            )

        last_id = rows[-1].id
        await db.commit()
        logger.info(f"Processed up to ID {last_id}")
```

## Parallel Batch Processing

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

async def parallel_migrate(db, batch_size=10000, workers=4):
    """Process batches in parallel using multiple workers."""
    # Get ID ranges for each worker
    min_id = await db.scalar(select(func.min(User.id)))
    max_id = await db.scalar(select(func.max(User.id)))
    range_size = (max_id - min_id) // workers

    async def process_range(start_id, end_id):
        cursor = start_id
        while cursor < end_id:
            batch_ids = await db.execute(
                select(User.id)
                .where(User.id >= cursor)
                .where(User.id < cursor + batch_size)
                .where(User.status.is_(None))
            )
            ids = batch_ids.scalars().all()

            if ids:
                await db.execute(
                    update(User)
                    .where(User.id.in_(ids))
                    .values(status='active')
                )
                await db.commit()

            cursor += batch_size
            await asyncio.sleep(0.1)

    # Run workers in parallel
    tasks = [
        process_range(
            min_id + i * range_size,
            min_id + (i + 1) * range_size if i < workers - 1 else max_id + 1
        )
        for i in range(workers)
    ]
    await asyncio.gather(*tasks)
```

## Progress Tracking

```python
class MigrationProgress:
    def __init__(self, total: int):
        self.total = total
        self.processed = 0
        self.errors = 0
        self.start_time = time.time()

    def update(self, count: int, errors: int = 0):
        self.processed += count
        self.errors += errors

    @property
    def elapsed(self) -> float:
        return time.time() - self.start_time

    @property
    def rate(self) -> float:
        return self.processed / self.elapsed if self.elapsed > 0 else 0

    @property
    def eta(self) -> float:
        remaining = self.total - self.processed
        return remaining / self.rate if self.rate > 0 else 0

    def __str__(self):
        return (
            f"Progress: {self.processed}/{self.total} "
            f"({self.processed/self.total*100:.1f}%) | "
            f"Rate: {self.rate:.0f}/s | "
            f"ETA: {self.eta:.0f}s | "
            f"Errors: {self.errors}"
        )
```

## Error Handling

```python
async def safe_batch_migrate(db, batch_size=10000, max_retries=3):
    """Migrate with error handling and retry logic."""
    cursor = 0

    while True:
        try:
            rows = await fetch_batch(db, cursor, batch_size)
            if not rows:
                break

            await process_batch(db, rows)
            cursor = rows[-1].id

        except DeadlockDetected:
            logger.warning("Deadlock detected, retrying...")
            await asyncio.sleep(1)
            continue

        except Exception as e:
            logger.error(f"Error at cursor {cursor}: {e}")
            # Log failed batch for manual review
            await log_failed_batch(cursor, batch_size, e)
            # Skip and continue
            cursor += batch_size

async def log_failed_batch(cursor, batch_size, error):
    """Record failed batches for manual retry."""
    await db.execute(insert(FailedBatch).values(
        cursor_start=cursor,
        batch_size=batch_size,
        error=str(error),
        created_at=datetime.utcnow(),
    ))
```

## Dry Run Mode

```python
async def dry_run_migrate(db, batch_size=10000):
    """Preview what the migration would do without making changes."""
    stats = {
        'total_rows': 0,
        'affected_rows': 0,
        'sample_changes': [],
    }

    cursor = 0
    while True:
        rows = await fetch_batch(db, cursor, batch_size)
        if not rows:
            break

        for row in rows:
            stats['total_rows'] += 1
            if needs_migration(row):
                stats['affected_rows'] += 1
                if len(stats['sample_changes']) < 10:
                    stats['sample_changes'].append({
                        'id': row.id,
                        'old': row.status,
                        'new': 'active',
                    })

        cursor = rows[-1].id

    print(f"Total rows: {stats['total_rows']}")
    print(f"Would affect: {stats['affected_rows']}")
    print(f"Sample changes: {stats['sample_changes']}")
```

## Monitoring During Migration

```sql
-- PostgreSQL: Check lock contention
SELECT pid, relation, mode, granted
FROM pg_locks
WHERE relation IN (SELECT oid FROM pg_class WHERE relname = 'users');

-- Check replication lag
SELECT client_addr, replay_lag
FROM pg_stat_replication;

-- Check table size and bloat
SELECT pg_size_pretty(pg_total_relation_size('users'));
```

## Post-Migration

```sql
-- Update table statistics
ANALYZE users;

-- Reindex if needed
REINDEX TABLE CONCURRENTLY users;

-- Verify row counts
SELECT COUNT(*) FROM users WHERE status = 'active';
SELECT COUNT(*) FROM users WHERE status IS NULL;
```
