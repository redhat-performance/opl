import logging
import psycopg2.extras


def get_column(connection, column, include_null=False, table='items'):
    """
    Given connection to the PostgreSQL DB, return values from table items
    column column.
    """
    queryfrom = f"SELECT {column} FROM {table}"
    querycondition = f" WHERE {column} IS NOT NULL"
    sql = f"{queryfrom} {querycondition}" if not include_null else queryfrom
    logging.debug(f"Executing {sql}")
    cursor = connection.cursor()
    cursor.execute(sql)
    results = cursor.fetchall()
    return [i[0] for i in results]


def get_column_min_max(connection, column, table='items'):
    """
    Return min and max from the column
    """
    sql = f"SELECT MIN({column}), MAX({column}) FROM {table} WHERE {column} IS NOT NULL"
    logging.debug(f"Executing {sql}")
    cursor = connection.cursor()
    cursor.execute(sql)
    result = cursor.fetchone()
    return (result[0], result[1])


def get_timestamps(connection, column, table='items'):
    sql = f"SELECT EXTRACT (EPOCH FROM {column}) as {column} FROM {table} WHERE {column} IS NOT NULL"
    logging.debug(f"Executing {sql}")
    cursor = connection.cursor()
    cursor.execute(sql)
    results = cursor.fetchall()
    return [i[0] for i in results]


def get_timedelta_between_columns(connection, columns, table='items'):
    """
    Accepting 2 datetime columns in `items` table, produce the time difference
    in seconds (first - second).
    """
    if len(columns) != 2:
        raise Exception("This function requires exactly 2 column names as input.")
    else:
        queryfrom = f"SELECT EXTRACT (EPOCH FROM({columns[0]} - {columns[1]})) FROM {table}"
        querycondition = f" WHERE {columns[0]} IS NOT NULL AND {columns[1]} IS NOT NULL"
        sql = f"{queryfrom} {querycondition}"
        logging.debug(f"Executing {sql}")
        cursor = connection.cursor()
        cursor.execute(sql)
        return [i[0] for i in cursor.fetchall()]


def get_timedelta_between_timestamp_n_dbcolumn(start_time, connection, column, table='items'):
    timedelta = [(i - start_time).total_seconds() for i in get_column(connection, column, table=table)]
    return timedelta


class BatchProcessor():
    """
    Goal of this object is to have some versatile mechanism, that would allow
    me to add data to DB one by one, but that would actually insert that data
    to DB only when it accumulated some amount of it (1 DB insert with 100
    rows is far faster than 100 small inserts with 1 row).
    """
    def __init__(self, db, sql, batch=100, lock=None):
        self.db = db
        self.sql = sql
        self.batch = batch
        self.lock = lock
        self.data = []

    def commit(self):
        logging.debug(f"Executing '{self.sql}' with {len(self.data)} rows of data")
        cursor = self.db.cursor()

        if self.lock is not None:
            self.lock.acquire(True)

        psycopg2.extras.execute_values(
            cursor, self.sql, self.data, template=None, page_size=100)

        self.data.clear()

        if self.lock is not None:
            self.lock.release()

        self.db.commit()
        cursor.close()

    def add(self, row):
        self.data.append(row)
        if len(self.data) >= self.batch:
            self.commit()


def BatchReader(db, sql, limit=100):
    """
    Creates named server side cursor (so not all results are fetched to
    the client when query is executed):

        https://www.psycopg.org/docs/usage.html#server-side-cursors

    Use separate connection when creating this as commits in pther cursor
    in same connection will invalidate this and I probably do not understand
    withhold=True good enough to use it correctly.
    """
    cursor = db.cursor(name="OPLBatchReader")
    cursor.itersize = limit
    cursor.execute(sql)
    return cursor
