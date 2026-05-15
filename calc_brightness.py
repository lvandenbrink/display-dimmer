import matplotlib.pyplot as plt
from astral import LocationInfo
from astral.sun import sun
import numpy as np
import datetime

# Configuration
LATITUDE = 52.3702    # e.g. Amsterdam latitude
LONGITUDE = 4.8952    # Amsterdam longitude
TIMEZONE = 'Europe/Amsterdam'
brightness_min = 0
brightness_max = 100

# Brightness settings (0‑100)
BRIGHTNESS_MIN = 0     # at night
BRIGHTNESS_MAX = 100   # during day

# Optionally you can apply an “offset” so brightness ramps earlier/later
SUNRISE_OFFSET = datetime.timedelta(minutes=0)
SUNSET_OFFSET = datetime.timedelta(minutes=0)

def compute_brightness(now, sunrise, sunset):
    """
    Brightness goes:
    - 0 before sunrise
    - 0 → 100 between sunrise and sunrise + 4h
    - 100 between sunrise + 4h and sunset - 4h
    - 100 → 0 between sunset - 4h and sunset
    - 0 after sunset
    """
    ramp_up_start = sunrise
    # ramp_up_end = sunrise + datetime.timedelta(hours=4)
    ramp_up_end = sunrise.replace(hour=10, minute=30)
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
    
def get_sun_times(date):
    """Return sunrise and sunset (timezone-aware) for given date."""
    location = LocationInfo(latitude=LATITUDE, longitude=LONGITUDE, timezone=TIMEZONE)
    s = sun(location.observer, date=date, tzinfo=location.timezone)
    # s is a dict with keys: sunrise, sunset, dawn, dusk, etc.
    return s['sunrise'], s['sunset']

now = datetime.datetime.now(datetime.timezone.utc).astimezone()
today = now.date()
sunrise, sunset = get_sun_times(today)

sunrise_time = sunrise.strptime("07:30", "%H:%M")
sunset_time = sunset.strptime("19:30", "%H:%M")


def brightness_at(hour, minute):
    time = now.replace(hour=hour, minute=minute)
    b = compute_brightness(time, sunrise, sunset)
    print(f"time: {hour}:{minute} + now: {now} = {time} == {b}")
    return b

# Generate time values from 00:00 to 23:30 in 30-minute steps
times, brightness_values = zip(*[
    (datetime.datetime.combine(today, datetime.time(hour, minute*5)), brightness_at(hour, minute*5))
    for hour in range(24)
    for minute in range(12)
])

# Plotting
time_labels = [t.strftime("%H:%M") for t in times]

# Reduce number of x-ticks — show every Nth label
N = 6  # Change to 2, 6, etc. to control spacing
reduced_xticks = time_labels[::N]

plt.figure(figsize=(12, 6))
plt.plot(time_labels, brightness_values, label="Brightness", color="orange")
plt.xticks(ticks=range(0, len(time_labels), N), labels=reduced_xticks, rotation=45)
plt.xlabel("Time of Day")
plt.ylabel("Brightness (%)")
plt.title("Brightness vs Time of Day (Sunrise 07:30, Sunset 19:30)")
plt.grid(True)
plt.tight_layout()
plt.show()
