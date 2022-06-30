# encode = utf-8

"""
This module is used to filter and reload PATH.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))
