module dyn_inverter (
    input  real vin,
    output real vout
);

    parameter real k0    = 3.0;
    parameter real tau_a = 1e-9;
    parameter time DT    = 10ps;

    real x;

    // Initial condition (break symmetry)
    initial begin
        x = 1e-3;

        forever begin
            #DT;
            x = x + (DT / tau_a) * (-x - k0 * vin);
        end
    end

    assign vout = x;

endmodule
