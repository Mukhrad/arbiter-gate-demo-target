"""Fast migration-SQL generator: a plain CREATE INDEX statement."""


def migration_sql() -> str:
    return "CREATE INDEX idx_decisions_bucket ON decisions(bucket);"
