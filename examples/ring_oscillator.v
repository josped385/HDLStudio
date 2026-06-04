module ring_oscillator (
    output real vout
);

    parameter real k0    = 3.0;
    parameter real tau_a = 1e-9;
    parameter time DT    = 10ps;

    real n1, n2;
    real fb;

    // Nonlinear block
    saturation sat (
        .vin(vout),
        .vout(fb)
    );

    dyn_inverter #(.k0(k0), .tau_a(tau_a), .DT(DT)) inv1 (
        .vin(fb), .vout(n1)
    );

    dyn_inverter #(.k0(k0), .tau_a(tau_a), .DT(DT)) inv2 (
        .vin(n1), .vout(n2)
    );

    dyn_inverter #(.k0(k0), .tau_a(tau_a), .DT(DT)) inv3 (
        .vin(n2), .vout(vout)
    );

endmodule
