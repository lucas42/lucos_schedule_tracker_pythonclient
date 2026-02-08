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
*   **`frequency`** (*int*, optional): How often the job is expected to run, in seconds. Defaults to `86400` (24 hours).
