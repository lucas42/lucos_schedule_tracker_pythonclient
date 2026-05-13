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
	sys.exit("\033[91mSCHEDULE_TRACKER_ENDPOINT environment variable not set - needs to be the URL of a running lucos_schedule_tracker instance\033[0m")

# Derive the v2 endpoint base from the configured endpoint URL.
# The env var conventionally points at the v1 path (/report-status);
# strip that suffix if present so both old and new configs work.
# e.g. https://host/report-status -> https://host/v2/report-status
_base_url = SCHEDULE_TRACKER_ENDPOINT.rstrip('/')
if _base_url.endswith('/report-status'):
	_base_url = _base_url[:-len('/report-status')]
_V2_ENDPOINT = _base_url + '/v2/report-status'

session = requests.Session()
session.headers.update({
	"User-Agent": SYSTEM,
	"Content-Type": "application/json",
})

def updateScheduleTracker(success: bool, system: str = SYSTEM, job_name: str = "", message: Optional[str] = None, frequency: int = (24 * 60 * 60)):
	"""Report the outcome of a scheduled run to lucos_schedule_tracker.

	Posts to the v2 /report-status endpoint.

	Args:
		success: Whether the job completed successfully.
		system: Identifier of the owning system (e.g. "lucos_arachne"). Defaults
			to the SYSTEM env var.
		job_name: Sub-job identifier within the system (e.g.
			"ingestor_dbpedia_meanOfTransportation"). Defaults to an empty string.
			See ADR-0004 for the architectural background:
			https://github.com/lucas42/lucos/blob/main/docs/adr/0004-scheduled-jobs-monitoring-architecture.md
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
		schedule_tracker_response = requests.post(_V2_ENDPOINT, json=payload, timeout=30)
		schedule_tracker_response.raise_for_status()
	except Exception as error:
		print("\033[91m [{}] ** Error calling schedule-tracker: {}\033[0m".format(datetime.now().isoformat(), error), flush=True)
