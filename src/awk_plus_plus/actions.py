import numbers
from venv import logger
from kink import inject
import re
import keyring
import urllib


def replace_path(matches):
    service = matches.group("service")
    key = matches.group("key")
    print(matches.group())
    return keyring.get_password(service, key)
   
def interpret_url(url: str):
    url = re.sub(r"{{(keyring\.(?P<service>\w+)\.(?P<key>\w+))}}", replace_path, url)
    url = urllib.parse.urlparse(url)
    return url



class ParseResult:
    def __init__(self, url):
        self.url = url.replace("\n", " ")
        matches = re.match(r"([a-z+]+):?(.+)", self.url)
        if not matches:
            self.scheme = ""
            self.path = ""
            return
        self.scheme = matches.group(1)
        self.path = matches.group(2)
    def geturl(self):
        return self.url


class Actions:
    def __init__(self):
        self.actions = []

    def parse(self, url):
        if isinstance(url, numbers.Number):
            return url
        try:
            parsed_url = ParseResult(url)
            for action in self.actions:
                f, matcher = action
                if args := matcher(parsed_url):
                    return f, args
            return parsed_url.geturl()
        except Exception as e:
            logger.error(e)
            return url

    def command(self, matcher):
        def decorate(f):
            f = inject(f)

            self.actions.append((f, matcher))

            return f

        return decorate
