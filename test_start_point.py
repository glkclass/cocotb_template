# Start point for tests. Init. No tests here.

import logging

from cocotb_util.cocotb_util import set_starttime


log = logging.getLogger(__name__)
log.addHandler(logging.StreamHandler())
log.setLevel(logging.INFO)


# init test start time to support test timeout feature
set_starttime()
