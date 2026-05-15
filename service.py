import time
import datetime
from astral import LocationInfo
from astral.sun import sun
import screen_brightness_control as sbc
import logging
from logging.handlers import RotatingFileHandler

log_handler = RotatingFileHandler('service.log', maxBytes=1024, backupCount=1)
logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[log_handler]
)

# Configuration — fill with your location
LATITUDE = 52.3702    # e.g. Amsterdam latitude
LONGITUDE = 4.8952    # Amsterdam longitude
TIMEZONE = 'Europe/Amsterdam'

# Brightness settings (0‑100)
BRIGHTNESS_MIN = 0     # at night
BRIGHTNESS_MAX = 75    # during day

# Optionally you can apply an “offset” so brightness ramps earlier/later
SUNRISE_OFFSET = datetime.timedelta(minutes=0)
SUNSET_OFFSET = datetime.timedelta(minutes=0)

# Interval in seconds to set brightness
INTERVAL = 300

def get_sun_times(date):
    """Return sunrise and sunset (timezone-aware) for given date."""
    location = LocationInfo(latitude=LATITUDE, longitude=LONGITUDE, timezone=TIMEZONE)
    s = sun(location.observer, date=date, tzinfo=location.timezone)
    # s is a dict with keys: sunrise, sunset, dawn, dusk, etc.
    return s['sunrise'], s['sunset']

def compute_brightness(now, sunrise, sunset):
    """
    Brightness goes:
    - 0 before sunrise
    - # 0 → 100 between sunrise and sunrise + 4h
    - 0 → 100 between sunrise and 10:30
    - 100 between sunrise + 4h and sunset - 4h
    - 100 → 0 between sunset - 4h and sunset
    - 0 after sunset
    """
    ramp_up_start = sunrise
    # ramp_up_end = sunrise + datetime.timedelta(hours=4)
    ramp_up_end = sunrise.replace(hour=9, minute=30)
    ramp_down_start = sunset - datetime.timedelta(hours=4)
    ramp_down_end = sunset

    if now < ramp_up_start or now > ramp_down_end:
        return 0  # Night time
    elif ramp_up_start <= now < ramp_up_end:
        # Ramp up from 0 to 100
        total = (ramp_up_end - ramp_up_start).total_seconds()
        elapsed = (now - ramp_up_start).total_seconds()
        frac = elapsed / total
        brightness = frac * BRIGHTNESS_MAX
    elif ramp_up_end <= now < ramp_down_start:
        # Daytime: full brightness
        brightness = BRIGHTNESS_MAX
    elif ramp_down_start <= now <= ramp_down_end:
        # Ramp down from 100 to 0
        total = (ramp_down_end - ramp_down_start).total_seconds()
        elapsed = (now - ramp_down_start).total_seconds()
        frac = elapsed / total
        brightness = BRIGHTNESS_MAX * (1 - frac)
    else:
        brightness = 0  # Just in case

    return int(brightness)


def set_brightness_for_all(monitors, value):
    """Set value for all monitors in the list."""
    try:
        sbc.set_brightness(value)
    except Exception as e:
        print("Failed to set brightness:", e)

def main_loop():
    """
    Main loop: recalc sunrise/sunset daily, then every interval,
    compute brightness and set it.
    """
    last_date = None
    monitors = sbc.list_monitors()
    print("Detected monitors:", monitors)

    while True:
        now = datetime.datetime.now(datetime.timezone.utc).astimezone()
        today = now.date()
        if today != last_date:
            # recalc new sunrise/sunset
            sunrise, sunset = get_sun_times(today)
            print(f"Sunrise: {sunrise}, Sunset: {sunset}")
            last_date = today

        # Compute brightness
        b = compute_brightness(now, sunrise, sunset)
        print(f"{now.strftime('%Y-%m-%d %H:%M:%S')} → brightness = {b}")
        
        # Apply brightness
        set_brightness_for_all(monitors, b)

        # Sleep until next poll
        time.sleep(INTERVAL)

if __name__ == '__main__':
    main_loop()
