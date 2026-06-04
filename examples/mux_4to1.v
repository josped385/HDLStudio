module mux_4to1 (
    input  wire [3:0] in,
    input  wire [1:0] sel,
    output wire       y
);

    assign y = in[sel];

endmodule