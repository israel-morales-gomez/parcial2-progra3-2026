import mysql.connector
from mysql.connector import Error


class Conexion:
    def __init__(self):
        # XAMPP: usuario root sin clave por defecto
        self.host = "localhost"
        self.port = 3306  # puerto de MySQL/MariaDB en XAMPP (cambiar si usa otro, ej. 3307)
        self.user = "root"
        self.password = ""
        self.database = "parcial-2"
        self.conexion = None
        self._conectar()

    def _conectar(self):
        print("Conectando a la base de datos...")
        try:
            self.conexion = mysql.connector.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
                charset="utf8mb4",
                autocommit=True
            )
            print("Conexion exitosa")
            return True
        except Error as e:
            self.conexion = None
            print(f"Error al conectar a la base de datos (¿esta MySQL encendido en XAMPP?): {e}")
            return False

    def _asegurar_conexion(self):
        # Si no hay conexion (XAMPP apagado al iniciar) o MariaDB la cerro, se reconecta
        if self.conexion is None:
            if not self._conectar():
                raise Error("Sin conexion a la base de datos")
        else:
            self.conexion.ping(reconnect=True, attempts=3, delay=1)

    def consultar(self, sql, datos=None):
        try:
            self._asegurar_conexion()
            cursor = self.conexion.cursor(dictionary=True)
            cursor.execute(sql, datos)
            filas = cursor.fetchall()
            cursor.close()
            return filas
        except Error as e:
            print(f"Error al consultar la base de datos: {e}")
            return None

    def ejecutar(self, sql, datos):
        try:
            self._asegurar_conexion()
            cursor = self.conexion.cursor()
            cursor.execute(sql, datos)
            cursor.close()
            return 'ok'
        except Error as e:
            print(f"Error al ejecutar la consulta: {e}")
            return f'Error: {e}'
