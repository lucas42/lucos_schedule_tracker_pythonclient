import os
import unittest
from unittest.mock import patch, MagicMock

# Set required environment variables before importing the module, which reads
# them at import time.
os.environ.setdefault("SYSTEM", "test_system")
os.environ.setdefault("SCHEDULE_TRACKER_ENDPOINT", "https://schedule-tracker.example.com/report-status")

import schedule_tracker

V1_ENDPOINT = "https://schedule-tracker.example.com/report-status"
V2_ENDPOINT = "https://schedule-tracker.example.com/v2/report-status"

# The SYSTEM constant is read from the environment at import time; use the
# module's resolved value rather than a hardcoded string so the tests work
# regardless of what SYSTEM is set to in the host environment.
SYSTEM = schedule_tracker.SYSTEM


class TestUpdateScheduleTrackerV1(unittest.TestCase):
	"""Tests for the v1 code path — no job_name provided."""

	@patch("requests.post")
	def test_success_posts_to_v1_endpoint(self, mock_post):
		mock_post.return_value = MagicMock()
		schedule_tracker.updateScheduleTracker(success=True)
		mock_post.assert_called_once_with(
			V1_ENDPOINT,
			json={
				"system": SYSTEM,
				"frequency": 86400,
				"status": "success",
				"message": None,
			},
			timeout=30,
		)

	@patch("requests.post")
	def test_failure_with_message_posts_to_v1_endpoint(self, mock_post):
		mock_post.return_value = MagicMock()
		schedule_tracker.updateScheduleTracker(success=False, message="Database connection failed")
		mock_post.assert_called_once_with(
			V1_ENDPOINT,
			json={
				"system": SYSTEM,
				"frequency": 86400,
				"status": "error",
				"message": "Database connection failed",
			},
			timeout=30,
		)

	@patch("requests.post")
	def test_explicit_job_name_none_uses_v1_endpoint(self, mock_post):
		"""Explicitly passing job_name=None must still use the v1 endpoint."""
		mock_post.return_value = MagicMock()
		schedule_tracker.updateScheduleTracker(success=True, job_name=None)
		mock_post.assert_called_once_with(
			V1_ENDPOINT,
			json={
				"system": SYSTEM,
				"frequency": 86400,
				"status": "success",
				"message": None,
			},
			timeout=30,
		)

	@patch("requests.post")
	def test_custom_frequency_posts_to_v1_endpoint(self, mock_post):
		mock_post.return_value = MagicMock()
		schedule_tracker.updateScheduleTracker(success=True, frequency=3600)
		mock_post.assert_called_once_with(
			V1_ENDPOINT,
			json={
				"system": SYSTEM,
				"frequency": 3600,
				"status": "success",
				"message": None,
			},
			timeout=30,
		)


class TestUpdateScheduleTrackerV2(unittest.TestCase):
	"""Tests for the v2 code path — job_name provided."""

	@patch("requests.post")
	def test_success_with_job_name_posts_to_v2_endpoint(self, mock_post):
		mock_post.return_value = MagicMock()
		schedule_tracker.updateScheduleTracker(success=True, job_name="ingestor_dbpedia")
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
	def test_failure_with_job_name_and_message_posts_to_v2_endpoint(self, mock_post):
		mock_post.return_value = MagicMock()
		schedule_tracker.updateScheduleTracker(
			success=False,
			job_name="ingestor_loc",
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
	def test_custom_system_and_frequency_with_job_name(self, mock_post):
		mock_post.return_value = MagicMock()
		schedule_tracker.updateScheduleTracker(
			success=True,
			system="lucos_arachne",
			job_name="ingestor_wikidata",
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


class TestErrorHandling(unittest.TestCase):
	"""Error handling applies to both code paths."""

	@patch("requests.post", side_effect=Exception("Connection refused"))
	def test_v1_network_error_is_caught_not_raised(self, _mock_post):
		"""Network errors on the v1 path must be swallowed (not raised)."""
		schedule_tracker.updateScheduleTracker(success=True)

	@patch("requests.post", side_effect=Exception("Connection refused"))
	def test_v2_network_error_is_caught_not_raised(self, _mock_post):
		"""Network errors on the v2 path must be swallowed (not raised)."""
		schedule_tracker.updateScheduleTracker(success=True, job_name="some_job")


if __name__ == "__main__":
	unittest.main()
