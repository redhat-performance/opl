import logging
import os
import tempfile

import opl.status_data


def load(pg_host, pg_port, pg_database, query, paths, **kwargs):
    try:
        import psycopg2
    except ImportError as exc:
        raise ImportError(
            "PostgreSQL support requires psycopg2-binary, which is not included in "
            "the core install. Run 'pip install psycopg2-binary', install core with "
            "the [postgresql] extra, or install the full opl package (includes extras)."
        ) from exc

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

    out = {}

    for path in paths:
        out[path] = []

    logging.info(
        f"Querying PostgreSQL on {pg_host}:{pg_port}/{pg_database} with query={query}"
    )

    connection = psycopg2.connect(**db_conf)
    cursor = connection.cursor()
    cursor.execute(query)

    for row in cursor:
        data = row[0]
        logging.debug(
            f"Loading data from row with id={data.get('id', None)} name={data.get('name', None)}"
        )
        tmpfile = tempfile.NamedTemporaryFile(delete=False).name
        sd = opl.status_data.StatusData(tmpfile, data=data)
        for path in paths:
            tmp = sd.get(path)
            if tmp is not None:
                out[path].append(tmp)

    cursor.close()
    connection.close()

    logging.debug(f"Loaded {out}")
    return out
