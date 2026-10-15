"""Local server for LuckyDraw: serves static files and saves the winners
Excel file directly to a fixed path on disk (e.g. inside a OneDrive-synced
Documents folder) so no browser file picker is ever shown.

Also backs up the in-progress draw state (participants left, winners so
far, round/prize position) to a dedicated git branch after every round, so
that if this laptop hangs mid-event, a different laptop can run
`python server.py -restore` (after `git pull`/`git fetch`) to pick up the
draw exactly where it left off."""
import argparse
import http.server
import os
import subprocess
import threading

WINNERS_FILE_PATH = r"C:\Users\queenach\OneDrive - Intel Corporation\Documents\AtomGPTWLuckyDraw\lucky_draw_winners.xlsx"
PORT = 8000

REPO_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_FILE_NAME = "draw_state.json"
STATE_FILE_PATH = os.path.join(REPO_DIR, STATE_FILE_NAME)
STATE_BRANCH = "lucky-draw-state"


def run_git(args):
    return subprocess.run(["git", *args], cwd=REPO_DIR, capture_output=True, text=True)


def backup_state_to_git():
    """Push draw_state.json to STATE_BRANCH on the remote as a standalone
    snapshot commit, without touching the working tree or whatever branch
    is currently checked out locally."""
    try:
        blob = run_git(["hash-object", "-w", STATE_FILE_NAME])
        if blob.returncode != 0:
            print(f"[git-backup] hash-object failed: {blob.stderr.strip()}")
            return
        blob_sha = blob.stdout.strip()

        mktree = subprocess.run(
            ["git", "mktree"], cwd=REPO_DIR, capture_output=True, text=True,
            newline="", input=f"100644 blob {blob_sha}\t{STATE_FILE_NAME}\n",
        )
        if mktree.returncode != 0:
            print(f"[git-backup] mktree failed: {mktree.stderr.strip()}")
            return
        tree_sha = mktree.stdout.strip()

        commit = run_git(["commit-tree", tree_sha, "-m", "Lucky draw state backup"])
        if commit.returncode != 0:
            print(f"[git-backup] commit-tree failed: {commit.stderr.strip()}")
            return
        commit_sha = commit.stdout.strip()

        push = run_git(["push", "--force", "origin", f"{commit_sha}:refs/heads/{STATE_BRANCH}"])
        if push.returncode != 0:
            print(f"[git-backup] push failed (continuing without it): {push.stderr.strip()}")
        else:
            print(f"[git-backup] pushed draw state to '{STATE_BRANCH}' ({commit_sha[:8]})")
    except Exception as e:
        print(f"[git-backup] ERROR: {type(e).__name__}: {e}")


def restore_state_from_git():
    """Fetch the latest draw_state.json backed up on STATE_BRANCH and write
    it locally so the app picks it up on load, like resuming on a new
    laptop after `git pull`."""
    print(f"[restore] fetching '{STATE_BRANCH}' from origin...")
    fetch = run_git(["fetch", "origin", STATE_BRANCH])
    if fetch.returncode != 0:
        print(f"[restore] fetch failed (no saved state yet?): {fetch.stderr.strip()}")
        return

    show = run_git(["show", f"origin/{STATE_BRANCH}:{STATE_FILE_NAME}"])
    if show.returncode != 0:
        print(f"[restore] no {STATE_FILE_NAME} found on '{STATE_BRANCH}': {show.stderr.strip()}")
        return

    with open(STATE_FILE_PATH, "w", encoding="utf-8") as f:
        f.write(show.stdout)
    print(f"[restore] restored {STATE_FILE_NAME} from '{STATE_BRANCH}' — start the draw and it will resume")


class Handler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == "/save-winners":
            self._save_winners()
        elif self.path == "/save-state":
            self._save_state()
        else:
            print(f"[server] rejected unknown POST path: {self.path}")
            self.send_error(404)

    def _save_winners(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            data = self.rfile.read(length)

            os.makedirs(os.path.dirname(WINNERS_FILE_PATH), exist_ok=True)
            with open(WINNERS_FILE_PATH, "wb") as f:
                f.write(data)

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"status":"ok"}')
            print(f"[save-winners] saved {length} bytes OK")
        except PermissionError as e:
            print(f"[save-winners] PERMISSION ERROR (is the xlsx file open in Excel?): {e}")
            self.send_error(500, "File is locked or permission denied — close it in Excel and try again")
        except Exception as e:
            print(f"[save-winners] ERROR: {type(e).__name__}: {e}")
            self.send_error(500, str(e))

    def _save_state(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            data = self.rfile.read(length)

            with open(STATE_FILE_PATH, "wb") as f:
                f.write(data)

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"status":"ok"}')
            print(f"[save-state] saved {length} bytes, backing up to git in background...")
            threading.Thread(target=backup_state_to_git, daemon=True).start()
        except Exception as e:
            print(f"[save-state] ERROR: {type(e).__name__}: {e}")
            self.send_error(500, str(e))

    def log_message(self, format, *args):
        pass  # keep routine GET/static-file logs quiet; POST outcomes are printed explicitly above


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LuckyDraw local server")
    parser.add_argument(
        "-restore", "--restore", action="store_true", dest="restore",
        help="Before starting, restore draw_state.json from the 'lucky-draw-state' "
             "git branch (use this on a backup laptop after git pull/fetch).",
    )
    args = parser.parse_args()

    if args.restore:
        restore_state_from_git()

    with http.server.ThreadingHTTPServer(("", PORT), Handler) as httpd:
        print(f"Serving LuckyDraw at http://localhost:{PORT}")
        print(f"Winners Excel file: {WINNERS_FILE_PATH}")
        httpd.serve_forever()
