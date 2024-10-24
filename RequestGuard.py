import requests
import re
from urllib import parse


class RequestGuard:
    def __init__(self, link):
        """takes any link, gets domain, scheme (https), and forbidden paths by using parse_robots"""
        parsed = parse.urlparse(link)
        self.domain = parsed.netloc
        self.scheme = parsed.scheme
        self.forbidden = self.parse_robots()

    def parse_robots(self):
        """find all forbidden paths after Disallow"""
        robots_obj = requests.get(f'{self.scheme}://{self.domain}/robots.txt')
        return re.findall(r"Disallow: (.*)", robots_obj.text.split('User-agent: *', 1)[1])

    def can_follow_link(self, url):
        """Does the link start with the stored domain?
        - If it doesn't, return False. Otherwise, proceed to the next check.
        Does the link contain any of the paths specified in the list generated from the path list provided?
        - If it does, return False, otherwise return True."""
        if not url.startswith(f'{self.scheme}://{self.domain}'):
            return False  # Different domain (different website)
        for path in self.forbidden:
            if url.startswith(f'{self.scheme}://{self.domain}{path}'):
                return False
        return True

    def make_get_request(self, *args, **kwargs):
        if self.can_follow_link(args[0]):
            requests.get(args[0], **kwargs)
        else:
            return None
