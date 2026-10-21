from mysql.connector.errors import Error
import conexion

db = conexion.Conexion()
TABLA = "usuarios_usss102024"


class crud_usuarios_usss102024:
    def consultar(self, buscar):
        # Nunca se devuelve la clave al navegador
        like = f"%{buscar}%"
        filas = db.consultar(
            f"""SELECT idUsuario, usuario, nombre, direccion, telefono
                FROM {TABLA}
                WHERE usuario LIKE %s OR nombre LIKE %s
                ORDER BY nombre""",
            (like, like)
        )
        return filas if filas is not None else []

    def login(self, datos):
        filas = db.consultar(
            f"SELECT idUsuario, usuario, nombre FROM {TABLA} WHERE usuario=%s AND clave=%s",
            (str(datos.get('usuario', '')), str(datos.get('clave', '')))
        )
        return filas[0] if filas else None

    def validar(self, datos, clave_obligatoria):
        limites = {'usuario': 35, 'clave': 35, 'nombre': 85, 'direccion': 100, 'telefono': 9}
        for campo, maximo in limites.items():
            valor = str(datos.get(campo, '')).strip()
            if campo == 'clave' and not clave_obligatoria and valor == '':
                continue
            if valor == '' and campo != 'direccion':
                return f"El campo {campo} es obligatorio"
            if len(valor) > maximo:
                return f"El campo {campo} no puede pasar de {maximo} caracteres"
        return None

    def usuario_repetido(self, usuario, idUsuario=0):
        filas = db.consultar(
            f"SELECT idUsuario FROM {TABLA} WHERE usuario=%s AND idUsuario<>%s",
            (usuario, idUsuario)
        )
        return bool(filas)

    def administrar(self, datos):
        try:
            accion = datos.get('accion')
            if accion in ('nuevo', 'modificar'):
                error = self.validar(datos, clave_obligatoria=(accion == 'nuevo'))
                if error:
                    return error
                usuario = datos['usuario'].strip()
                clave = datos.get('clave', '').strip()
                nombre = datos['nombre'].strip()
                direccion = datos.get('direccion', '').strip()
                telefono = datos['telefono'].strip()

            if accion == 'nuevo':
                if self.usuario_repetido(usuario):
                    return "Ese usuario ya existe"
                sql = f"""
                    INSERT INTO {TABLA}(usuario,clave,nombre,direccion,telefono)
                    VALUES(%s,%s,%s,%s,%s)
                """
                valores = (usuario, clave, nombre, direccion, telefono)
            elif accion == 'modificar':
                idUsuario = int(datos['idUsuario'])
                if self.usuario_repetido(usuario, idUsuario):
                    return "Ese usuario ya existe"
                if clave:
                    sql = f"""
                        UPDATE {TABLA} SET usuario=%s,clave=%s,nombre=%s,direccion=%s,telefono=%s
                        WHERE idUsuario=%s
                    """
                    valores = (usuario, clave, nombre, direccion, telefono, idUsuario)
                else:  # clave vacia = conservar la actual
                    sql = f"""
                        UPDATE {TABLA} SET usuario=%s,nombre=%s,direccion=%s,telefono=%s
                        WHERE idUsuario=%s
                    """
                    valores = (usuario, nombre, direccion, telefono, idUsuario)
            elif accion == 'eliminar':
                sql = f"DELETE FROM {TABLA} WHERE idUsuario=%s"
                valores = (int(datos['idUsuario']),)
            else:
                return "Accion no valida"
            return db.ejecutar(sql, valores)
        except (Error, KeyError, ValueError) as e:
            return f"Error al guardar el usuario: {e}"
