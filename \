import pluggy

from awk_plus_plus import hook_implementation, dist_name
from awk_plus_plus.url_action import FileReader, MailReader, Keyring, Sql, Http
from awk_plus_plus import _logger as logger
from urllib.parse import ParseResult

hookspec = pluggy.HookspecMarker(dist_name)

class UrlReader:
    """A hook specification namespace."""

    @hookspec
    def read(self, url: ParseResult):
        """My special little hook that you can customize."""


def init_plugin_manager():
    pm = pluggy.PluginManager(dist_name)
    pm.add_hookspecs(UrlReader)
    pm.register(FileReader())
    pm.register(MailReader())
    pm.register(Keyring())
    pm.register(Sql())
    pm.register(Http())
    return pm

plugin_manager = init_plugin_manager()
