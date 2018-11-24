import re

# optional dot, word characters, hyphens allowed
tag_regex = "^\.?[-\w]+$"
# same but repeated and joined by +
multitag_regex = "^(\+?\.?[-\w]+)+$"

def website_from_url(url: str):
    # idea: reverse url, look from last / to start
    match = re.match(r"^(?:\w+:\/\/)?(?:www\.)?([\w.]+).*", url)

    if match and match.group(1):
        return match.group(1)
