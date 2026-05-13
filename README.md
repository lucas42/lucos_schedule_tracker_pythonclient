# lucos_schedule_tracker_pythonclient

Python library for sending updates to [lucos_schedule_tracker](https://github.com/lucas42/lucos_schedule_tracker).

## Configuration

The following environment variables must be set for the library to function:

*   **`SYSTEM`**: A unique identifier for the system or job being tracked. This is used as the `User-Agent` header and as the default `system` name in reports.
*   **`SCHEDULE_TRACKER_ENDPOINT`**: The full URL of the `lucos_schedule_tracker` instance's v1 report endpoint (e.g., `https://schedule-tracker.example.com/report-status`). The v2 endpoint URL is derived automatically from this value.

## Usage

```python
from schedule_tracker import updateScheduleTracker

# Report a successful run (v1 endpoint)
updateScheduleTracker(success=True)

# Report a failure with a message (v1 endpoint)
updateScheduleTracker(success=False, message="Database connection failed")

# Report with a job_name — posts to the v2 endpoint so multiple sub-jobs
# within one system can be tracked separately (see ADR-0004)
updateScheduleTracker(success=True, job_name="ingestor_dbpedia")
updateScheduleTracker(success=False, job_name="ingestor_loc", message="Connection timeout")
```

## API Reference

### `updateScheduleTracker(success: bool, system: str = SYSTEM, job_name: str | None = None, message: str | None = None, frequency: int = 86400)`

Sends a status update to the schedule tracker.

*   **`success`** (*bool*, required): Whether the job completed successfully.
*   **`system`** (*str*, optional): The identifier for the owning system (e.g. `"lucos_arachne"`). Defaults to the value of the `SYSTEM` environment variable.
*   **`job_name`** (*str | None*, optional): A sub-job identifier within the system (e.g. `"ingestor_dbpedia_meanOfTransportation"`). When provided, the report is posted to the `/v2/report-status` endpoint, which supports tracking multiple distinct jobs per system. When omitted, the v1 `/report-status` endpoint is used (backwards compatible). See [ADR-0004](https://github.com/lucas42/lucos/blob/main/docs/adr/0004-scheduled-jobs-monitoring-architecture.md) for the architectural background.
*   **`message`** (*str | None*, optional): A human-readable message, typically used to provide details on failure.
*   **`frequency`** (*int*, optional): How often the job is expected to run, in seconds. Defaults to `86400` (24 hours).
