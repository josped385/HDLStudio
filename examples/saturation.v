module saturation (
    input  real vin,
    output real vout
);

    parameter real A = 1.0;

    assign vout = (vin >  A) ?  A :
                  (vin < -A) ? -A :
                               vin;

endmodule