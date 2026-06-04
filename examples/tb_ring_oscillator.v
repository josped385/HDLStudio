`timescale 1ns/1ps

module tb_ring_oscillator;

    wire real vout;

    ring_oscillator dut (
        .vout(vout)
    );

    initial begin
        $dumpfile("ring.vcd");
        $dumpvars(0, tb_ring_oscillator);
        #2000 $finish;
    end

endmodule
