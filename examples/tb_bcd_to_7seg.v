`timescale 1ns/1ps

module tb_bcd_to_7seg;

    reg  [3:0] bcd;
    wire [6:0] seg;

    bcd_to_7seg uut (
        .bcd(bcd),
        .seg(seg)
    );

    initial begin
        $dumpfile("bcd_to_7seg.vcd");
        $dumpvars(0, tb_bcd_to_7seg);
        $monitor("t=%0t | bcd=%d -> seg=%b", $time, bcd, seg);

        for (integer i = 0; i < 16; i++) begin
            bcd = i;
            #10;
        end

        $finish;
    end

endmodule