import os
from typing import Any


class ThumbnailMixin:
    """Build absolute paths to thumbnail files."""

    @classmethod
    def path_for_uuid(cls, config: Any, uuid: str) -> str:
        """Return absolute path for a given UUID using config."""
        return os.path.join(config.THUMBNAILS_DIR, uuid)

    def path(self, config: Any) -> str:
        """Return absolute path to the thumbnail file by its UUID."""
        return self.__class__.path_for_uuid(config, self.uuid)
