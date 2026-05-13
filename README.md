# lucos_schedule_tracker_pythonclient

Python library for sending updates to [lucos_schedule_tracker](https://github.com/lucas42/lucos_schedule_tracker).

This library posts to the v2 `/report-status` endpoint. See [ADR-0004](https://github.com/lucas42/lucos/blob/main/docs/adr/0004-scheduled-jobs-monitoring-architecture.md) for the architectural background on `system` vs `job_name`.

## Configuration

The following environment variables must be set for the library to function:

*   **`SYSTEM`**: A unique identifier for the system being tracked. This is used as the `User-Agent` header and as the default `system` name in reports.
*   **`SCHEDULE_TRACKER_ENDPOINT`**: The URL of the `lucos_schedule_tracker` instance's report endpoint (e.g., `https://schedule-tracker.example.com/report-status`). The library derives the v2 endpoint URL from this value automatically.

## Usage

```python
from schedule_tracker import updateScheduleTracker

# Report a successful run
updateScheduleTracker(True, "ingestor_dbpedia")

# Report a failure with a message
updateScheduleTracker(False, "ingestor_loc", message="Database connection failed")
```

## API Reference

### `updateScheduleTracker(success: bool, job_name: str, system: str = SYSTEM, message: str | None = None, frequency: int = 86400)`

Sends a status update to the v2 schedule tracker endpoint.

*   **`success`** (*bool*, required): Whether the job completed successfully.
*   **`job_name`** (*str*, required): A sub-job identifier within the system (e.g. `"ingestor_dbpedia_meanOfTransportation"`). Naming the job explicitly makes it easier to add further jobs to the same system later without schema changes.
*   **`system`** (*str*, optional): The identifier for the owning system (e.g. `"lucos_arachne"`). Defaults to the value of the `SYSTEM` environment variable.
*   **`message`** (*str | None*, optional): A human-readable message, typically used to provide details on failure.
*   **`frequency`** (*int*, optional): How often the job is expected to run, in seconds. Defaults to `86400` (24 hours).
