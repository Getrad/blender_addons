"""
chm_example_sayHello.py
v1.0.0
Copyright 2024 Launchpad, FRANK Labs
CONFIDENTIAL AND PROPRIETARY
"""

import sys

from launchpad.helpers import log
from launchpad.helpers.action import getActionParameters
from launchpad.helpers.entity import getLangShorthand

action = getActionParameters(sys.argv)
entity = action["entity"]
lang = getLangShorthand(action["lang"])

if __name__ == "__main__":

    if lang == "fre":
        salutation = "Bonjour"
    elif lang == "cre":
        salutation = "Wâciye"
    else:
        salutation = "Hello"

    try:
        log.info(f"{salutation}, {entity}!")

    except Exception as e:
        log.error(e)