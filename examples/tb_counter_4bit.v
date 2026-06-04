`timescale 1ns/1ps

module tb_counter_4bit;

    reg        clk;
    reg        rst_n;
    reg        enable;
    wire [3:0] count;

    counter_4bit uut (
        .clk   (clk),
        .rst_n (rst_n),
        .enable(enable),
        .count (count)
    );

    always #5 clk = ~clk;

    initial begin
        $dumpfile("counter_4bit.vcd");
        $dumpvars(0, tb_counter_4bit);
        $monitor("t=%0t | rst_n=%b enable=%b count=%d", $time, rst_n, enable, count);

        clk    = 0;
        rst_n  = 0;
        enable = 0;

        #20 rst_n = 1;
        #10 enable = 1;
        #100 enable = 0;
        #20 enable = 1;
        #80 $finish;
    end

endmodule