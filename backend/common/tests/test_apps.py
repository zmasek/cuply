from unittest import mock
from unittest.mock import patch
from django.test import TestCase, override_settings
from django.apps import apps
from .factories import MicrocontrollerFactory
from ..apps import Thread
from django.conf import settings


class CommonConfigTestCase(TestCase):
    def setUp(self):
        self.common_config = apps.get_app_config("common")

    @override_settings(TESTING=False, MIGRATIONS=False)
    @patch("common.apps.Thread")
    def test_ready(self, mock_Thread):
        with patch.dict('os.environ', {'RUN_MAIN': "false"}, clear=True):
            mock_Thread_instance = mock_Thread.return_value
            mock_Thread_instance.start.return_value = None
            self.common_config.ready()
            mock_Thread_instance.start.assert_called_once()

    @patch("common.loop_manager.GreenHouseManager")
    def test_initialize_manager_no_microcontroller(self, mock_GreenHouseManager):
        mock_GreenHouseManager_instance = mock_GreenHouseManager.return_value
        self.common_config.initialize_manager()
        mock_GreenHouseManager_instance.assert_not_called()

    @patch("common.loop_manager.GreenHouseManager")
    def test_initialize_manager_microcontroller(self, mock_GreenHouseManager):
        mock_GreenHouseManager_instance = mock_GreenHouseManager.return_value
        microcontroller = MicrocontrollerFactory()
        with patch.object(microcontroller, "start"), patch.object(mock_GreenHouseManager_instance, "_setup_readings"), patch.object(mock_GreenHouseManager_instance, "run") as mock_run:
            self.common_config.initialize_manager()
            mock_run.assert_called_once()
