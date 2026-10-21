import json
import os
import secrets
from http.cookies import SimpleCookie
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

import crud_usuarios_usss102024

os.chdir(os.path.dirname(os.path.abspath(__file__)))

port = 3000
crudUsuarios = crud_usuarios_usss102024.crud_usuarios_usss102024()
sesiones = {}  # token de sesion -> usuario
VISTAS = ("usuarios", "busqueda_usuarios")


class miServidor(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def token_sesion(self):
        cookie = SimpleCookie(self.headers.get("Cookie", ""))
        return cookie["sid"].value if "sid" in cookie else None

    def hay_sesion(self):
        return self.token_sesion() in sesiones

    def responder(self, datos, codigo=200, cabeceras=None):
        cuerpo = json.dumps(datos).encode("utf-8")
        self.send_response(codigo)
        self.send_header("Content-type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(cuerpo)))
        for clave, valor in (cabeceras or {}).items():
            self.send_header(clave, valor)
        self.end_headers()
        self.wfile.write(cuerpo)

    def do_POST(self):
        try:
            longitud = int(self.headers.get("Content-Length", 0))
            datos = json.loads(self.rfile.read(longitud).decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            return self.responder({"msg": "Solicitud invalida"}, 400)

        modulo = datos.get("modulo")
        if modulo == "login":
            usuario = crudUsuarios.login(datos)
            if usuario is None:
                return self.responder({"msg": "Usuario o clave incorrectos. Acceso denegado"})
            token = secrets.token_hex(16)
            sesiones[token] = usuario["usuario"]
            return self.responder(
                {"msg": "ok"},
                cabeceras={"Set-Cookie": f"sid={token}; Path=/; HttpOnly; SameSite=Strict"}
            )
        if modulo == "logout":
            sesiones.pop(self.token_sesion(), None)
            return self.responder({"msg": "ok"}, cabeceras={"Set-Cookie": "sid=; Path=/; Max-Age=0"})

        if not self.hay_sesion():
            return self.responder({"msg": "Acceso denegado"}, 401)
        if modulo == "usuario":
            return self.responder({"msg": crudUsuarios.administrar(datos)})
        self.responder({"msg": "Modulo desconocido"}, 400)

    def do_GET(self):
        ruta = urlparse(self.path)
        qs = parse_qs(ruta.query)

        # El login es lo primero que se muestra; sin sesion no se llega al sistema
        if ruta.path in ("/", "/index.html", "/login.html"):
            self.path = "/index.html" if self.hay_sesion() else "/login.html"
            return SimpleHTTPRequestHandler.do_GET(self)

        if not self.hay_sesion():
            return self.responder({"msg": "Acceso denegado"}, 401)

        if ruta.path == "/usuarios":
            buscar = qs.get("buscar", [""])[0]
            return self.responder(crudUsuarios.consultar(buscar))

        if ruta.path == "/vistas":
            form = qs.get("form", [""])[0]
            if form in VISTAS:
                self.path = f"/modulos/{form}.html"
                return SimpleHTTPRequestHandler.do_GET(self)

        self.send_error(404)


print(f"Servidor corriendo en http://localhost:{port}")
server = HTTPServer(("localhost", port), miServidor)
server.serve_forever()
