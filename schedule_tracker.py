import os, sys, requests
from datetime import datetime
from typing import Optional

try:
	SYSTEM = os.environ["SYSTEM"]
except KeyError:
	sys.exit("\033[91mSYSTEM environment variable not set\033[0m")
try:
	SCHEDULE_TRACKER_ENDPOINT = os.environ["SCHEDULE_TRACKER_ENDPOINT"]
except KeyError:
	sys.exit("\033[91mSCHEDULE_TRACKER_ENDPOINT environment variable not set - must be the v2 endpoint URL of a running lucos_schedule_tracker instance (e.g. http://host/v2/report-status)\033[0m")

if "/v2/" not in SCHEDULE_TRACKER_ENDPOINT:
	sys.exit("\033[91mSCHEDULE_TRACKER_ENDPOINT must point at the v2 endpoint (e.g. http://host/v2/report-status) — got: {}\033[0m".format(SCHEDULE_TRACKER_ENDPOINT))

session = requests.Session()
session.headers.update({
	"User-Agent": SYSTEM,
	"Content-Type": "application/json",
})

def updateScheduleTracker(success: bool, job_name: str, system: str = SYSTEM, message: Optional[str] = None, frequency: int = (24 * 60 * 60)):
	"""Report the outcome of a scheduled run to lucos_schedule_tracker.

	Posts to the v2 /report-status endpoint.

	Args:
		success: Whether the job completed successfully.
		job_name: Sub-job identifier within the system (e.g.
			"ingestor_dbpedia_meanOfTransportation"). Required — naming the job
			explicitly makes it easier to add further jobs to the same system
			later without schema changes. See ADR-0004 for the architectural
			background:
			https://github.com/lucas42/lucos/blob/main/docs/adr/0004-scheduled-jobs-monitoring-architecture.md
		system: Identifier of the owning system (e.g. "lucos_arachne"). Defaults
			to the SYSTEM env var.
		message: Optional human-readable detail, typically used to describe a
			failure.
		frequency: How often this job is genuinely scheduled to run, in seconds.
			Defaults to 86400 (24 hours). Pass your cron's actual interval —
			schedule-tracker uses this to derive its alert threshold. Do not
			adjust this value to manipulate the threshold; if the resulting
			alert window is wrong for your job, raise it as a schedule-tracker
			issue rather than passing a misleading value here.
	"""
	payload = {
		"system": system,
		"job_name": job_name,
		"frequency": frequency,
		"status": "success" if success else "error",
		"message": message,
	}
	try:
		schedule_tracker_response = requests.post(SCHEDULE_TRACKER_ENDPOINT, json=payload, timeout=30)
		schedule_tracker_response.raise_for_status()
	except Exception as error:
		print("\033[91m [{}] ** Error calling schedule-tracker: {}\033[0m".format(datetime.now().isoformat(), error), flush=True)
