# lucos_schedule_tracker_pythonclient

Python library for sending updates to [lucos_schedule_tracker](https://github.com/lucas42/lucos_schedule_tracker).

## Configuration

The following environment variables must be set for the library to function:

*   **`SYSTEM`**: A unique identifier for the system or job being tracked. This is used as the `User-Agent` header and as the default `system` name in reports.
*   **`SCHEDULE_TRACKER_ENDPOINT`**: The full URL of the `lucos_schedule_tracker` instance's report endpoint (e.g., `https://schedule-tracker.example.com/report-status`).

## Usage

```python
from schedule_tracker import updateScheduleTracker

# Report a successful run
updateScheduleTracker(success=True)

# Report a failure with a message
updateScheduleTracker(success=False, message="Database connection failed")
```

## API Reference

### `updateScheduleTracker(success: bool, system: str = SYSTEM, message: str = None, frequency: int = 86400)`

Sends a status update to the schedule tracker.

*   **`success`** (*bool*, required): Whether the job completed successfully.
*   **`system`** (*str*, optional): The identifier for the system. Defaults to the value of the `SYSTEM` environment variable.
*   **`message`** (*str*, optional): A human-readable message, typically used to provide details on failure.
*   **`frequency`** (*int*, optional): How often the job is expected to run, in seconds. Defaults to `86400` (24 hours). See [How `frequency` becomes an alert threshold](#how-frequency-becomes-an-alert-threshold) below for how this value is interpreted server-side.

## How `frequency` becomes an alert threshold

Picking the right value of `frequency` requires knowing how `lucos_schedule_tracker` uses it. The server **multiplies the most recent `frequency` it received by 3** to derive the alert threshold:

```
alert_threshold_seconds = frequency * 3
```

So a job that calls `updateScheduleTracker` once a day with the default `frequency=86400` will alert after 3 days of silence — i.e. after roughly 3 missed runs.

This means you must pick `frequency` based on the **alert latency you want**, not literally the cron cadence. Examples:

| Cron schedule | Want alert after… | Pass `frequency=` | Resulting threshold |
|---|---|---|---|
| Every 10 min | 30 min of silence | `600` | 30 min |
| Hourly | 3 missed runs | `3600` | 3 hours |
| Daily | 3 missed runs (default) | `86400` (default) | 3 days |
| Weekly | 1 missed run + 2 days slack | `259200` (3 days) | 9 days |
| Monthly | 1 missed run + ~6 days slack | `1036800` (12 days) | 36 days |

**For a weekly cron, the natural-looking value `frequency=604800` (7 days) gives a 21-day threshold** — almost certainly too lax to be useful. If you want an alert within a few days of a missed weekly run, pass `frequency=259200` (3 days), which gives a 9-day threshold.

It's worth a comment in the calling code explaining the chosen value, since the × 3 multiplier is non-obvious from the call site.
