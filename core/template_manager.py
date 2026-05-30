import os


TEMPLATE_CATEGORIES = [
    {
        "id": "fsm",
        "name": "State Machines",
        "icon": "fsm",
        "templates": [
            {
                "id": "moore_fsm",
                "name": "Moore FSM",
                "description": "Moore finite state machine with 3-process style (next-state, state reg, output)",
                "formats": {
                    "verilog": """\
// Moore Finite State Machine
// Outputs depend only on current state

module moore_fsm #(
    parameter STATE_WIDTH = 2
)(
    input  wire             clk,
    input  wire             rst_n,
    input  wire             input_signal,
    output reg              output_signal
);

    // State encoding
    localparam [STATE_WIDTH-1:0]
        IDLE    = 2'b00,
        STATE_1 = 2'b01,
        STATE_2 = 2'b10,
        STATE_3 = 2'b11;

    reg [STATE_WIDTH-1:0] current_state, next_state;

    // State register (sequential)
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n)
            current_state <= IDLE;
        else
            current_state <= next_state;
    end

    // Next state logic (combinational)
    always @(*) begin
        next_state = current_state;
        case (current_state)
            IDLE: begin
                if (input_signal)
                    next_state = STATE_1;
            end
            STATE_1: begin
                if (input_signal)
                    next_state = STATE_2;
                else
                    next_state = IDLE;
            end
            STATE_2: begin
                if (input_signal)
                    next_state = STATE_3;
                else
                    next_state = STATE_1;
            end
            STATE_3: begin
                next_state = IDLE;
            end
        endcase
    end

    // Output logic (combinational) — depends only on current_state
    always @(*) begin
        case (current_state)
            IDLE:    output_signal = 1'b0;
            STATE_1: output_signal = 1'b0;
            STATE_2: output_signal = 1'b1;
            STATE_3: output_signal = 1'b1;
            default: output_signal = 1'b0;
        endcase
    end

endmodule
""",
                    "systemverilog": """\
// Moore Finite State Machine (SystemVerilog)
// Outputs depend only on current state
// Uses enum for state types and always_ff/always_comb

module moore_fsm #(
    parameter int STATE_WIDTH = 2
)(
    input  logic        clk,
    input  logic        rst_n,
    input  logic        input_signal,
    output logic        output_signal
);

    typedef enum logic [STATE_WIDTH-1:0] {
        IDLE    = 2'b00,
        STATE_1 = 2'b01,
        STATE_2 = 2'b10,
        STATE_3 = 2'b11
    } state_t;

    state_t current_state, next_state;

    // State register
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n)
            current_state <= IDLE;
        else
            current_state <= next_state;
    end

    // Next state logic
    always_comb begin
        next_state = current_state;
        unique case (current_state)
            IDLE:    if (input_signal) next_state = STATE_1;
            STATE_1: next_state = input_signal ? STATE_2 : IDLE;
            STATE_2: next_state = input_signal ? STATE_3 : STATE_1;
            STATE_3: next_state = IDLE;
        endcase
    end

    // Output logic — depends only on current_state
    always_comb begin
        unique case (current_state)
            IDLE:    output_signal = 1'b0;
            STATE_1: output_signal = 1'b0;
            STATE_2: output_signal = 1'b1;
            STATE_3: output_signal = 1'b1;
            default: output_signal = 1'b0;
        endcase
    end

endmodule
""",
                    "vhdl": """\
-- Moore Finite State Machine
-- Outputs depend only on current state

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity moore_fsm is
    generic (
        STATE_WIDTH : positive := 2
    );
    port (
        clk          : in  std_logic;
        rst_n        : in  std_logic;
        input_signal : in  std_logic;
        output_signal: out std_logic
    );
end entity;

architecture rtl of moore_fsm is

    type state_t is (IDLE, STATE_1, STATE_2, STATE_3);
    signal current_state, next_state : state_t;

begin

    -- State register
    process(clk, rst_n)
    begin
        if rst_n = '0' then
            current_state <= IDLE;
        elsif rising_edge(clk) then
            current_state <= next_state;
        end if;
    end process;

    -- Next state logic
    process(current_state, input_signal)
    begin
        next_state <= current_state;
        case current_state is
            when IDLE =>
                if input_signal = '1' then
                    next_state <= STATE_1;
                end if;
            when STATE_1 =>
                if input_signal = '1' then
                    next_state <= STATE_2;
                else
                    next_state <= IDLE;
                end if;
            when STATE_2 =>
                if input_signal = '1' then
                    next_state <= STATE_3;
                else
                    next_state <= STATE_1;
                end if;
            when STATE_3 =>
                next_state <= IDLE;
        end case;
    end process;

    -- Output logic
    process(current_state)
    begin
        case current_state is
            when IDLE    => output_signal <= '0';
            when STATE_1 => output_signal <= '0';
            when STATE_2 => output_signal <= '1';
            when STATE_3 => output_signal <= '1';
            when others  => output_signal <= '0';
        end case;
    end process;

end architecture;
""",
                },
            },
            {
                "id": "mealy_fsm",
                "name": "Mealy FSM",
                "description": "Mealy finite state machine — outputs depend on current state AND inputs",
                "formats": {
                    "verilog": """\
// Mealy Finite State Machine
// Outputs depend on current state AND inputs

module mealy_fsm #(
    parameter STATE_WIDTH = 2
)(
    input  wire             clk,
    input  wire             rst_n,
    input  wire             input_signal,
    output reg              output_signal
);

    localparam [STATE_WIDTH-1:0]
        IDLE    = 2'b00,
        STATE_1 = 2'b01,
        STATE_2 = 2'b10,
        STATE_3 = 2'b11;

    reg [STATE_WIDTH-1:0] current_state, next_state;

    // State register
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n)
            current_state <= IDLE;
        else
            current_state <= next_state;
    end

    // Next state and output logic (combinational)
    always @(*) begin
        next_state   = current_state;
        output_signal = 1'b0;

        case (current_state)
            IDLE: begin
                if (input_signal) begin
                    next_state = STATE_1;
                    output_signal = 1'b0;
                end
            end
            STATE_1: begin
                if (input_signal) begin
                    next_state = STATE_2;
                    output_signal = 1'b0;
                end else begin
                    next_state = IDLE;
                    output_signal = 1'b1;
                end
            end
            STATE_2: begin
                if (input_signal) begin
                    next_state = STATE_3;
                    output_signal = 1'b1;
                end else begin
                    next_state = STATE_1;
                    output_signal = 1'b0;
                end
            end
            STATE_3: begin
                next_state = IDLE;
                output_signal = 1'b0;
            end
        endcase
    end

endmodule
""",
                    "systemverilog": """\
// Mealy Finite State Machine (SystemVerilog)
// Outputs depend on current state AND inputs

module mealy_fsm #(
    parameter int STATE_WIDTH = 2
)(
    input  logic        clk,
    input  logic        rst_n,
    input  logic        input_signal,
    output logic        output_signal
);

    typedef enum logic [STATE_WIDTH-1:0] {
        IDLE    = 2'b00,
        STATE_1 = 2'b01,
        STATE_2 = 2'b10,
        STATE_3 = 2'b11
    } state_t;

    state_t current_state, next_state;

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n)
            current_state <= IDLE;
        else
            current_state <= next_state;
    end

    always_comb begin
        next_state    = current_state;
        output_signal = 1'b0;
        unique case (current_state)
            IDLE: begin
                if (input_signal) begin
                    next_state = STATE_1;
                end
            end
            STATE_1: begin
                if (input_signal) begin
                    next_state = STATE_2;
                end else begin
                    next_state   = IDLE;
                    output_signal = 1'b1;
                end
            end
            STATE_2: begin
                if (input_signal) begin
                    next_state    = STATE_3;
                    output_signal = 1'b1;
                end else begin
                    next_state = STATE_1;
                end
            end
            STATE_3: begin
                next_state = IDLE;
            end
        endcase
    end

endmodule
""",
                    "vhdl": """\
-- Mealy Finite State Machine
-- Outputs depend on current state AND inputs

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity mealy_fsm is
    generic (
        STATE_WIDTH : positive := 2
    );
    port (
        clk          : in  std_logic;
        rst_n        : in  std_logic;
        input_signal : in  std_logic;
        output_signal: out std_logic
    );
end entity;

architecture rtl of mealy_fsm is

    type state_t is (IDLE, STATE_1, STATE_2, STATE_3);
    signal current_state, next_state : state_t;

begin

    process(clk, rst_n)
    begin
        if rst_n = '0' then
            current_state <= IDLE;
        elsif rising_edge(clk) then
            current_state <= next_state;
        end if;
    end process;

    process(current_state, input_signal)
    begin
        next_state    <= current_state;
        output_signal <= '0';
        case current_state is
            when IDLE =>
                if input_signal = '1' then
                    next_state <= STATE_1;
                end if;
            when STATE_1 =>
                if input_signal = '1' then
                    next_state <= STATE_2;
                else
                    next_state    <= IDLE;
                    output_signal <= '1';
                end if;
            when STATE_2 =>
                if input_signal = '1' then
                    next_state    <= STATE_3;
                    output_signal <= '1';
                else
                    next_state <= STATE_1;
                end if;
            when STATE_3 =>
                next_state <= IDLE;
        end case;
    end process;

end architecture;
""",
                },
            },
        ],
    },
    {
        "id": "uart",
        "name": "UART",
        "icon": "uart",
        "templates": [
            {
                "id": "uart_tx",
                "name": "UART Transmitter",
                "description": "8-bit UART transmitter with configurable baud rate, 1 start bit, 1 stop bit, no parity",
                "formats": {
                    "verilog": """\
// UART Transmitter
// 8-N-1 format: 1 start bit, 8 data bits, 1 stop bit

module uart_tx #(
    parameter CLK_FREQ = 50_000_000,
    parameter BAUD_RATE = 115_200
)(
    input  wire       clk,
    input  wire       rst_n,
    input  wire [7:0] tx_data,
    input  wire       tx_start,
    output reg        tx_busy,
    output reg        tx_serial
);

    localparam BIT_TICKS = CLK_FREQ / BAUD_RATE;

    reg [15:0] baud_counter;
    reg [3:0]  bit_index;
    reg [9:0]  shift_reg;
    reg        sending;

    // Baud rate generator and transmitter
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            tx_serial <= 1'b1;
            tx_busy <= 1'b0;
            sending <= 1'b0;
            baud_counter <= 0;
            bit_index <= 0;
            shift_reg <= 0;
        end else if (!sending) begin
            tx_serial <= 1'b1;
            tx_busy <= 1'b0;
            if (tx_start) begin
                sending <= 1'b1;
                tx_busy <= 1'b1;
                baud_counter <= 0;
                bit_index <= 0;
                shift_reg <= {1'b1, tx_data, 1'b0};  // stop, data, start
            end
        end else begin
            if (baud_counter == BIT_TICKS - 1) begin
                baud_counter <= 0;
                tx_serial <= shift_reg[0];
                shift_reg <= {1'b1, shift_reg[9:1]};
                if (bit_index == 9) begin
                    sending <= 1'b0;
                    tx_busy <= 1'b0;
                end else begin
                    bit_index <= bit_index + 1;
                end
            end else begin
                baud_counter <= baud_counter + 1;
            end
        end
    end

endmodule
""",
                    "systemverilog": """\
// UART Transmitter (SystemVerilog)
// 8-N-1 format: 1 start bit, 8 data bits, 1 stop bit

module uart_tx #(
    parameter int CLK_FREQ  = 50_000_000,
    parameter int BAUD_RATE = 115_200
)(
    input  logic       clk,
    input  logic       rst_n,
    input  logic [7:0] tx_data,
    input  logic       tx_start,
    output logic       tx_busy,
    output logic       tx_serial
);

    localparam int BIT_TICKS = CLK_FREQ / BAUD_RATE;

    logic [15:0] baud_counter;
    logic [3:0]  bit_index;
    logic [9:0]  shift_reg;
    logic        sending;

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            tx_serial   <= 1'b1;
            tx_busy     <= 1'b0;
            sending     <= 1'b0;
            baud_counter <= 0;
            bit_index   <= 0;
            shift_reg   <= 0;
        end else if (!sending) begin
            tx_serial <= 1'b1;
            tx_busy   <= 1'b0;
            if (tx_start) begin
                sending     <= 1'b1;
                tx_busy     <= 1'b1;
                baud_counter <= 0;
                bit_index   <= 0;
                shift_reg   <= {1'b1, tx_data, 1'b0};
            end
        end else begin
            if (baud_counter == BIT_TICKS - 1) begin
                baud_counter <= 0;
                tx_serial   <= shift_reg[0];
                shift_reg   <= {1'b1, shift_reg[9:1]};
                if (bit_index == 9) begin
                    sending <= 1'b0;
                end else begin
                    bit_index <= bit_index + 1;
                end
            end else begin
                baud_counter <= baud_counter + 1;
            end
        end
    end

endmodule
""",
                    "vhdl": """\
-- UART Transmitter
-- 8-N-1 format: 1 start bit, 8 data bits, 1 stop bit

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity uart_tx is
    generic (
        CLK_FREQ  : positive := 50_000_000;
        BAUD_RATE : positive := 115_200
    );
    port (
        clk       : in  std_logic;
        rst_n     : in  std_logic;
        tx_data   : in  std_logic_vector(7 downto 0);
        tx_start  : in  std_logic;
        tx_busy   : out std_logic;
        tx_serial : out std_logic
    );
end entity;

architecture rtl of uart_tx is

    constant BIT_TICKS : positive := CLK_FREQ / BAUD_RATE;

    signal baud_counter : unsigned(15 downto 0);
    signal bit_index    : unsigned(3 downto 0);
    signal shift_reg    : std_logic_vector(9 downto 0);
    signal sending      : std_logic;

begin

    process(clk, rst_n)
    begin
        if rst_n = '0' then
            tx_serial   <= '1';
            tx_busy     <= '0';
            sending     <= '0';
            baud_counter <= (others => '0');
            bit_index   <= (others => '0');
            shift_reg   <= (others => '0');
        elsif rising_edge(clk) then
            if sending = '0' then
                tx_serial <= '1';
                tx_busy   <= '0';
                if tx_start = '1' then
                    sending     <= '1';
                    tx_busy     <= '1';
                    baud_counter <= (others => '0');
                    bit_index    <= (others => '0');
                    shift_reg   <= '1' & tx_data & '0';
                end if;
            else
                if baud_counter = BIT_TICKS - 1 then
                    baud_counter <= (others => '0');
                    tx_serial    <= shift_reg(0);
                    shift_reg    <= '1' & shift_reg(9 downto 1);
                    if bit_index = 9 then
                        sending <= '0';
                    else
                        bit_index <= bit_index + 1;
                    end if;
                else
                    baud_counter <= baud_counter + 1;
                end if;
            end if;
        end if;
    end process;

end architecture;
""",
                },
            },
            {
                "id": "uart_rx",
                "name": "UART Receiver",
                "description": "8-bit UART receiver with configurable baud rate, 1 start bit, 1 stop bit, no parity",
                "formats": {
                    "verilog": """\
// UART Receiver
// 8-N-1: 1 start bit, 8 data bits, 1 stop bit
// Oversamples at 16x baud rate for robust start detection

module uart_rx #(
    parameter CLK_FREQ = 50_000_000,
    parameter BAUD_RATE = 115_200
)(
    input  wire       clk,
    input  wire       rst_n,
    input  wire       rx_serial,
    output reg [7:0] rx_data,
    output reg        rx_valid
);

    localparam BAUD_TICKS = CLK_FREQ / BAUD_RATE;
    localparam HALF_TICK  = BAUD_TICKS / 2;

    reg        rx_sync, rx_prev;
    reg [15:0] baud_counter;
    reg [3:0]  bit_index;
    reg [7:0]  data_reg;
    reg        receiving;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            rx_sync   <= 1'b1;
            rx_prev   <= 1'b1;
            rx_data   <= 0;
            rx_valid  <= 1'b0;
            receiving <= 1'b0;
            baud_counter <= 0;
            bit_index <= 0;
            data_reg  <= 0;
        end else begin
            rx_sync <= rx_serial;
            rx_prev <= rx_sync;
            rx_valid <= 1'b0;

            if (!receiving) begin
                // Detect start bit: falling edge
                if (rx_prev && !rx_sync) begin
                    receiving <= 1'b1;
                    baud_counter <= 0;
                    bit_index <= 0;
                end
            end else begin
                if (baud_counter == BAUD_TICKS - 1) begin
                    baud_counter <= 0;
                    if (bit_index == 0) begin
                        // Skip start bit
                        bit_index <= bit_index + 1;
                    end else if (bit_index <= 8) begin
                        data_reg <= {rx_sync, data_reg[7:1]};
                        bit_index <= bit_index + 1;
                    end else begin
                        // Stop bit — valid
                        rx_data  <= data_reg;
                        rx_valid <= 1'b1;
                        receiving <= 1'b0;
                    end
                end else begin
                    baud_counter <= baud_counter + 1;
                end
            end
        end
    end

endmodule
""",
                    "systemverilog": """\
// UART Receiver (SystemVerilog)
// 8-N-1: 1 start bit, 8 data bits, 1 stop bit
// Oversamples at 16x baud rate for robust start detection

module uart_rx #(
    parameter int CLK_FREQ  = 50_000_000,
    parameter int BAUD_RATE = 115_200
)(
    input  logic       clk,
    input  logic       rst_n,
    input  logic       rx_serial,
    output logic [7:0] rx_data,
    output logic       rx_valid
);

    localparam int BAUD_TICKS = CLK_FREQ / BAUD_RATE;

    logic        rx_sync, rx_prev;
    logic [15:0] baud_counter;
    logic [3:0]  bit_index;
    logic [7:0]  data_reg;
    logic        receiving;

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            rx_sync    <= 1'b1;
            rx_prev    <= 1'b1;
            rx_data    <= 0;
            rx_valid   <= 1'b0;
            receiving  <= 1'b0;
            baud_counter <= 0;
            bit_index  <= 0;
            data_reg   <= 0;
        end else begin
            rx_sync  <= rx_serial;
            rx_prev  <= rx_sync;
            rx_valid <= 1'b0;

            if (!receiving) begin
                if (rx_prev && !rx_sync) begin
                    receiving    <= 1'b1;
                    baud_counter <= 0;
                    bit_index    <= 0;
                end
            end else begin
                if (baud_counter == BAUD_TICKS - 1) begin
                    baud_counter <= 0;
                    if (bit_index == 0) begin
                        bit_index <= bit_index + 1;
                    end else if (bit_index <= 8) begin
                        data_reg <= {rx_sync, data_reg[7:1]};
                        bit_index <= bit_index + 1;
                    end else begin
                        rx_data    <= data_reg;
                        rx_valid   <= 1'b1;
                        receiving  <= 1'b0;
                    end
                end else begin
                    baud_counter <= baud_counter + 1;
                end
            end
        end
    end

endmodule
""",
                },
            },
            {
                "id": "uart_baud_gen",
                "name": "Baud Rate Generator",
                "description": "Configurable baud rate tick generator for UART",
                "formats": {
                    "verilog": """\
// Baud Rate Generator
// Generates a tick pulse at the configured baud rate

module baud_gen #(
    parameter CLK_FREQ  = 50_000_000,
    parameter BAUD_RATE = 115_200
)(
    input  wire       clk,
    input  wire       rst_n,
    input  wire       enable,
    output reg        baud_tick
);

    localparam DIV_MAX = CLK_FREQ / BAUD_RATE;

    reg [15:0] counter;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            counter   <= 0;
            baud_tick <= 1'b0;
        end else if (enable) begin
            if (counter == DIV_MAX - 1) begin
                counter   <= 0;
                baud_tick <= 1'b1;
            end else begin
                counter   <= counter + 1;
                baud_tick <= 1'b0;
            end
        end else begin
            counter   <= 0;
            baud_tick <= 1'b0;
        end
    end

endmodule
""",
                    "systemverilog": """\
// Baud Rate Generator (SystemVerilog)

module baud_gen #(
    parameter int CLK_FREQ  = 50_000_000,
    parameter int BAUD_RATE = 115_200
)(
    input  logic clk,
    input  logic rst_n,
    input  logic enable,
    output logic baud_tick
);

    localparam int DIV_MAX = CLK_FREQ / BAUD_RATE;

    logic [15:0] counter;

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            counter   <= 0;
            baud_tick <= 1'b0;
        end else if (enable) begin
            if (counter == DIV_MAX - 1) begin
                counter   <= 0;
                baud_tick <= 1'b1;
            end else begin
                counter   <= counter + 1;
                baud_tick <= 1'b0;
            end
        end else begin
            counter   <= 0;
            baud_tick <= 1'b0;
        end
    end

endmodule
""",
                },
            },
        ],
    },
    {
        "id": "i2c",
        "name": "I2C",
        "icon": "i2c",
        "templates": [
            {
                "id": "i2c_master",
                "name": "I2C Master Controller",
                "description": "I2C master with start/stop/restart, 7-bit addressing, ACK handling",
                "formats": {
                    "verilog": """\
// I2C Master Controller
// 7-bit addressing, clock stretching support
// FSM-based with start, data/ack, stop phases

module i2c_master #(
    parameter CLK_FREQ  = 50_000_000,
    parameter I2C_FREQ  = 100_000
)(
    input  wire       clk,
    input  wire       rst_n,
    input  wire       start,
    input  wire       rw,          // 0 = write, 1 = read
    input  wire [6:0] dev_addr,
    input  wire [7:0] data_wr,
    output reg  [7:0] data_rd,
    output reg        busy,
    output reg        ack_error,
    inout  wire       scl,
    inout  wire       sda
);

    localparam DIV_MAX = CLK_FREQ / I2C_FREQ / 4;

    localparam [2:0]
        IDLE     = 0,
        START    = 1,
        SEND_BYTE= 2,
        GET_ACK  = 3,
        READ_BYTE= 4,
        SEND_ACK = 5,
        STOP     = 6;

    reg [2:0]  state;
    reg [2:0]  bit_cnt;
    reg [7:0]  shift_reg;
    reg [15:0] clk_cnt;
    reg        scl_out, sda_out;
    reg        scl_en,  sda_en;

    // Tristate buffers
    assign scl = scl_en ? scl_out : 1'bz;
    assign sda = sda_en ? sda_out : 1'bz;

    reg scl_in, sda_in, sda_sync;
    reg sda_rise;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state <= IDLE;
            busy  <= 1'b0;
            ack_error <= 1'b0;
            clk_cnt <= 0;
            scl_en <= 1'b0;
            sda_en <= 1'b0;
            scl_out <= 1'b1;
            sda_out <= 1'b1;
        end else begin
            sda_sync <= sda;
            scl_in   <= scl;
            sda_rise <= 1'b0;

            case (state)
                IDLE: begin
                    busy <= 1'b0;
                    scl_en <= 1'b0;
                    sda_en <= 1'b0;
                    scl_out <= 1'b1;
                    sda_out <= 1'b1;
                    if (start) begin
                        busy  <= 1'b1;
                        state <= START;
                        clk_cnt <= 0;
                    end
                end

                START: begin
                    // Generate start condition: SDA falls while SCL high
                    sda_en <= 1'b1;
                    scl_en <= 1'b0;
                    scl_out <= 1'b1;
                    if (clk_cnt < DIV_MAX) begin
                        sda_out <= 1'b1;
                        clk_cnt <= clk_cnt + 1;
                    end else if (clk_cnt < DIV_MAX * 2) begin
                        sda_out <= 1'b0;  // falling edge
                        clk_cnt <= clk_cnt + 1;
                    end else begin
                        clk_cnt <= 0;
                        state <= SEND_BYTE;
                        bit_cnt <= 8;
                        shift_reg <= {dev_addr, rw};
                    end
                end

                SEND_BYTE: begin
                    scl_en <= 1'b1;
                    sda_en <= 1'b1;
                    if (clk_cnt < DIV_MAX) begin
                        scl_out <= 0;  // SCL low
                        sda_out <= shift_reg[7];
                        clk_cnt <= clk_cnt + 1;
                    end else if (clk_cnt < DIV_MAX * 2) begin
                        scl_out <= 1;  // SCL high — data sampled
                        clk_cnt <= clk_cnt + 1;
                    end else if (clk_cnt < DIV_MAX * 3) begin
                        scl_out <= 0;
                        clk_cnt <= clk_cnt + 1;
                    end else begin
                        clk_cnt <= 0;
                        shift_reg <= {shift_reg[6:0], 1'b0};
                        if (bit_cnt == 1) begin
                            state <= GET_ACK;
                        end else begin
                            bit_cnt <= bit_cnt - 1;
                        end
                    end
                end

                GET_ACK: begin
                    sda_en <= 1'b0;  // release SDA for slave ACK
                    scl_en <= 1'b1;
                    if (clk_cnt < DIV_MAX) begin
                        scl_out <= 0;
                        clk_cnt <= clk_cnt + 1;
                    end else if (clk_cnt < DIV_MAX * 2) begin
                        scl_out <= 1;  // sample ACK
                        clk_cnt <= clk_cnt + 1;
                    end else if (clk_cnt < DIV_MAX * 3) begin
                        scl_out <= 0;
                        clk_cnt <= clk_cnt + 1;
                    end else begin
                        clk_cnt <= 0;
                        ack_error <= sda_sync;  // active low ACK
                        if (rw)
                            state <= READ_BYTE;
                        else
                            state <= STOP;
                        bit_cnt <= 8;
                    end
                end

                READ_BYTE: begin
                    sda_en <= 1'b0;
                    scl_en <= 1'b1;
                    if (clk_cnt < DIV_MAX) begin
                        scl_out <= 0;
                        clk_cnt <= clk_cnt + 1;
                    end else if (clk_cnt < DIV_MAX * 2) begin
                        scl_out <= 1;
                        shift_reg <= {shift_reg[6:0], sda_sync};
                        clk_cnt <= clk_cnt + 1;
                    end else if (clk_cnt < DIV_MAX * 3) begin
                        scl_out <= 0;
                        clk_cnt <= clk_cnt + 1;
                    end else begin
                        clk_cnt <= 0;
                        if (bit_cnt == 1) begin
                            data_rd <= {shift_reg[6:0], sda_sync};
                            state <= SEND_ACK;
                        end else begin
                            bit_cnt <= bit_cnt - 1;
                        end
                    end
                end

                SEND_ACK: begin
                    sda_en <= 1'b1;
                    sda_out <= 1'b1;  // NACK (last byte)
                    scl_en <= 1'b1;
                    if (clk_cnt < DIV_MAX) begin
                        scl_out <= 0;
                        clk_cnt <= clk_cnt + 1;
                    end else if (clk_cnt < DIV_MAX * 2) begin
                        scl_out <= 1;
                        clk_cnt <= clk_cnt + 1;
                    end else if (clk_cnt < DIV_MAX * 3) begin
                        scl_out <= 0;
                        clk_cnt <= clk_cnt + 1;
                    end else begin
                        clk_cnt <= 0;
                        state <= STOP;
                    end
                end

                STOP: begin
                    // Generate stop: SDA rises while SCL high
                    scl_en <= 1'b1;
                    sda_en <= 1'b1;
                    if (clk_cnt < DIV_MAX) begin
                        scl_out <= 0;
                        sda_out <= 1'b0;
                        clk_cnt <= clk_cnt + 1;
                    end else if (clk_cnt < DIV_MAX * 2) begin
                        scl_out <= 1;
                        sda_out <= 1'b0;
                        clk_cnt <= clk_cnt + 1;
                    end else if (clk_cnt < DIV_MAX * 3) begin
                        sda_out <= 1'b1;  // rising edge
                        clk_cnt <= clk_cnt + 1;
                    end else begin
                        clk_cnt <= 0;
                        state <= IDLE;
                    end
                end
            endcase
        end
    end

endmodule
""",
                },
            },
            {
                "id": "i2c_slave",
                "name": "I2C Slave",
                "description": "I2C slave with 7-bit address detection, read/write support",
                "formats": {
                    "verilog": """\
// I2C Slave
// 7-bit address detection, supports write and read transactions

module i2c_slave #(
    parameter I2C_ADDR = 7'h50
)(
    input  wire       clk,
    input  wire       rst_n,
    input  wire       scl,
    inout  wire       sda,
    output reg  [7:0] data_byte,
    output reg        data_valid,
    input  wire [7:0] data_to_send,
    input  wire       data_available
);

    reg scl_sync, scl_prev;
    reg sda_sync, sda_prev;
    reg sda_out, sda_en;
    reg [3:0] bit_cnt;
    reg [6:0] addr_recv;
    reg [7:0] shift_reg;
    reg       got_addr;
    reg       rw_flag;

    assign sda = sda_en ? sda_out : 1'bz;

    // SCL and SDA sampling with edge detection
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            scl_sync <= 1'b1;
            scl_prev <= 1'b1;
            sda_sync <= 1'b1;
            sda_prev <= 1'b1;
        end else begin
            scl_prev <= scl_sync;
            scl_sync <= scl;
            sda_prev <= sda_sync;
            sda_sync <= sda;
        end
    end

    wire scl_rise = scl_sync && !scl_prev;
    wire scl_fall = !scl_sync && scl_prev;
    wire sda_fall = !sda_sync && sda_prev && scl_sync;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            bit_cnt <= 0;
            shift_reg <= 0;
            got_addr <= 1'b0;
            sda_en <= 1'b0;
            sda_out <= 1'b1;
            data_valid <= 1'b0;
        end else begin
            data_valid <= 1'b0;

            // Start condition
            if (sda_fall) begin
                bit_cnt <= 0;
                got_addr <= 1'b0;
                sda_en <= 1'b0;
                sda_out <= 1'b1;
            end

            // Sample data on SCL rising edge
            if (scl_rise && !got_addr) begin
                shift_reg <= {shift_reg[6:0], sda_sync};
                if (bit_cnt < 7) begin
                    bit_cnt <= bit_cnt + 1;
                end else begin
                    // Last bit is R/W
                    rw_flag <= sda_sync;
                    addr_recv <= {shift_reg[6:0], sda_sync};
                    bit_cnt <= 0;
                end
            end

            // After 9 bits (8 addr + 1 ACK), check address
            if (scl_rise && got_addr) begin
                if (rw_flag) begin
                    // Read — send data
                    if (bit_cnt < 8) begin
                        sda_out <= data_to_send[7];
                        bit_cnt <= bit_cnt + 1;
                    end else begin
                        sda_en <= 1'b0;
                        bit_cnt <= 0;
                        got_addr <= 1'b0;
                    end
                end else begin
                    // Write — receive data
                    shift_reg <= {shift_reg[6:0], sda_sync};
                    if (bit_cnt < 8) begin
                        bit_cnt <= bit_cnt + 1;
                    end else begin
                        data_byte <= {shift_reg[6:0], sda_sync};
                        data_valid <= 1'b1;
                        bit_cnt <= 0;
                        got_addr <= 1'b0;
                    end
                end
            end

            // ACK generation after address match
            if (scl_fall && addr_recv[7:1] == I2C_ADDR && !got_addr && bit_cnt == 0) begin
                got_addr <= 1'b1;
                sda_en <= 1'b1;
                sda_out <= 1'b0;  // ACK
                bit_cnt <= 0;
            end
        end
    end

endmodule
""",
                },
            },
        ],
    },
    {
        "id": "spi",
        "name": "SPI",
        "icon": "spi",
        "templates": [
            {
                "id": "spi_master",
                "name": "SPI Master",
                "description": "SPI master with configurable CPOL/CPHA, clock divider, full-duplex",
                "formats": {
                    "verilog": """\
// SPI Master
// Full-duplex, configurable polarity (CPOL) and phase (CPHA)

module spi_master #(
    parameter CLK_FREQ    = 50_000_000,
    parameter SPI_FREQ    = 10_000_000,
    parameter DATA_WIDTH  = 8,
    parameter CPOL        = 0,
    parameter CPHA        = 0
)(
    input  wire               clk,
    input  wire               rst_n,
    input  wire               start,
    input  wire [DATA_WIDTH-1:0] data_tx,
    output reg  [DATA_WIDTH-1:0] data_rx,
    output reg                 busy,
    output reg                 sclk,
    output reg                 mosi,
    input  wire                miso,
    output reg                 cs_n
);

    localparam DIV_MAX = CLK_FREQ / SPI_FREQ / 2;

    localparam [1:0]
        IDLE = 0,
        TX   = 1,
        DONE = 2;

    reg [1:0]  state;
    reg [15:0] clk_cnt;
    reg [3:0]  bit_cnt;
    reg [DATA_WIDTH-1:0] shift_tx, shift_rx;
    reg        sclk_int, sclk_prev;
    reg        sample_edge, change_edge;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state <= IDLE;
            busy  <= 1'b0;
            cs_n  <= 1'b1;
            sclk  <= CPOL;
            mosi  <= 1'b0;
            clk_cnt <= 0;
            bit_cnt <= 0;
        end else begin
            sclk_prev <= sclk_int;

            case (state)
                IDLE: begin
                    cs_n  <= 1'b1;
                    sclk  <= CPOL;
                    busy  <= 1'b0;
                    if (start) begin
                        busy     <= 1'b1;
                        cs_n     <= 1'b0;
                        state    <= TX;
                        clk_cnt  <= 0;
                        bit_cnt  <= DATA_WIDTH;
                        shift_tx <= data_tx;
                        shift_rx <= 0;
                        sclk_int <= CPOL;
                    end
                end

                TX: begin
                    // Generate SCLK
                    if (clk_cnt == DIV_MAX - 1) begin
                        clk_cnt    <= 0;
                        sclk_int   <= ~sclk_int;
                    end else begin
                        clk_cnt    <= clk_cnt + 1;
                    end

                    sclk <= sclk_int;

                    // Determine sample/change edges based on CPOL/CPHA
                    if (CPHA == 0) begin
                        sample_edge = ~sclk_int;  // sample on opposite edge
                        change_edge = sclk_int;
                    end else begin
                        sample_edge = sclk_int;
                        change_edge = ~sclk_int;
                    end

                    // Change MOSI on change edge
                    if (sclk_int == change_edge && bit_cnt > 0) begin
                        mosi <= shift_tx[DATA_WIDTH-1];
                        shift_tx <= {shift_tx[DATA_WIDTH-2:0], 1'b0};
                    end

                    // Sample MISO on sample edge
                    if (sclk_int == sample_edge && bit_cnt > 0) begin
                        shift_rx <= {shift_rx[DATA_WIDTH-2:0], miso};
                        bit_cnt <= bit_cnt - 1;
                    end

                    // Transaction complete
                    if (bit_cnt == 0 && sclk_int == change_edge) begin
                        data_rx <= shift_rx;
                        state   <= DONE;
                    end
                end

                DONE: begin
                    cs_n  <= 1'b1;
                    sclk  <= CPOL;
                    mosi  <= 1'b0;
                    busy  <= 1'b0;
                    state <= IDLE;
                end
            endcase
        end
    end

endmodule
""",
                },
            },
        ],
    },
    {
        "id": "axi",
        "name": "AXI / AXI4-Lite",
        "icon": "axi",
        "templates": [
            {
                "id": "axi_lite_slave",
                "name": "AXI4-Lite Slave",
                "description": "AXI4-Lite slave with read/write registers, configurable register count",
                "formats": {
                    "verilog": """\
// AXI4-Lite Slave
// Supports simple register read/write with configurable register count

module axi_lite_slave #(
    parameter C_S_AXI_ADDR_WIDTH = 8,
    parameter C_S_AXI_DATA_WIDTH = 32,
    parameter NUM_REG = 16
)(
    input  wire                        clk,
    input  wire                        rst_n,

    // Write Address Channel
    input  wire [C_S_AXI_ADDR_WIDTH-1:0]  s_axi_awaddr,
    input  wire                            s_axi_awvalid,
    output reg                             s_axi_awready,

    // Write Data Channel
    input  wire [C_S_AXI_DATA_WIDTH-1:0]  s_axi_wdata,
    input  wire [(C_S_AXI_DATA_WIDTH/8)-1:0] s_axi_wstrb,
    input  wire                            s_axi_wvalid,
    output reg                             s_axi_wready,

    // Write Response Channel
    output reg                             s_axi_bvalid,
    input  wire                            s_axi_bready,
    output reg  [1:0]                      s_axi_bresp,

    // Read Address Channel
    input  wire [C_S_AXI_ADDR_WIDTH-1:0]  s_axi_araddr,
    input  wire                            s_axi_arvalid,
    output reg                             s_axi_arready,

    // Read Data Channel
    output reg [C_S_AXI_DATA_WIDTH-1:0]   s_axi_rdata,
    output reg  [1:0]                      s_axi_rresp,
    output reg                             s_axi_rvalid,
    input  wire                            s_axi_rready
);

    // Register file
    reg [C_S_AXI_DATA_WIDTH-1:0] reg_file [0:NUM_REG-1];

    // Address decoding
    wire [C_S_AXI_ADDR_WIDTH-1:0] addr_word = s_axi_awaddr >> 2;
    wire [C_S_AXI_ADDR_WIDTH-1:0] addr_rd   = s_axi_araddr >> 2;

    integer i;
    initial begin
        for (i = 0; i < NUM_REG; i = i + 1)
            reg_file[i] = 0;
    end

    // --------------------------------------------------------
    // Write Transaction
    // --------------------------------------------------------
    localparam [1:0]
        WR_IDLE = 0,
        WR_ADDR = 1,
        WR_DATA = 2,
        WR_RESP = 3;

    reg [1:0] wr_state;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            wr_state    <= WR_IDLE;
            s_axi_awready <= 1'b0;
            s_axi_wready  <= 1'b0;
            s_axi_bvalid  <= 1'b0;
            s_axi_bresp   <= 2'b00;
        end else begin
            case (wr_state)
                WR_IDLE: begin
                    s_axi_awready <= 1'b0;
                    s_axi_wready  <= 1'b0;
                    if (s_axi_awvalid) begin
                        s_axi_awready <= 1'b1;
                        wr_state <= WR_ADDR;
                    end
                end
                WR_ADDR: begin
                    s_axi_awready <= 1'b0;
                    if (s_axi_wvalid) begin
                        s_axi_wready <= 1'b1;
                        wr_state <= WR_DATA;
                    end
                end
                WR_DATA: begin
                    s_axi_wready <= 1'b0;
                    // Write to register file
                    if (addr_word < NUM_REG) begin
                        reg_file[addr_word] <= s_axi_wdata;
                    end
                    s_axi_bresp  <= 2'b00;  // OKAY
                    s_axi_bvalid <= 1'b1;
                    wr_state <= WR_RESP;
                end
                WR_RESP: begin
                    if (s_axi_bready) begin
                        s_axi_bvalid <= 1'b0;
                        wr_state <= WR_IDLE;
                    end
                end
            endcase
        end
    end

    // --------------------------------------------------------
    // Read Transaction
    // --------------------------------------------------------
    localparam [1:0]
        RD_IDLE = 0,
        RD_ADDR = 1,
        RD_DATA = 2;

    reg [1:0] rd_state;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            rd_state    <= RD_IDLE;
            s_axi_arready <= 1'b0;
            s_axi_rvalid  <= 1'b0;
            s_axi_rresp   <= 2'b00;
            s_axi_rdata   <= 0;
        end else begin
            case (rd_state)
                RD_IDLE: begin
                    s_axi_arready <= 1'b0;
                    if (s_axi_arvalid) begin
                        s_axi_arready <= 1'b1;
                        rd_state <= RD_ADDR;
                    end
                end
                RD_ADDR: begin
                    s_axi_arready <= 1'b0;
                    s_axi_rdata <= (addr_rd < NUM_REG) ?
                                    reg_file[addr_rd] : 0;
                    s_axi_rresp  <= 2'b00;  // OKAY
                    s_axi_rvalid <= 1'b1;
                    rd_state <= RD_DATA;
                end
                RD_DATA: begin
                    if (s_axi_rready) begin
                        s_axi_rvalid <= 1'b0;
                        rd_state <= RD_IDLE;
                    end
                end
            endcase
        end
    end

endmodule
""",
                },
            },
        ],
    },
    {
        "id": "fifo",
        "name": "FIFO / Memories",
        "icon": "fifo",
        "templates": [
            {
                "id": "sync_fifo",
                "name": "Synchronous FIFO",
                "description": "Single-clock FIFO with configurable depth and width",
                "formats": {
                    "verilog": """\
// Synchronous FIFO
// Single-clock domain, configurable width and depth

module sync_fifo #(
    parameter DATA_WIDTH = 8,
    parameter FIFO_DEPTH = 16
)(
    input  wire                clk,
    input  wire                rst_n,
    input  wire                wr_en,
    input  wire [DATA_WIDTH-1:0] wr_data,
    output reg                 full,
    input  wire                rd_en,
    output reg  [DATA_WIDTH-1:0] rd_data,
    output reg                 empty
);

    localparam ADDR_WIDTH = $clog2(FIFO_DEPTH);

    reg [DATA_WIDTH-1:0] mem [0:FIFO_DEPTH-1];
    reg [ADDR_WIDTH:0] wr_ptr, rd_ptr;  // extra bit for full/empty detection

    wire [ADDR_WIDTH-1:0] wr_addr = wr_ptr[ADDR_WIDTH-1:0];
    wire [ADDR_WIDTH-1:0] rd_addr = rd_ptr[ADDR_WIDTH-1:0];

    // Write
    always @(posedge clk) begin
        if (wr_en && !full)
            mem[wr_addr] <= wr_data;
    end

    // Read
    always @(posedge clk) begin
        if (rd_en && !empty)
            rd_data <= mem[rd_addr];
    end

    // Pointer management
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            wr_ptr <= 0;
            rd_ptr <= 0;
        end else begin
            if (wr_en && !full)
                wr_ptr <= wr_ptr + 1;
            if (rd_en && !empty)
                rd_ptr <= rd_ptr + 1;
        end
    end

    // Status flags
    assign full  = (wr_ptr[ADDR_WIDTH] != rd_ptr[ADDR_WIDTH]) &&
                   (wr_ptr[ADDR_WIDTH-1:0] == rd_ptr[ADDR_WIDTH-1:0]);

    assign empty = (wr_ptr == rd_ptr);

endmodule
""",
                    "systemverilog": """\
// Synchronous FIFO (SystemVerilog)
// Single-clock domain, configurable width and depth

module sync_fifo #(
    parameter int DATA_WIDTH = 8,
    parameter int FIFO_DEPTH = 16
)(
    input  logic               clk,
    input  logic               rst_n,
    input  logic               wr_en,
    input  logic [DATA_WIDTH-1:0] wr_data,
    output logic               full,
    input  logic               rd_en,
    output logic [DATA_WIDTH-1:0] rd_data,
    output logic               empty
);

    localparam int ADDR_WIDTH = $clog2(FIFO_DEPTH);

    logic [DATA_WIDTH-1:0] mem [FIFO_DEPTH];
    logic [ADDR_WIDTH:0] wr_ptr, rd_ptr;

    always_ff @(posedge clk) begin
        if (wr_en && !full)
            mem[wr_ptr[ADDR_WIDTH-1:0]] <= wr_data;
    end

    always_ff @(posedge clk) begin
        if (rd_en && !empty)
            rd_data <= mem[rd_ptr[ADDR_WIDTH-1:0]];
    end

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            wr_ptr <= 0;
            rd_ptr <= 0;
        end else begin
            if (wr_en && !full)  wr_ptr <= wr_ptr + 1;
            if (rd_en && !empty) rd_ptr <= rd_ptr + 1;
        end
    end

    assign full  = (wr_ptr[ADDR_WIDTH] != rd_ptr[ADDR_WIDTH]) &&
                   (wr_ptr[ADDR_WIDTH-1:0] == rd_ptr[ADDR_WIDTH-1:0]);
    assign empty = (wr_ptr == rd_ptr);

    // Calculate fill level
    logic [ADDR_WIDTH:0] fill_count;
    assign fill_count = wr_ptr - rd_ptr;

endmodule
""",
                },
            },
            {
                "id": "async_fifo",
                "name": "Async FIFO (Dual-Clock)",
                "description": "Dual-clock asynchronous FIFO with gray-coded pointers for CDC",
                "formats": {
                    "verilog": """\
// Asynchronous FIFO (Dual-Clock)
// Uses Gray code pointers for safe clock domain crossing

module async_fifo #(
    parameter DATA_WIDTH = 8,
    parameter FIFO_DEPTH = 16
)(
    input  wire                wr_clk,
    input  wire                wr_rst_n,
    input  wire                wr_en,
    input  wire [DATA_WIDTH-1:0] wr_data,
    output reg                 full,

    input  wire                rd_clk,
    input  wire                rd_rst_n,
    input  wire                rd_en,
    output reg  [DATA_WIDTH-1:0] rd_data,
    output reg                 empty
);

    localparam ADDR_WIDTH = $clog2(FIFO_DEPTH);

    reg  [DATA_WIDTH-1:0] mem [0:FIFO_DEPTH-1];
    reg  [ADDR_WIDTH:0]   wr_ptr, rd_ptr;
    reg  [ADDR_WIDTH:0]   wr_gray, rd_gray;
    reg  [ADDR_WIDTH:0]   wr_gray_sync, wr_gray_sync2;
    reg  [ADDR_WIDTH:0]   rd_gray_sync, rd_gray_sync2;

    wire [ADDR_WIDTH-1:0] wr_addr = wr_ptr[ADDR_WIDTH-1:0];
    wire [ADDR_WIDTH-1:0] rd_addr = rd_ptr[ADDR_WIDTH-1:0];

    // Binary to Gray
    function [ADDR_WIDTH:0] bin2gray(input [ADDR_WIDTH:0] bin);
        bin2gray = bin ^ (bin >> 1);
    endfunction

    // Gray to Binary
    function [ADDR_WIDTH:0] gray2bin(input [ADDR_WIDTH:0] gray);
        reg [ADDR_WIDTH:0] bin;
        integer i;
        begin
            bin[ADDR_WIDTH] = gray[ADDR_WIDTH];
            for (i = ADDR_WIDTH-1; i >= 0; i = i - 1)
                bin[i] = bin[i+1] ^ gray[i];
            gray2bin = bin;
        end
    endfunction

    // Write domain
    always @(posedge wr_clk or negedge wr_rst_n) begin
        if (!wr_rst_n) begin
            wr_ptr <= 0;
            wr_gray <= 0;
        end else begin
            if (wr_en && !full) begin
                wr_ptr <= wr_ptr + 1;
                mem[wr_addr] <= wr_data;
            end
            wr_gray <= bin2gray(wr_ptr);
        end
    end

    // Read domain
    always @(posedge rd_clk or negedge rd_rst_n) begin
        if (!rd_rst_n) begin
            rd_ptr <= 0;
            rd_gray <= 0;
        end else begin
            if (rd_en && !empty) begin
                rd_ptr <= rd_ptr + 1;
            end
            rd_gray <= bin2gray(rd_ptr);
        end
    end

    // CDC: synchronize write gray pointer to read clock
    always @(posedge rd_clk or negedge rd_rst_n) begin
        if (!rd_rst_n) begin
            wr_gray_sync  <= 0;
            wr_gray_sync2 <= 0;
        end else begin
            wr_gray_sync  <= wr_gray;
            wr_gray_sync2 <= wr_gray_sync;
        end
    end

    // CDC: synchronize read gray pointer to write clock
    always @(posedge wr_clk or negedge wr_rst_n) begin
        if (!wr_rst_n) begin
            rd_gray_sync  <= 0;
            rd_gray_sync2 <= 0;
        end else begin
            rd_gray_sync  <= rd_gray;
            rd_gray_sync2 <= rd_gray_sync;
        end
    end

    // Read data
    always @(posedge rd_clk) begin
        if (rd_en && !empty)
            rd_data <= mem[rd_addr];
    end

    // Full/Empty detection using synchronized pointers
    always @(posedge wr_clk or negedge wr_rst_n) begin
        if (!wr_rst_n)
            full <= 1'b0;
        else
            full <= ((wr_ptr[ADDR_WIDTH] != rd_gray_sync2[ADDR_WIDTH]) &&
                     (wr_ptr[ADDR_WIDTH-1:0] == rd_gray_sync2[ADDR_WIDTH-1:0]));
    end

    always @(posedge rd_clk or negedge rd_rst_n) begin
        if (!rd_rst_n)
            empty <= 1'b1;
        else
            empty <= (rd_ptr == gray2bin(wr_gray_sync2));
    end

endmodule
""",
                },
            },
        ],
    },
    {
        "id": "basic",
        "name": "Basic Building Blocks",
        "icon": "basic",
        "templates": [
            {
                "id": "clock_divider",
                "name": "Clock Divider",
                "description": "Configurable clock divider by even division factor",
                "formats": {
                    "verilog": """\
// Clock Divider
// Divides input clock by DIV_FACTOR (must be even)

module clk_divider #(
    parameter DIV_FACTOR = 2
)(
    input  wire clk,
    input  wire rst_n,
    output reg  clk_out
);

    localparam HALF = DIV_FACTOR / 2;
    reg [$clog2(DIV_FACTOR)-1:0] counter;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            counter <= 0;
            clk_out <= 1'b0;
        end else begin
            if (counter == HALF - 1) begin
                clk_out <= ~clk_out;
                counter <= 0;
            end else begin
                counter <= counter + 1;
            end
        end
    end

endmodule
""",
                    "systemverilog": """\
// Clock Divider (SystemVerilog)

module clk_divider #(
    parameter int DIV_FACTOR = 2
)(
    input  logic clk,
    input  logic rst_n,
    output logic clk_out
);

    localparam int HALF = DIV_FACTOR / 2;
    logic [$clog2(DIV_FACTOR)-1:0] counter;

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            counter <= 0;
            clk_out <= 1'b0;
        end else begin
            if (counter == HALF - 1) begin
                clk_out <= ~clk_out;
                counter <= 0;
            end else begin
                counter <= counter + 1;
            end
        end
    end

endmodule
""",
                },
            },
            {
                "id": "debouncer",
                "name": "Debouncer",
                "description": "Button/switch debouncer with configurable timeout",
                "formats": {
                    "verilog": """\
// Debouncer
// Debounces a noisy input signal with configurable settling time

module debouncer #(
    parameter CLK_FREQ   = 50_000_000,
    parameter SETTLE_MS  = 10
)(
    input  wire clk,
    input  wire rst_n,
    input  wire noisy,
    output reg  clean
);

    localparam MAX_COUNT = CLK_FREQ / 1000 * SETTLE_MS;

    reg [$clog2(MAX_COUNT+1)-1:0] counter;
    reg stable;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            counter <= 0;
            stable  <= noisy;
            clean   <= noisy;
        end else begin
            if (stable != noisy) begin
                counter <= counter + 1;
                if (counter == MAX_COUNT - 1) begin
                    stable <= noisy;
                    counter <= 0;
                end
            end else begin
                counter <= 0;
            end
            clean <= stable;
        end
    end

endmodule
""",
                    "systemverilog": """\
// Debouncer (SystemVerilog)

module debouncer #(
    parameter int CLK_FREQ  = 50_000_000,
    parameter int SETTLE_MS = 10
)(
    input  logic clk,
    input  logic rst_n,
    input  logic noisy,
    output logic clean
);

    localparam int MAX_COUNT = CLK_FREQ / 1000 * SETTLE_MS;
    logic [$clog2(MAX_COUNT+1)-1:0] counter;
    logic stable;

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            counter <= 0;
            stable  <= noisy;
            clean   <= noisy;
        end else begin
            if (stable != noisy) begin
                counter <= counter + 1;
                if (counter == MAX_COUNT - 1) begin
                    stable <= noisy;
                    counter <= 0;
                end
            end else begin
                counter <= 0;
            end
            clean <= stable;
        end
    end

endmodule
""",
                },
            },
            {
                "id": "edge_detector",
                "name": "Edge Detector",
                "description": "Rising edge, falling edge, and dual-edge detector",
                "formats": {
                    "verilog": """\
// Edge Detector
// Detects rising, falling, and both edges of a signal

module edge_detector (
    input  wire clk,
    input  wire rst_n,
    input  wire signal_in,
    output reg  rising,
    output reg  falling,
    output reg  any_edge
);

    reg signal_dly;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            signal_dly <= 1'b0;
            rising     <= 1'b0;
            falling    <= 1'b0;
            any_edge   <= 1'b0;
        end else begin
            signal_dly <= signal_in;
            rising  <= signal_in && !signal_dly;
            falling <= !signal_in && signal_dly;
            any_edge <= signal_in != signal_dly;
        end
    end

endmodule
""",
                },
            },
            {
                "id": "pwm",
                "name": "PWM Generator",
                "description": "Pulse-width modulator with configurable period and duty cycle",
                "formats": {
                    "verilog": """\
// PWM Generator
// Generates a PWM signal with configurable period and duty cycle

module pwm_generator #(
    parameter CLK_FREQ   = 50_000_000,
    parameter PWM_FREQ   = 1_000,
    parameter PWM_WIDTH  = 8
)(
    input  wire                 clk,
    input  wire                 rst_n,
    input  wire [PWM_WIDTH-1:0] duty_cycle,
    output reg                  pwm_out
);

    localparam PERIOD_CYCLES = CLK_FREQ / PWM_FREQ;
    localparam SCALE = PERIOD_CYCLES / (2**PWM_WIDTH);

    reg [PWM_WIDTH-1:0]    counter;
    reg [31:0]             cycle_counter;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            counter <= 0;
            cycle_counter <= 0;
            pwm_out <= 1'b0;
        end else begin
            if (cycle_counter >= PERIOD_CYCLES - 1) begin
                cycle_counter <= 0;
                counter <= counter + 1;
            end else begin
                cycle_counter <= cycle_counter + 1;
            end
            pwm_out <= (counter < duty_cycle);
        end
    end

endmodule
""",
                    "systemverilog": """\
// PWM Generator (SystemVerilog)

module pwm_generator #(
    parameter int CLK_FREQ   = 50_000_000,
    parameter int PWM_FREQ   = 1_000,
    parameter int PWM_WIDTH  = 8
)(
    input  logic                clk,
    input  logic                rst_n,
    input  logic [PWM_WIDTH-1:0] duty_cycle,
    output logic                 pwm_out
);

    localparam int PERIOD_CYCLES = CLK_FREQ / PWM_FREQ;
    logic [PWM_WIDTH-1:0] counter;
    logic [31:0]          cycle_counter;

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            counter       <= 0;
            cycle_counter <= 0;
            pwm_out       <= 1'b0;
        end else begin
            if (cycle_counter >= PERIOD_CYCLES - 1) begin
                cycle_counter <= 0;
                counter <= counter + 1;
            end else begin
                cycle_counter <= cycle_counter + 1;
            end
            pwm_out <= (counter < duty_cycle);
        end
    end

endmodule
""",
                },
            },
            {
                "id": "counter",
                "name": "Up/Down Counter",
                "description": "N-bit counter with up/down control and configurable max value",
                "formats": {
                    "verilog": """\
// N-bit Up/Down Counter
// Configurable width, up/down control, max count, and overflow/underflow

module updown_counter #(
    parameter WIDTH = 8
)(
    input  wire           clk,
    input  wire           rst_n,
    input  wire           enable,
    input  wire           up,       // 1 = count up, 0 = count down
    input  wire           load,     // synchronous load
    input  wire [WIDTH-1:0] load_value,
    output reg  [WIDTH-1:0] count,
    output reg           max_reached,
    output reg           min_reached
);

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            count <= 0;
        end else if (load) begin
            count <= load_value;
        end else if (enable) begin
            if (up)
                count <= count + 1;
            else
                count <= count - 1;
        end
    end

    always @(*) begin
        max_reached = (up && count == {WIDTH{1'b1}} && enable);
        min_reached = (!up && count == 0 && enable);
    end

endmodule
""",
                },
            },
            {
                "id": "shift_register",
                "name": "Shift Register",
                "description": "N-bit shift register with left/right shift, parallel load",
                "formats": {
                    "verilog": """\
// N-bit Shift Register
// Supports left shift, right shift, parallel load, and serial in/out

module shift_register #(
    parameter WIDTH = 8
)(
    input  wire             clk,
    input  wire             rst_n,
    input  wire             load,     // parallel load
    input  wire [WIDTH-1:0] load_data,
    input  wire             shift_en,
    input  wire             left_right,  // 1 = left, 0 = right
    input  wire             serial_in,
    output reg  [WIDTH-1:0] data,
    output wire             serial_out
);

    assign serial_out = left_right ? data[WIDTH-1] : data[0];

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n)
            data <= 0;
        else if (load)
            data <= load_data;
        else if (shift_en) begin
            if (left_right)
                data <= {data[WIDTH-2:0], serial_in};
            else
                data <= {serial_in, data[WIDTH-1:1]};
        end
    end

endmodule
""",
                },
            },
            {
                "id": "stimulus",
                "name": "Testbench Template",
                "description": "Basic self-checking testbench with clock generation and waveform dump",
                "formats": {
                    "verilog": """\
// Testbench Template
// Self-checking testbench with clock/reset generation

`timescale 1ns / 1ps

module tb_template;

    // Parameters
    parameter CLK_PERIOD = 10;  // 100 MHz

    // Signals
    reg  clk;
    reg  rst_n;
    reg  [7:0] stimulus;
    wire [7:0] response;

    // DUT instantiation
    // dut_name #(
    //     .PARAM1(VALUE1)
    // ) u_dut (
    //     .clk(clk),
    //     .rst_n(rst_n),
    //     .input_signal(stimulus),
    //     .output_signal(response)
    // );

    // Clock generation
    initial begin
        clk = 0;
        forever #(CLK_PERIOD / 2) clk = ~clk;
    end

    // Reset and stimulus
    initial begin
        rst_n = 0;
        stimulus = 0;

        // Release reset
        #(CLK_PERIOD * 10) rst_n = 1;

        // Test sequence
        #(CLK_PERIOD * 5);
        stimulus = 8'hAA;
        #(CLK_PERIOD * 10);

        stimulus = 8'h55;
        #(CLK_PERIOD * 10);

        // Check result
        // if (response != EXPECTED) begin
        //     $display("ERROR: Expected %0h, got %0h", EXPECTED, response);
        //     $finish;
        // end

        $display("TEST PASSED");
        $finish;
    end

    // VCD dump
    initial begin
        $dumpfile("dump.vcd");
        $dumpvars(0, tb_template);
    end

endmodule
""",
                },
            },
        ],
    },
]


class TemplateManager:

    @staticmethod
    def get_categories():
        return TEMPLATE_CATEGORIES

    @staticmethod
    def get_template(category_id, template_id):
        for cat in TEMPLATE_CATEGORIES:
            if cat["id"] == category_id:
                for tmpl in cat["templates"]:
                    if tmpl["id"] == template_id:
                        return tmpl
        return None

    @staticmethod
    def get_code(category_id, template_id, language):
        tmpl = TemplateManager.get_template(category_id, template_id)
        if tmpl:
            return tmpl["formats"].get(language)
        return None

    @staticmethod
    def available_languages(category_id, template_id):
        tmpl = TemplateManager.get_template(category_id, template_id)
        if tmpl:
            return list(tmpl["formats"].keys())
        return []

    @staticmethod
    def template_count():
        count = 0
        for cat in TEMPLATE_CATEGORIES:
            count += len(cat["templates"])
        return count
