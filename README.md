# Arduino Environmental Monitor + SCADA-Style Data Logging & Data-Quality Filtering

A breadboard prototype that mimics a PLC/SCADA workflow: 
sensors → controller logic → serial telemetry → historian logging → analysis/trending.

This project reads temperature & humidity (DHT11) and distance/proximity (HC-SR04) using an Arduino UNO, displays live values on a 16×2 parallel LCD, triggers a buzzer alarm when thresholds are exceeded, streams data over USB serial, logs to CSV using Python, and generates plots where temperature values are invalidated whenever the proximity alarm condition is active.

---

## Features

### Arduino (Edge/PLC Layer)
- Reads DHT11*temperature/humidity
- Reads HC-SR04 distance
- Displays live values on 16×2 LCD (parallel, 4-bit mode)
- Drives a passive buzzer (via 2N2222A transistor) with alarm patterns:
  - Temperature out of range
  - Object too close
- Outputs a CSV serial frame every sample for logging:
  - 'millis,tempC,humPct,distCm'

### Python (SCADA/Historian + Analytics Layer)
- Reads USB serial data (COM port) and logs continuously to CSV
- Analysis script:
  - Flags too-close events from distance data
  - Invalidates temperature readings during those periods (data-quality rule)
  - Plots raw vs valid temperature + moving average
  - Optionally exports a cleaned CSV for Excel/Power BI

---

## System Architecture (SCADA Mapping)

Field Sensors → Controller → Comms → Historian → Analytics
- DHT11 + HC-SR04 → Arduino UNO → USB Serial → Python Logger (CSV) → Python Analysis/Plots

---

## Hardware

- Arduino UNO R3
- DHT11 temperature/humidity module
- HC-SR04 ultrasonic distance sensor
- 16×2 LCD (1602A parallel)
- 10k potentiometer (LCD contrast)
- Passive buzzer
- 2N2222A transistor (buzzer driver)
- Resistors:
  - 1kΩ (2N2222A base resistor)
  - 10kΩ (base pulldown)
  - 220Ω (LCD backlight, recommended if no onboard resistor)
- Breadboard + jumper wires
- USB cable

![Wiring](/Codes/WiringDiagramorSchematic.png)
---

## Python Setup

Install dependencies:
```bash
pip install pyserial pandas matplotlib
```
## Python: Data Logger

- Logs continuously to: sensor_log.csv
- Make sure Arduino Serial Monitor is closed.

```bash
python logger_dht_ultra.py
```
## Python: Data Quality Filtering + Plotting

This script invalidates temperature whenever distance is too close (proximity alarm condition):
- If dist_cm <= DIST_CLOSE_CM, then temp_valid = NaN

```bash
python plot_invalidated_temp.py
```

## Outputs:

Trend plot: raw temperature vs valid-only temperature + moving average

Optional cleaned export: sensor_log_cleaned.csv

![Graph](/Codes/Graph.png)
