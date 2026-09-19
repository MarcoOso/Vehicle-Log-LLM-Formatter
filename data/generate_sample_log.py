"""
generate_sample_log.py

Generates a synthetic vehicle telemetry log that mimics the shape of real
CAN-bus / OBD-II diagnostic exports: timestamped rows of engine RPM,
throttle position, coolant temperature, vehicle speed, and (occasionally)
a diagnostic trouble code (DTC).

This is synthetic data (no real vehicle or proprietary data used) — it exists
purely to demonstrate the data-cleaning and LLM-formatting pipeline in
clean_and_format.py.
"""

import csv
import random
from datetime import datetime, timedelta

random.seed(42)

FAULT_CODES = [
    "P0300",  # Random/multiple cylinder misfire
    "P0171",  # System too lean (Bank 1)
    "P0420",  # Catalyst efficiency below threshold
    "P0128",  # Coolant thermostat below regulating temp
]


def generate_rows(n=500, start_time=None):
    if start_time is None:
        start_time = datetime(2026, 9, 18, 8, 0, 0)

    rows = []
    rpm = 800.0        # idle
    speed = 0.0
    coolant_temp = 70.0  # deg F, cold start
    throttle = 0.0

    t = start_time
    for i in range(n):
        # Simulate a rough driving cycle: idle -> accelerate -> cruise -> decel -> idle
        phase = (i % 100)
        if phase < 10:
            throttle = max(0, throttle - random.uniform(0, 5))
        elif phase < 40:
            throttle = min(100, throttle + random.uniform(0, 8))
        elif phase < 70:
            throttle = throttle + random.uniform(-3, 3)
            throttle = max(10, min(60, throttle))
        else:
            throttle = max(0, throttle - random.uniform(0, 6))

        rpm = 800 + throttle * 45 + random.uniform(-100, 100)
        rpm = max(700, rpm)
        speed = speed * 0.9 + throttle * 0.5 + random.uniform(-2, 2)
        speed = max(0, min(85, speed))  # keep within plausible street-driving range
        coolant_temp = min(210, coolant_temp + random.uniform(0, 0.6)) if coolant_temp < 195 else coolant_temp + random.uniform(-0.5, 0.5)

        fault_code = ""
        # Inject a handful of fault events with some noisy sensor readings around them
        if i in (150, 151, 152, 300, 301, 450):
            fault_code = random.choice(FAULT_CODES)
            rpm += random.uniform(150, 400)  # misfire/lean condition often spikes or destabilizes RPM

        rows.append({
            "timestamp": t.isoformat(),
            "rpm": round(rpm, 1),
            "throttle_pct": round(throttle, 1),
            "coolant_temp_f": round(coolant_temp, 1),
            "vehicle_speed_mph": round(speed, 1),
            "dtc_code": fault_code,
        })
        t += timedelta(seconds=1)

    return rows


def inject_dirty_data(rows):
    """Introduce realistic real-world messiness: missing values, duplicate
    timestamps, out-of-range sensor glitches, and inconsistent casing —
    so the cleaning step in clean_and_format.py has real work to do."""
    dirty = [dict(r) for r in rows]

    # Missing values
    for idx in (20, 87, 210, 333):
        dirty[idx]["coolant_temp_f"] = ""

    # Sensor glitch / out-of-range spike (bad reading, not a real event)
    dirty[60]["rpm"] = 9999.9

    # Duplicate timestamp (common in logging systems with buffering issues)
    dirty[100]["timestamp"] = dirty[99]["timestamp"]

    # Inconsistent fault code casing / whitespace
    for idx in (150, 300):
        dirty[idx]["dtc_code"] = f" {dirty[idx]['dtc_code'].lower()} "

    return dirty


def main():
    rows = generate_rows(n=500)
    rows = inject_dirty_data(rows)

    out_path = "data/raw_vehicle_log.csv"
    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} rows to {out_path}")


if __name__ == "__main__":
    main()
