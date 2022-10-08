from django.apps import AppConfig
from django.conf import settings
from threading import Thread
import os


class CommonConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'common'

    def ready(self):
        from .signals import post_save_update_devices, post_delete_update_devices
        # needed to spawn only *one* thread
        if os.environ.get('RUN_MAIN', None) != 'true' and not (settings.TESTING or settings.MIGRATIONS or settings.COLLECTING_STATIC or settings.RUNNING_SHELL):
            thread = Thread(target=self.initialize_manager, daemon=True)
            thread.start()

    def initialize_manager(self):
        # need to be imported in the thread
        from .models import Device, Microcontroller
        from .loop_manager import GreenHouseManager
        devices = Device.objects.all()
        # could hardcode, but leaving as is for now
        microcontroller = Microcontroller.objects.first()
        if microcontroller:
            manager = GreenHouseManager(microcontroller, devices)
            manager.run()
