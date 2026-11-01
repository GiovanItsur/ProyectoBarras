import mysql.connector
from mysql.connector import Error
class Conexion:
    def conectar(self):
        try:
            conexion = mysql.connector.connect(
                host="tbdiuhg.mysql.database.azure.com",
                user="Admin",
                password="12345root#",
                database="punto_venta"
            )
            if conexion.is_connected():
                return conexion

        except Error as e:
            print(f"Error al conectar a MySQL en Azure: {e}")
            return None