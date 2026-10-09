# Lucky Draw System

A single-page HTML lucky draw app with animated prize reveals, a rolling name picker, and a winners list that auto-syncs to an Excel file.

## Files

- `LuckyDraw.html` — the app (open this in a browser)
- `Games.html` — a separate slideshow page for game-round pictures, to alternate with the lucky draw
- `server.py` — local server that serves the app and saves the winners Excel file
- `participant_names.txt` — list of participants, one name per line
- `images/` — prize photos referenced by the app
- `game_images/` — put your game slide pictures here
- `game_slides.txt` — list of game slide filenames (from `game_images/`), one per line, in the order they should be shown
- `lib/xlsx.full.min.js` — offline copy of the SheetJS library, used to build the winners `.xlsx` file

## Setup

1. Edit `participant_names.txt` and put one participant name per line. Blank lines are ignored.
2. (Optional) Edit the prize lists inside `LuckyDraw.html` (`lowPrizeNames`, `mediumPrizeNames`, `highPrizeNames`, and the `prizeImages` map) if you want to change prizes or images.
3. (Optional) Change `WINNERS_FILE_PATH` in `server.py` if you want the winners Excel file saved somewhere other than `C:\Users\queenach\OneDrive - Intel Corporation\Documents\AtomGPTWLuckyDraw\lucky_draw_winners.xlsx`.
4. Because the page loads `participant_names.txt` via `fetch()` and saves winners through a server endpoint, it must be run through `server.py`, not opened directly as a `file://` path and not `python -m http.server` (that doesn't support saving). Start it from this folder:

   ```powershell
   python server.py
   ```

5. Open the app in your browser at:

   ```
   http://localhost:8000/LuckyDraw.html
   ```

## How to run a draw

1. Wait for the button to change from "LOADING PARTICIPANTS..." to **🎁 SHOW PRIZE**.
2. Click **🎁 SHOW PRIZE** to reveal the next prize in the queue.
3. Click **🎰 START DRAW!** to start the rolling animation and pick winner(s).
4. Watch the names roll, then the winner(s) are announced automatically with confetti.
5. The draw confirms automatically after a short delay — winners are removed from the remaining participant pool, added to the Winners List panel(s), and the winners Excel file is updated automatically (see below).
6. Click **🎁 SHOW NEXT PRIZE** to continue to the next prize, and repeat.

## Winners Excel sync

- Every time winners are confirmed, winners are cleared, or everything is reset, the app sends the full winners list to `server.py`, which writes it to the fixed path set by `WINNERS_FILE_PATH` (default `C:\Users\queenach\OneDrive - Intel Corporation\Documents\AtomGPTWLuckyDraw\lucky_draw_winners.xlsx`), overwriting the previous contents.
- No file picker or extra clicks are needed — this happens silently in the background. The small status line under the draw button shows `✅ Synced ...` or `⚠️ Sync failed ...`.
- This path is inside your OneDrive-synced folder, so the file uploads automatically and can be shared from there.
- `server.py` must stay running for the sync to work; if you see a sync failure, make sure the terminal running `python server.py` is still open.

## Other controls

- **Export Winners** — downloads a text file summary of all winners by round.
- **Clear Winners** — clears the on-screen winners list display (removed participants stay removed).
- **Reset All** — resets participants, winners, and prize progress back to the start (cannot be undone).

## Notes

- The stats bar at the top shows total participants, remaining participants, prizes drawn, and round count.
- High-tier prizes hide the side winners panels during the draw for a bigger reveal.
- If you see "Unable to load participant_names.txt", make sure you're accessing the page through `http://localhost:...` (via `python server.py`) and not double-clicking the HTML file.

## Alternating with game rounds (Games.html)

1. Put your game slide pictures in `game_images/` and list their filenames in order in `game_slides.txt` (one per line). Each game round can have as many slides as you like (e.g. 2 slides per round) — they're just shown one after another.
2. Click the **🎮 Game Slides** link in the Lucky Draw header to open `Games.html`, or go to `http://localhost:8000/Games.html` directly.
3. Use **◀ Previous** / **Next ▶** (or the left/right arrow keys) to step through slides, and **⬅ Back to Lucky Draw** to return.
4. During the event, keep both `LuckyDraw.html` and `Games.html` open in separate browser tabs and switch between them (e.g. `Ctrl+Tab`) to go back and forth between a lucky draw round and a game round.

