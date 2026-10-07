"""Local server for LuckyDraw: serves static files and saves the winners
Excel file directly to a fixed path on disk (e.g. inside a OneDrive-synced
Documents folder) so no browser file picker is ever shown."""
import http.server
import os

WINNERS_FILE_PATH = r"C:\Users\queenach\OneDrive - Intel Corporation\Documents\AtomGPTWLuckyDraw\lucky_draw_winners.xlsx"
PORT = 8000


class Handler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path != "/save-winners":
            self.send_error(404)
            return

        length = int(self.headers.get("Content-Length", 0))
        data = self.rfile.read(length)

        os.makedirs(os.path.dirname(WINNERS_FILE_PATH), exist_ok=True)
        with open(WINNERS_FILE_PATH, "wb") as f:
            f.write(data)

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"status":"ok"}')

    def log_message(self, format, *args):
        pass  # keep terminal output quiet


if __name__ == "__main__":
    with http.server.ThreadingHTTPServer(("", PORT), Handler) as httpd:
        print(f"Serving LuckyDraw at http://localhost:{PORT}")
        print(f"Winners Excel file: {WINNERS_FILE_PATH}")
        httpd.serve_forever()
