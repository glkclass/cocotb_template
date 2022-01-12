# Test Rock SPI ports: write/read registers.
# Regs config is located in cfg/regs.json:reg addresses, bit_width, ...

import logging

import cocotb
from cocotb.triggers import Timer

from cocotb_util import cocotb_util
from template.template import TemplateTestBench


@cocotb.test()
async def test_template(dut):

    dut.template_dut._log.setLevel(logging.INFO)

    # Create SPI agent for SPI #0
    template_tb = TemplateTestBench(dut)

    # Init Template
    dut.template_dut.I_SPI_SEL.value = 0

    # Run Clocks
    cocotb.start_soon(cocotb_util.clk_1GHz(dut.template_dut.I_CLK_I))

    # Reset Template
    await cocotb_util.reset(dut.template_dut.I_RESET_N, 123.1)
    await Timer(20, units='ns')

    # Start testing
    await template_tb.run_tb()
