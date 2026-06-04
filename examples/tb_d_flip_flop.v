`timescale 1ns/1ps

module tb_d_flip_flop;

    reg  clk, rst_n, en, d;
    wire q;

    d_flip_flop uut (
        .clk  (clk),
        .rst_n(rst_n),
        .en   (en),
        .d    (d),
        .q    (q)
    );

    always #5 clk = ~clk;

    initial begin
        $dumpfile("d_flip_flop.vcd");
        $dumpvars(0, tb_d_flip_flop);
        $monitor("t=%0t | rst_n=%b en=%b d=%b -> q=%b", $time, rst_n, en, d, q);

        clk   = 0;
        rst_n = 0;
        en    = 0;
        d     = 0;

        #15 rst_n = 1;
        #10 en = 1; d = 1;
        #10 d = 0;
        #10 d = 1;
        #10 en = 0; d = 0;
        #10 en = 1;
        #30 $finish;
    end

endmodule