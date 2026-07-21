from sqlalchemy import inspect, text

from database import engine


COLUMN_MIGRATIONS = {
    "subscribers": [("tenant_id", "INTEGER")],
    "regulations": [("tenant_id", "INTEGER"), ("status", "VARCHAR(30)"), ("approved_at", "DATETIME"), ("approved_by", "INTEGER")],
    "alerts": [("tenant_id", "INTEGER"), ("delivery_key", "VARCHAR(255)")],
}


def migrate_schema() -> None:
    """Apply additive MVP migrations for existing local databases.

    Production deployments should run reviewed transactional migrations against Postgres.
    """
    inspector = inspect(engine)
    with engine.begin() as connection:
        for table_name, columns in COLUMN_MIGRATIONS.items():
            if not inspector.has_table(table_name):
                continue
            existing = {column["name"] for column in inspector.get_columns(table_name)}
            for column_name, column_type in columns:
                if column_name not in existing:
                    connection.execute(text(f'ALTER TABLE "{table_name}" ADD COLUMN "{column_name}" {column_type}'))
