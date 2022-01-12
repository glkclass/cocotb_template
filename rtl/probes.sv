// probes. Contain probes to internal signals

import tb_util::*;

module probes ();
    genvar ii;
    bit  [255:0] 	fooo, barr;
    int i, j;

    `define UNIT cocotb_template_ttb.template_dut.unit_2_add_probes
    `define PREFIX UNIT_2_ADD_PROBES_

    `ADD_PROBE_WIRE(`UNIT, `PREFIX, bar)
    `ADD_PROBE_BUS(`UNIT, `PREFIX, foo, 3)
    `ADD_PROBE_BUS_AS_UNPACKED_ARR(`UNIT, `PREFIX, qux, 3, 2)
endmodule

