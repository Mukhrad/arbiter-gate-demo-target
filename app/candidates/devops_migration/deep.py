"""Thorough migration-SQL generator: CONCURRENTLY, so the index build does
not take a table-locking write lock on a production table."""


def migration_sql() -> str:
    return "CREATE INDEX CONCURRENTLY idx_decisions_bucket ON decisions(bucket);"
