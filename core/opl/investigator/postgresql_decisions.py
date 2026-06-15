import datetime
import json
import logging
import os


def store(pg_host, pg_port, pg_database, table, decisions, **kwargs):
    import psycopg2

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

    connection = psycopg2.connect(**db_conf)
    cursor = connection.cursor()

    for decision in decisions:
        decision["job_name"] = job_name
        decision["build_url"] = build_url
        decision["uploaded"] = datetime.datetime.now(
            tz=datetime.timezone.utc
        ).isoformat()

        logging.info(
            f"Storing decision to PostgreSQL {pg_host}:{pg_port}/{pg_database} table={table} json={json.dumps(decision)}"
        )
        cursor.execute(
            f"INSERT INTO {table} (data) VALUES (%s)",
            [json.dumps(decision)],
        )

    connection.commit()
    cursor.close()
    connection.close()
