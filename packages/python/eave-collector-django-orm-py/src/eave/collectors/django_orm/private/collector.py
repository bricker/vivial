from typing import Any

from django.db.models import Model
from django.db.models.signals import post_save

"""
setup hast o be calle dbefore we can access any orm models (do we need to??)
> django.setup()

check settings to see if django has been setup yet (django.conf.settings[.configured])
"""

class DjangoOrmCollector:
    def _model_saved_callback(self, sender: Any, instance: Model, created: bool, raw: bool, using: str, update_fields: Any, *args, **kwargs) -> None:
        """
        https://docs.djangoproject.com/en/5.0/ref/signals/#post-save
        """
        # TODO: write to writequeue
        print("model got saved:", sender, instance, created, raw, using, update_fields)

    def instrument(self) -> None:
        post_save.connect(self._model_saved_callback)

    def uninstrument(self) -> None:
        """dont need to call this if `Signal.connect` was called with `weak=True` kwarg (the default value)"""
        post_save.disconnect(self._model_saved_callback)
