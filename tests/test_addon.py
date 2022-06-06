import os

import pytest
from pytest_splunk_addon.standard_lib.addon_basic import Basic


# @pytest.mark.skipif(
#     os.getenv("PYTEST_SPLUNK_ADDON") is not None, reason="Only run in standalone mode"
# )
@pytest.mark.skip("Only run in standalone mode")
class TestCensysAddon(Basic):
    def empty_method():
        pass
