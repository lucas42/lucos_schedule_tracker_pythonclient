import os, sys, requests
from datetime import datetime

try:
	SYSTEM = os.environ["SYSTEM"]
except KeyError:
	sys.exit("\033[91mSYSTEM environment variable not set\033[0m")
try:
	SCHEDULE_TRACKER_ENDPOINT = os.environ["SCHEDULE_TRACKER_ENDPOINT"]
except KeyError:
	sys.exit("\033[91mSCHEDULE_TRACKER_ENDPOINT environment variable not set - needs to be the URL of a running lucos_schedule_tracker instance\033[0m")

session = requests.Session()
session.headers.update({
	"User-Agent": SYSTEM,
	"Content-Type": "application/json",
})

def updateScheduleTracker(success: bool, system: str = SYSTEM, message: str = None, frequency: int = (24 * 60 * 60)):
	"""Report the outcome of a scheduled run to lucos_schedule_tracker.

	Args:
		success: Whether the job completed successfully.
		system: Identifier of the calling system. Defaults to the SYSTEM env var.
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
		"frequency": frequency,
		"status": "success" if success else "error",
		"message": message,
	}
	try:
		schedule_tracker_response = requests.post(SCHEDULE_TRACKER_ENDPOINT, json=payload, timeout=30)
		schedule_tracker_response.raise_for_status()
	except Exception as error:
		print("\033[91m [{}] ** Error calling schedule-tracker: {}\033[0m".format(datetime.now().isoformat(), error), flush=True)