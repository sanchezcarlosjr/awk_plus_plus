import os
import urllib

import awk_plus_plus
from awk_plus_plus.io.assets import read_from


class FileReader:
    """A hook implementation namespace."""

    @awk_plus_plus.hook_implementation
    def read(self, url: str):
        url = urllib.parse.urlparse(url).path
        filename = os.path.basename(url).replace("-", "_").replace(".", "_")
        result = read_from(url)
        result['source_file'] = url
        return result


class MailReader:
    """A hook implementation namespace."""

    @awk_plus_plus.hook_implementation
    def read(self, url: str):
        result = urllib.parse.urlparse(url)
        return url