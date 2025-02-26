import mysql.connector

class OcasionDataBase:
    def __init__(self, user: str, password: str, host: str, database: str) -> None:
        self.connection = mysql.connector.connect(
            user=user,
            password=password,
            host=host,
            database=database
        )
        self.cursor = self.connection.cursor()

    def get_all_cars(self):
        query = """
        SELECT * FROM WHERE
        """
        self.cursor.execute(query)

        return self.cursor.fetchall()




    def close_connection(self):
        self.connection.close()