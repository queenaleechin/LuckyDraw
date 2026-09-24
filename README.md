# Lucky Draw System

A single-page HTML lucky draw app with animated prize reveals, a rolling name picker, and a winners list.

## Files

- `LuckyDraw.html` — the app (open this in a browser)
- `participant_names.txt` — list of participants, one name per line
- `images/` — prize photos referenced by the app

## Setup

1. Edit `participant_names.txt` and put one participant name per line. Blank lines are ignored.
2. (Optional) Edit the prize lists inside `LuckyDraw.html` (`lowPrizeNames`, `mediumPrizeNames`, `highPrizeNames`, and the `prizeImages` map) if you want to change prizes or images.
3. Because the page loads `participant_names.txt` via `fetch()`, it must be served over `http://`, not opened directly as a `file://` path (browsers block local file fetches). Start a local server from this folder:

   ```powershell
   python -m http.server 8000
   ```

4. Open the app in your browser at:

   ```
   http://localhost:8000/LuckyDraw.html
   ```

## How to run a draw

1. Wait for the button to change from "LOADING PARTICIPANTS..." to **🎁 SHOW PRIZE**.
2. Click **🎁 SHOW PRIZE** to reveal the next prize in the queue.
3. Click **🎰 START DRAW!** to start the rolling animation and pick winner(s).
4. Watch the names roll, then the winner(s) are announced automatically with confetti.
5. The draw confirms automatically after a short delay — winners are removed from the remaining participant pool and added to the Winners List panel(s).
6. Click **🎁 SHOW NEXT PRIZE** to continue to the next prize, and repeat.

## Other controls

- **Export Winners** — downloads a text file summary of all winners by round.
- **Clear Winners** — clears the on-screen winners list display (removed participants stay removed).
- **Reset All** — resets participants, winners, and prize progress back to the start (cannot be undone).

## Notes

- The stats bar at the top shows total participants, remaining participants, prizes drawn, and round count.
- High-tier prizes hide the side winners panels during the draw for a bigger reveal.
- If you see "Unable to load participant_names.txt", make sure you're accessing the page through `http://localhost:...` and not double-clicking the HTML file.
