import os
import sys
import threading
import time
from datetime import datetime, timezone
from http.server import HTTPServer, SimpleHTTPRequestHandler

from colorama import Fore, Style
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from . import config as cfg
from .core.engine import build_site


class BuildHandler(FileSystemEventHandler):
    def __init__(self, build_func):
        self.build_func = build_func
        self.last_build = 0

    def on_modified(self, event):
        if event.is_directory or "build" in event.src_path:
            return

        now = time.time()
        if now - self.last_build < 1:
            return
        self.last_build = now

        if os.path.basename(event.src_path) in ["stapler.toml", "stapler.yaml", "stapler.yml"]:
            print(f"\n{Fore.YELLOW}Config changed! Restarting...{Style.RESET_ALL}\n")
            os.execv(sys.executable, [sys.executable] + sys.argv)

        rel_path = os.path.relpath(event.src_path)
        timestamp = datetime.now(timezone.utc).strftime("%H:%M:%S")
        print(
            f"\n{Fore.BLUE}[{timestamp}]{Style.RESET_ALL} "
            f"{Fore.YELLOW}File changed:{Style.RESET_ALL} {rel_path}\n"
        )
        self.build_func()


class StaplerHTTPServer(SimpleHTTPRequestHandler):
    directory = "build"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=self.directory, **kwargs)

    def log_message(self, format, *args):
        request_line = args[0]
        parts = request_line.split()

        if len(parts) >= 2:
            method = parts[0]
            path = parts[1]
        else:
            method = ""
            path = request_line

        method_colors = {
            "GET": Fore.CYAN,
            "POST": Fore.YELLOW,
            "PUT": Fore.MAGENTA,
            "DELETE": Fore.RED,
        }
        method_color = method_colors.get(method, Fore.WHITE)

        status = args[1] if len(args) > 1 else "000"
        if status.startswith("2"):
            status_color = Fore.GREEN
        elif status.startswith("3"):
            status_color = Fore.CYAN
        elif status.startswith("4"):
            status_color = Fore.YELLOW
        else:
            status_color = Fore.RED

        timestamp = datetime.now(timezone.utc).strftime("%H:%M:%S")
        print(
            f"{Fore.BLUE}[{timestamp}]{Style.RESET_ALL}  "
            f"{method_color}{Style.BRIGHT}{method}{Style.RESET_ALL}  "
            f"{Fore.WHITE}{path}{Style.RESET_ALL}  "
            f"{status_color}{status}{Style.RESET_ALL}"
        )

    def do_GET(self):
        path = self.translate_path(self.path)

        if self.path.endswith("/") or self.path == "":
            index_path = os.path.join(path, "index.html")
            if os.path.isfile(index_path):
                self.path = (
                    self.path.rstrip("/") + "/index.html"
                    if not self.path.endswith("index.html")
                    else self.path
                )
                return super().do_GET()

        if os.path.isfile(path):
            return super().do_GET()

        if not self.path.endswith("/") and "." not in os.path.basename(self.path):
            html_path = path + ".html"
            if os.path.isfile(html_path):
                self.path += ".html"
                return super().do_GET()

        not_found_path = os.path.join(self.directory, "404.html")
        if os.path.isfile(not_found_path):
            self.send_response(404)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            with open(not_found_path, "rb") as f:
                self.wfile.write(f.read())
            return

        self.send_error(404, "File not found")


def serve(config, port=8000):
    print(f"{Fore.BLUE}=== Development Server ==={Style.RESET_ALL}\n")

    build_site(config, is_dev=True)

    observer = Observer()
    handler = BuildHandler(lambda: build_site(config, is_dev=True))
    observer.schedule(handler, cfg.get_site_dir(config), recursive=True)
    observer.schedule(handler, ".", recursive=False)
    observer.start()

    build_dev_dir = cfg.get_build_dev_dir(config)

    class DevHTTPServer(StaplerHTTPServer):
        directory = build_dev_dir

    server = HTTPServer(("localhost", port), DevHTTPServer)
    threading.Thread(target=server.serve_forever, daemon=True).start()

    print(f"{Fore.GREEN}Server running at {Style.BRIGHT}http://localhost:{port}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}Serving from: {Style.BRIGHT}{build_dev_dir}/{Style.RESET_ALL}")
    print(
        f"{Fore.MAGENTA}Watching: {Style.BRIGHT}{cfg.get_site_dir(config)}/ "
        f"{Style.RESET_ALL}and config file"
    )
    print(f"\n{Fore.YELLOW}Press Ctrl+C to stop{Style.RESET_ALL}\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}Stopping server...{Style.RESET_ALL}")
        observer.stop()
        server.shutdown()
        observer.join()
