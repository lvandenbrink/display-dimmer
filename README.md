# display-dimmer

Automatically adjusts monitor brightness based on local sunrise and sunset times.

Brightness ramps up from sunrise to mid-morning, holds at maximum during the day, then ramps down to zero at sunset.

## Configuration

Edit the constants at the top of `service.py`:

| Variable | Description |
|---|---|
| `LATITUDE` / `LONGITUDE` | Your location |
| `TIMEZONE` | Your timezone (e.g. `Europe/Amsterdam`) |
| `BRIGHTNESS_MIN` / `BRIGHTNESS_MAX` | Brightness range (0–100) |
| `INTERVAL` | Poll interval in seconds (default: 300) |

## Setup

```bash
python -m venv .venv
.venv/bin/pip install -r requirements.txt  # Linux
.venv\Scripts\pip install -r requirements.txt  # Windows
```

## Usage

```bash
# Run the service
python service.py                  # Linux
run-display-service.cmd            # Windows

# Set brightness manually
python set_brightness.py 50

# Visualise the brightness curve for today
python calc_brightness.py
```

Logs are written to `service.log` in the working directory.

## Auto-start on Windows

To run the service automatically at login, add a shortcut to `run-display-service.cmd` in your Windows Startup folder. Press `Win+R`, type `shell:startup`, and place a shortcut there. For a more robust setup that starts without requiring a user login, use Task Scheduler: create a new task, set the trigger to "At startup", and set the action to run `run-display-service.cmd` with the project directory as the "Start in" path.
