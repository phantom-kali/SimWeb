from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs
import json
from template_engine import TemplateEngine


class Application:
    def __init__(self, templates_dir="templates"):
        self.routes = {}
        self.template_engine = TemplateEngine(templates_dir)

    def route(self, path, methods=None):
        if methods is None:
            methods = ["GET"]

        def decorator(handler):
            self.routes[path] = {"handler": handler, "methods": methods}
            return handler

        return decorator

    def handle_request(self, request):
        path = request.path.split("?")[0]  # Remove query string for routing
        method = request.method

        if path in self.routes:
            route = self.routes[path]
            if method in route["methods"]:
                return route["handler"](request)
            else:
                return self.method_not_allowed()
        else:
            return self.not_found()

    def not_found(self):
        return Response("Not Found", status=404)

    def method_not_allowed(self):
        return Response("Method Not Allowed", status=405)

    def render_template(self, template_name, context=None):
        return self.template_engine.render(template_name, context)

    def run(self, host="localhost", port=8000):
        class RequestHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                self.handle_request()

            def do_POST(self):
                self.handle_request()

            def handle_request(self):
                request = Request(self)
                response = self.server.app.handle_request(request)
                self.send_response(response.status)
                for header, value in response.headers.items():
                    self.send_header(header, value)
                self.end_headers()
                self.wfile.write(response.body.encode())

        server = HTTPServer((host, port), RequestHandler)
        server.app = self
        print(f"Running on http://{host}:{port}")
        server.serve_forever()


class Request:
    def __init__(self, handler):
        self.path = handler.path
        self.method = handler.command  # Changed from 'cmd' to 'command'
        self.headers = handler.headers
        self.query_params = (
            parse_qs(handler.path.split("?")[1]) if "?" in handler.path else {}
        )
        self.body = self._get_body(handler)

    def _get_body(self, handler):
        content_length = int(handler.headers.get("Content-Length", 0))
        return handler.rfile.read(content_length) if content_length > 0 else b""

    def get_json(self):
        if self.headers.get("Content-Type") == "application/json":
            return json.loads(self.body)
        return None


class Response:
    def __init__(self, body, status=200, content_type="text/html"):
        self.body = body
        self.status = status
        self.headers = {"Content-Type": content_type}

    @classmethod
    def html(cls, content):
        return cls(content)

    @classmethod
    def json(cls, content):
        return cls(json.dumps(content), content_type="application/json")
