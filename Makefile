# This file is public domain, it can be freely copied without restrictions.
# SPDX-License-Identifier: CC0-1.0

# Makefile


# user ENV
export COCOTB_TIMEOUT_HOURS = 1

# DUT defines
export DUT_GENERATE_WAVE = 0

# ENV
export RANDOM_SEED = 1638188048
export COCOTB_LOG_LEVEL = INFO
export COCOTB_REDUCED_LOG_FMT = 0

export PYTHONPATH = ..:/home/anton/design:../cocotb_repos/cocotb-coverage:/home/anton/.config/sublime-text/Packages/Todo:cocotbext-template

# defaults
SIM ?= xcelium
TOPLEVEL_LANG ?= verilog

# influences only on timescale precision!!!
# COCOTB_HDL_TIMEPRECISION = 1us

VERILOG_SOURCES += rtl/tb_util.sv
VERILOG_SOURCES += rtl/probes.sv
VERILOG_SOURCES += rtl/cocotb_template_ttb.sv

include rtl_verilog_sources.list



# TOPLEVEL is the name of the toplevel module in your Verilog or VHDL file
TOPLEVEL = cocotb_template_ttb

# MODULE is the basename of the Python test file
MODULE = test_start_point,tests.template.test_template


# include cocotb's make rules to take care of the simulator setup
include $(shell cocotb-config --makefiles)/Makefile.sim

