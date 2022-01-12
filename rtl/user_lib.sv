// User lib. Add missed units here


module template (
    input
        I_RESET_N,
        I_CLK_I,
        I_SPI_SEL
);
    unit_2_add_probes unit_2_add_probes();
endmodule

module unit_2_add_probes (
);
    wire bar;
    reg [2:0] foo;
    reg [5:0] qux;
endmodule
