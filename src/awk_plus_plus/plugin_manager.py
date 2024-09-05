import pluggy

from awk_plus_plus import hook_implementation, dist_name
from awk_plus_plus.url_action import FileReader, MailReader
from awk_plus_plus import _logger as logger

hookspec = pluggy.HookspecMarker(dist_name)


class UrlReader:
    """A hook specification namespace."""

    @hookspec
    def read(self, url: str):
        """My special little hook that you can customize."""


def init_plugin_manager():
    pm = pluggy.PluginManager(dist_name)
    pm.add_hookspecs(UrlReader)
    pm.register(FileReader())
    pm.register(MailReader())
    return pm

plugin_manager = init_plugin_manager()
