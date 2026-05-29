`timescale 1ns/1ps

module tb_and_gate;

reg a;
reg b;
wire y;

// Instancia del DUT (Device Under Test)
and_gate uut (
    .a(a),
    .b(b),
    .y(y)
);

initial begin
    // Generar archivo VCD
    $dumpfile("waves.vcd");
    $dumpvars(0, tb_and_gate);

    // Mostrar señales por consola
    $monitor("t=%0t | a=%b b=%b -> y=%b", $time, a, b, y);

    // Estímulos
    a = 0; b = 0;
    #10;

    a = 0; b = 1;
    #10;

    a = 1; b = 0;
    #10;

    a = 1; b = 1;
    #10;

    $finish;
end

endmodule