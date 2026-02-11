import pandas as pd
import matplotlib.pyplot as plt

CSV_FILE = "sensor_log.csv"   
DIST_CLOSE_CM = 20            # distance thershold for valid data

df = pd.read_csv(CSV_FILE)

df["timestamp"] = pd.to_datetime(df["timestamp"])

df["temp_c"] = pd.to_numeric(df["temp_c"], errors="coerce")
df["hum_pct"] = pd.to_numeric(df["hum_pct"], errors="coerce")
df["dist_cm"] = pd.to_numeric(df["dist_cm"], errors="coerce")

# Consider dist -1 (invalid echo) as NOT close (so we don't invalidate temp for that)
df.loc[df["dist_cm"] < 0, "dist_cm"] = pd.NA

# Alarm condition: too close
df["too_close"] = df["dist_cm"].notna() & (df["dist_cm"] <= DIST_CLOSE_CM)

# Invalidate temperature when too close
df["temp_valid"] = df["temp_c"].where(~df["too_close"], pd.NA)

# Optional: moving average on valid temps only
WINDOW = 10
df["temp_valid_ma"] = df["temp_valid"].rolling(WINDOW, min_periods=1).mean()

# ---- Plot ----
plt.figure()
plt.plot(df["timestamp"], df["temp_c"], alpha=0.3, label="Temp (raw)")
plt.plot(df["timestamp"], df["temp_valid"], linewidth=2, label="Temp (valid only)")
plt.plot(df["timestamp"], df["temp_valid_ma"], linewidth=2, label=f"Valid Temp MA({WINDOW})")

# Shade intervals where too_close is True
# We do this by shading each "too_close" point's time span to the next time point
ts = df["timestamp"].values
mask = df["too_close"].values

for i in range(len(df) - 1):
    if mask[i]:
        plt.axvspan(ts[i], ts[i+1], alpha=0.15)

plt.title(f"Temperature with invalidation when distance ≤ {DIST_CLOSE_CM} cm")
plt.xlabel("Time")
plt.ylabel("Temperature (°C)")
plt.grid(True)
plt.legend()
plt.show()

out = df[["timestamp", "temp_c", "temp_valid", "hum_pct", "dist_cm", "too_close"]]
out.to_csv("sensor_log_cleaned.csv", index=False)
print("Saved cleaned file: sensor_log_cleaned.csv")