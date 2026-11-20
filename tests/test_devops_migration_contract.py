from candidate import migration_sql


def test_production_index_is_non_blocking():
    # A plain CREATE INDEX takes a table-locking write lock for the
    # duration of the build -- fine on a toy table, a real outage risk on
    # a production one. CONCURRENTLY avoids it; the fast candidate never
    # considers this.
    sql = migration_sql().upper()
    assert "CREATE INDEX CONCURRENTLY" in sql
    assert sql.endswith(";")
