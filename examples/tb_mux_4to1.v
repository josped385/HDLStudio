`timescale 1ns/1ps

module tb_mux_4to1;

    reg  [3:0] in;
    reg  [1:0] sel;
    wire       y;

    mux_4to1 uut (
        .in (in),
        .sel(sel),
        .y  (y)
    );

    initial begin
        $dumpfile("mux_4to1.vcd");
        $dumpvars(0, tb_mux_4to1);
        $monitor("t=%0t | in=%b sel=%b -> y=%b", $time, in, sel, y);

        in = 4'b1010;

        sel = 2'b00; #10;
        sel = 2'b01; #10;
        sel = 2'b10; #10;
        sel = 2'b11; #10;

        in = 4'b0101;

        sel = 2'b00; #10;
        sel = 2'b01; #10;
        sel = 2'b10; #10;
        sel = 2'b11; #10;

        $finish;
    end

endmodule