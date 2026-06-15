import datetime
import json
import logging
import os
import re

_SQL_IDENTIFIER = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")


def _validate_sql_identifier(name, kind="identifier"):
    if not _SQL_IDENTIFIER.fullmatch(name):
        raise ValueError(f"Invalid PostgreSQL {kind}: {name!r}")


def store(pg_host, pg_port, pg_database, table, decisions, **kwargs):
    try:
        import psycopg2
    except ImportError as exc:
        raise ImportError(
            "PostgreSQL support requires psycopg2-binary, which is not included in "
            "the core install. Run 'pip install psycopg2-binary', install core with "
            "the [postgresql] extra, or install the full opl package (includes extras)."
        ) from exc

    _validate_sql_identifier(table, "table name")

    pg_user = kwargs.get("pg_user")
    pg_password_env_var = kwargs.get("pg_password_env_var")

    db_conf = {
        "host": pg_host,
        "port": pg_port,
        "database": pg_database,
    }
    if pg_user:
        db_conf["user"] = pg_user
    if pg_password_env_var:
        db_conf["password"] = os.environ.get(pg_password_env_var)

    job_name = os.environ.get("JOB_NAME", "")
    build_url = os.environ.get("BUILD_URL", "")

    try:
        connection = psycopg2.connect(**db_conf)
    except psycopg2.Error as exc:
        logging.warning(
            f"Failed to connect to PostgreSQL {pg_host}:{pg_port}/{pg_database}: {exc}"
        )
        return

    cursor = connection.cursor()

    try:
        for decision in decisions:
            decision["job_name"] = job_name
            decision["build_url"] = build_url
            decision["uploaded"] = datetime.datetime.now(
                tz=datetime.timezone.utc
            ).isoformat()

            logging.info(
                f"Storing decision to PostgreSQL {pg_host}:{pg_port}/{pg_database} table={table} json={json.dumps(decision)}"
            )
            try:
                cursor.execute("SAVEPOINT store_decision")
                cursor.execute(
                    f"INSERT INTO {table} (data) VALUES (%s)",
                    [json.dumps(decision)],
                )
                cursor.execute("RELEASE SAVEPOINT store_decision")
            except psycopg2.Error as exc:
                logging.warning(f"Failed to store decision to PostgreSQL: {exc}")
                cursor.execute("ROLLBACK TO SAVEPOINT store_decision")

        connection.commit()
    except psycopg2.Error as exc:
        logging.warning(f"Failed to commit decisions to PostgreSQL: {exc}")
    finally:
        cursor.close()
        connection.close()
