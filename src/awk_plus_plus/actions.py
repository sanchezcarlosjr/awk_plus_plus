from urllib.parse import urlparse

from kink import inject


class Actions:
    def __init__(self):
        self.actions = []

    def parse(self, url):
        try:
            parsed_url = urlparse(url)
            for action in self.actions:
                f, matcher = action
                if args := matcher(parsed_url):
                    return f, args
            return parsed_url.geturl()
        except Exception as e:
            return url

    def command(self, matcher):
        def decorate(f):
            f = inject(f)

            self.actions.append((f, matcher))

            return f

        return decorate
