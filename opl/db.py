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
    cursor = connection.cursor()
    cursor.execute(sql)
    results = cursor.fetchall()
    return [i[0] for i in results]


def get_column_min_max(connection, column, table='items'):
    """
    Return min and max from the column
    """
    sql = f"SELECT MIN({column}), MAX({column}) FROM {table} WHERE {column} IS NOT NULL"
    cursor = connection.cursor()
    cursor.execute(sql)
    result = cursor.fetchone()
    return (result[0], result[1])


def get_timestamps(connection, column, table='items'):
    sql = f"SELECT EXTRACT (EPOCH FROM {column}) as {column} FROM {table} WHERE {column} IS NOT NULL"
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


class BatchReader():
    """
    Acts as iterator when reading batches of data from DB. Provided SQL
    needs to have limit and offset placeholders. When iterating through
    it, it returns cursor each time where you need to use `x.fetchall()`
    or so. Once we return less than batch items, we raise StopIteration
    on next iteration.
    """
    def __init__(self, db, sql, limit=100):
        self.db = db
        self.sql = sql
        self.limit = limit
        self.batch = 0
        self.out_of_msgs = False

    def __iter__(self):
        return self

    def __next__(self):
        if self.out_of_msgs:
            raise StopIteration

        cursor = self.db.cursor()
        offset = self.limit * self.batch
        data = (self.limit, offset)
        cursor.execute(self.sql, data)

        logging.debug(f"On batch {self.batch} returning {cursor.rowcount} of rows")
        if cursor.rowcount < self.limit:
            self.out_of_msgs = True
        self.batch += 1

        return cursor
