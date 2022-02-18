import psycopg2.pool


class DatabasePool():
    def __init__(self, DB_URI):
        self.DB_URI = DB_URI
        try:
            self.DB_POOL = psycopg2.pool.SimpleConnectionPool(
                1, 5, self.DB_URI)
            connection = self.DB_POOL.getconn()
            try:
                cursor = connection.cursor()
                cursor.execute(
                    'CREATE TABLE IF NOT EXISTS command (id SERIAL PRIMARY KEY, guild_id BIGINT, command VARCHAR, res TEXT)')
                cursor.execute(
                    'CREATE INDEX IF NOT EXISTS index_command ON command (guild_id, command)')
            except Exception as e:
                print(e)
            finally:
                cursor.close()
                connection.commit()
                self.DB_POOL.putconn(connection)
        except Exception as e:
            print(e)
            print('Failed to connect to database')
            return

    def getconn(self):
        return self.DB_POOL.getconn()

    def putconn(self, connection):
        self.DB_POOL.putconn(connection)
