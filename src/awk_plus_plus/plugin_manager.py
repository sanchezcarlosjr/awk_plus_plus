import pluggy

from awk_plus_plus import hook_implementation, dist_name
from awk_plus_plus.url_action import FileReader

hookspec = pluggy.HookspecMarker(dist_name)


class UrlReader:
    """A hook specification namespace."""

    @hookspec
    def read(self, url: str):
        """My special little hook that you can customize."""


# create a manager and add the spec
pm = pluggy.PluginManager(dist_name)
pm.add_hookspecs(UrlReader)
pm.register(FileReader())
results = pm.hook.read(url="")
print(results)