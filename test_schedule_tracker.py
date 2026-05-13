import os
import unittest
from unittest.mock import patch, MagicMock

# Set required environment variables before importing the module, which reads
# them at import time.
os.environ.setdefault("SYSTEM", "test_system")
os.environ.setdefault("SCHEDULE_TRACKER_ENDPOINT", "https://schedule-tracker.example.com/report-status")

import schedule_tracker

V2_ENDPOINT = "https://schedule-tracker.example.com/v2/report-status"

# The SYSTEM constant is read from the environment at import time; use the
# module's resolved value rather than a hardcoded string so the tests work
# regardless of what SYSTEM is set to in the host environment.
SYSTEM = schedule_tracker.SYSTEM


class TestUpdateScheduleTracker(unittest.TestCase):
	"""Tests for updateScheduleTracker posting to the v2 endpoint."""

	@patch("requests.post")
	def test_success_posts_to_v2_endpoint(self, mock_post):
		mock_post.return_value = MagicMock()
		schedule_tracker.updateScheduleTracker(True, "ingestor_dbpedia")
		mock_post.assert_called_once_with(
			V2_ENDPOINT,
			json={
				"system": SYSTEM,
				"job_name": "ingestor_dbpedia",
				"frequency": 86400,
				"status": "success",
				"message": None,
			},
			timeout=30,
		)

	@patch("requests.post")
	def test_failure_with_message(self, mock_post):
		mock_post.return_value = MagicMock()
		schedule_tracker.updateScheduleTracker(
			False,
			"ingestor_loc",
			message="Connection timeout",
		)
		mock_post.assert_called_once_with(
			V2_ENDPOINT,
			json={
				"system": SYSTEM,
				"job_name": "ingestor_loc",
				"frequency": 86400,
				"status": "error",
				"message": "Connection timeout",
			},
			timeout=30,
		)

	@patch("requests.post")
	def test_custom_system_and_frequency(self, mock_post):
		mock_post.return_value = MagicMock()
		schedule_tracker.updateScheduleTracker(
			True,
			"ingestor_wikidata",
			system="lucos_arachne",
			frequency=3600,
		)
		mock_post.assert_called_once_with(
			V2_ENDPOINT,
			json={
				"system": "lucos_arachne",
				"job_name": "ingestor_wikidata",
				"frequency": 3600,
				"status": "success",
				"message": None,
			},
			timeout=30,
		)

	@patch("requests.post")
	def test_job_name_is_required(self, mock_post):
		"""Calling without job_name must raise TypeError."""
		with self.assertRaises(TypeError):
			schedule_tracker.updateScheduleTracker(True)


class TestErrorHandling(unittest.TestCase):
	"""Network errors are caught and printed, never raised."""

	@patch("requests.post", side_effect=Exception("Connection refused"))
	def test_network_error_is_caught_not_raised(self, _mock_post):
		schedule_tracker.updateScheduleTracker(True, "some_job")


if __name__ == "__main__":
	unittest.main()
