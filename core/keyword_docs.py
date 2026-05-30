# Built-in HDL keyword documentation for the hover tooltip system.
# Each entry: keyword -> (kind, description, url)


VERILOG_DOCS = {

    # --- Module structure ---
    "module": ("keyword",
        "Module declaration. Defines a hardware block with ports.\n"
        "  module name ( port_list );\n"
        "    ... body ...\n"
        "  endmodule",
        "https://www.chipverify.com/verilog/verilog-module"),

    "endmodule": ("keyword",
        "Ends a module declaration.",
        "https://www.chipverify.com/verilog/verilog-module"),

    "input": ("keyword",
        "Declares a port as input (driven from outside the module).",
        "https://www.chipverify.com/verilog/verilog-port"),

    "output": ("keyword",
        "Declares a port as output (driven from inside the module).",
        "https://www.chipverify.com/verilog/verilog-port"),

    "inout": ("keyword",
        "Declares a bidirectional port.",
        "https://www.chipverify.com/verilog/verilog-port"),

    # --- Data types ---
    "wire": ("keyword",
        "Net type — continuous driver (assign, port connection).\n"
        "  wire [width] name;",
        "https://www.chipverify.com/verilog/verilog-wire"),

    "reg": ("keyword",
        "Variable type — stores a value across time.\n"
        "  reg [width] name;\n"
        "Assigned inside always/initial blocks.",
        "https://www.chipverify.com/verilog/verilog-reg"),

    "logic": ("keyword",
        "SystemVerilog — replaces both wire and reg.\n"
        "  logic [width] name;",
        "https://www.chipverify.com/systemverilog/systemverilog-logic"),

    "integer": ("keyword",
        "32-bit signed integer variable.\n"
        "  integer name;",
        "https://www.chipverify.com/verilog/verilog-integer"),

    "real": ("keyword",
        "Double-precision floating-point variable.",
        "https://www.chipverify.com/verilog/verilog-real"),

    "time": ("keyword",
        "64-bit unsigned integer for simulation time storage.\n"
        "  time name;",
        "https://www.chipverify.com/verilog/verilog-time"),

    # --- Continuous assignment ---
    "assign": ("keyword",
        "Continuous assignment — drives a wire/net.\n"
        "  assign wire_name = expression;\n"
        "Re-evaluated whenever RHS changes.",
        "https://www.chipverify.com/verilog/verilog-assign"),

    # --- Procedural blocks ---
    "always": ("keyword",
        "Procedural block that repeats forever.\n"
        "  always @(posedge clk) begin ... end\n"
        "Sensitive to the sensitivity list.",
        "https://www.chipverify.com/verilog/verilog-always-block"),

    "always_comb": ("keyword",
        "SystemVerilog — always combinational logic.\n"
        "Automatically sensitive to all variables read.",
        "https://www.chipverify.com/systemverilog/systemverilog-always-comb"),

    "always_ff": ("keyword",
        "SystemVerilog — always flip-flop logic.\n"
        "  always_ff @(posedge clk) begin ... end",
        "https://www.chipverify.com/systemverilog/systemverilog-always-ff"),

    "always_latch": ("keyword",
        "SystemVerilog — always latch inference.\n"
        "  always_latch begin ... end",
        "https://www.chipverify.com/systemverilog/systemverilog-always-latch"),

    "initial": ("keyword",
        "Procedural block that runs once at time 0.\n"
        "  initial begin ... end\n"
        "Used for testbench stimulus.",
        "https://www.chipverify.com/verilog/verilog-initial-block"),

    # --- Control flow ---
    "if": ("keyword",
        "Conditional statement.\n"
        "  if (condition) begin ... end\n"
        "  else begin ... end",
        "https://www.chipverify.com/verilog/verilog-if-else"),

    "else": ("keyword",
        "Alternative branch for if statement.",
        "https://www.chipverify.com/verilog/verilog-if-else"),

    "case": ("keyword",
        "Multi-way branch statement.\n"
        "  case (expr)\n"
        "    value1: statement;\n"
        "    default: statement;\n"
        "  endcase",
        "https://www.chipverify.com/verilog/verilog-case-statement"),

    "casex": ("keyword",
        "Case with don't-care (X/Z) matching.",
        "https://www.chipverify.com/verilog/verilog-casex-casez"),

    "casez": ("keyword",
        "Case with high-impedance (Z) matching.",
        "https://www.chipverify.com/verilog/verilog-casex-casez"),

    "for": ("keyword",
        "Loop statement (synthesizable with constant bounds).\n"
        "  for (i = 0; i < N; i = i + 1) begin ... end",
        "https://www.chipverify.com/verilog/verilog-for-loop"),

    "while": ("keyword",
        "Loop statement (simulation only).\n"
        "  while (condition) begin ... end",
        "https://www.chipverify.com/verilog/verilog-while-loop"),

    "repeat": ("keyword",
        "Fixed-repetition loop.\n"
        "  repeat (count) begin ... end",
        "https://www.chipverify.com/verilog/verilog-repeat-loop"),

    "forever": ("keyword",
        "Infinite loop (simulation only).\n"
        "  forever begin ... end",
        "https://www.chipverify.com/verilog/verilog-forever-loop"),

    # --- Block delimiters ---
    "begin": ("keyword",
        "Start of a named or unnamed sequential block.\n"
        "  begin : block_name\n"
        "    ...\n"
        "  end",
        "https://www.chipverify.com/verilog/verilog-begin-end"),

    "end": ("keyword",
        "End of a sequential block.",
        "https://www.chipverify.com/verilog/verilog-begin-end"),

    "fork": ("keyword",
        "Start of a parallel block.\n"
        "  fork\n"
        "    ...\n"
        "  join / join_any / join_none",
        "https://www.chipverify.com/verilog/verilog-fork-join"),

    "join": ("keyword",
        "End of parallel block — waits for all threads.",
        "https://www.chipverify.com/verilog/verilog-fork-join"),

    "join_any": ("keyword",
        "End of parallel block — continues when any one thread finishes.",
        "https://www.chipverify.com/verilog/verilog-fork-join"),

    "join_none": ("keyword",
        "End of parallel block — continues immediately without waiting.",
        "https://www.chipverify.com/verilog/verilog-fork-join"),

    # --- Events ---
    "posedge": ("keyword",
        "Positive (rising) edge trigger.\n"
        "  @(posedge clk)",
        "https://www.chipverify.com/verilog/verilog-always-block"),

    "negedge": ("keyword",
        "Negative (falling) edge trigger.\n"
        "  @(negedge clk)",
        "https://www.chipverify.com/verilog/verilog-always-block"),

    "edge": ("keyword",
        "SystemVerilog — both-edge trigger.\n"
        "  @(edge clk)",
        "https://www.chipverify.com/systemverilog/systemverilog-always-ff"),

    # --- Parameters ---
    "parameter": ("keyword",
        "Module parameter — compile-time constant.\n"
        "  parameter WIDTH = 8;",
        "https://www.chipverify.com/verilog/verilog-parameters"),

    "localparam": ("keyword",
        "Local parameter — not overridable at instantiation.\n"
        "  localparam WIDTH = 8;",
        "https://www.chipverify.com/verilog/verilog-parameters"),

    # --- Generate ---
    "generate": ("keyword",
        "Generates multiple instances or logic at compile time.\n"
        "  generate ... endgenerate",
        "https://www.chipverify.com/verilog/verilog-generate-block"),

    "endgenerate": ("keyword",
        "End of generate block.",
        "https://www.chipverify.com/verilog/verilog-generate-block"),

    "genvar": ("keyword",
        "Generate loop variable (integer used in generate for loops).\n"
        "  genvar i;\n"
        "  generate for (i = 0; i < N; i++) ...",
        "https://www.chipverify.com/verilog/verilog-generate-block"),

    # --- Functions and tasks ---
    "function": ("keyword",
        "Function — returns a value, no timing controls.\n"
        "  function [width] name;\n"
        "    input ...;\n"
        "    begin ... end\n"
        "  endfunction",
        "https://www.chipverify.com/verilog/verilog-function"),

    "endfunction": ("keyword",
        "Ends a function definition.",
        "https://www.chipverify.com/verilog/verilog-function"),

    "task": ("keyword",
        "Task — can have timing controls, no return value.\n"
        "  task name;\n"
        "    input ...;\n"
        "    begin ... end\n"
        "  endtask",
        "https://www.chipverify.com/verilog/verilog-task"),

    "endtask": ("keyword",
        "Ends a task definition.",
        "https://www.chipverify.com/verilog/verilog-task"),

    "return": ("keyword",
        "Exits a function/task and optionally returns a value.",
        "https://www.chipverify.com/verilog/verilog-function"),

    # --- I/O system functions ---
    "$display": ("sysfunc",
        "Prints formatted text to the simulation console.\n"
        "  $display(\"fmt\", args);\n"
        "  $display(\"a=%0d\", a);\n"
        "Adds a newline automatically.",
        "https://www.chipverify.com/verilog/verilog-display"),

    "$write": ("sysfunc",
        "Prints formatted text WITHOUT a newline.",
        "https://www.chipverify.com/verilog/verilog-display"),

    "$monitor": ("sysfunc",
        "Prints a message whenever any listed variable changes.\n"
        "  $monitor(\"fmt\", args);",
        "https://www.chipverify.com/verilog/verilog-display"),

    "$monitoron": ("sysfunc",
        "Enables monitoring (on by default).",
        "https://www.chipverify.com/verilog/verilog-display"),

    "$monitoroff": ("sysfunc",
        "Disables monitoring.",
        "https://www.chipverify.com/verilog/verilog-display"),

    "$strobe": ("sysfunc",
        "Prints at the end of the current time step.\n"
        "  $strobe(\"fmt\", args);",
        "https://www.chipverify.com/verilog/verilog-display"),

    # --- Waveform dump system functions ---
    "$dumpfile": ("sysfunc",
        "Specifies the VCD waveform dump file.\n"
        "  $dumpfile(\"dump.vcd\");\n"
        "Must be called before $dumpvars.",
        "https://www.chipverify.com/verilog/verilog-dump"),

    "$dumpvars": ("sysfunc",
        "Enables waveform dumping for specified signals.\n"
        "  $dumpvars;                  // all signals\n"
        "  $dumpvars(0, top);          // top and all below\n"
        "  $dumpvars(1, top.u_sig);    // just that signal",
        "https://www.chipverify.com/verilog/verilog-dump"),

    "$dumpoff": ("sysfunc",
        "Suspends waveform dumping.",
        "https://www.chipverify.com/verilog/verilog-dump"),

    "$dumpon": ("sysfunc",
        "Resumes waveform dumping.",
        "https://www.chipverify.com/verilog/verilog-dump"),

    "$dumpall": ("sysfunc",
        "Dumps a snapshot of all dumped variables.",
        "https://www.chipverify.com/verilog/verilog-dump"),

    "$dumplimit": ("sysfunc",
        "Sets the maximum VCD file size.",
        "https://www.chipverify.com/verilog/verilog-dump"),

    # --- Simulation control ---
    "$stop": ("sysfunc",
        "Stops the simulation and enters interactive mode.",
        "https://www.chipverify.com/verilog/verilog-stop-finish"),

    "$finish": ("sysfunc",
        "Ends the simulation and exits the simulator.",
        "https://www.chipverify.com/verilog/verilog-stop-finish"),

    "$time": ("sysfunc",
        "Returns current simulation time as a 64-bit integer.\n"
        "  t = $time;",
        "https://www.chipverify.com/verilog/verilog-time"),

    "$realtime": ("sysfunc",
        "Returns current simulation time as a real number."
        "https://www.chipverify.com/verilog/verilog-time"),

    # --- Randomization ---
    "$random": ("sysfunc",
        "Returns a random 32-bit integer.\n"
        "  r = $random;        // basic\n"
        "  r = $random(seed);  // seeded",
        "https://www.chipverify.com/verilog/verilog-random"),

    # --- File I/O ---
    "$readmemh": ("sysfunc",
        "Reads hex-format file into memory array.\n"
        "  $readmemh(\"file.hex\", mem);",
        "https://www.chipverify.com/verilog/verilog-readmemh"),

    "$readmemb": ("sysfunc",
        "Reads binary-format file into memory array.\n"
        "  $readmemb(\"file.bin\", mem);",
        "https://www.chipverify.com/verilog/verilog-readmemb"),

    "$writememh": ("sysfunc",
        "Writes memory array to hex-format file."
        "https://www.chipverify.com/verilog/verilog-writememh"),

    "$writememb": ("sysfunc",
        "Writes memory array to binary-format file."
        "https://www.chipverify.com/verilog/verilog-writememb"),

    "$fopen": ("sysfunc",
        "Opens a file for reading/writing.\n"
        "  fd = $fopen(\"file.txt\", \"r\");",
        "https://www.chipverify.com/verilog/verilog-file-operations"),

    "$fclose": ("sysfunc",
        "Closes an open file descriptor.\n"
        "  $fclose(fd);",
        "https://www.chipverify.com/verilog/verilog-file-operations"),

    "$fdisplay": ("sysfunc",
        "Writes formatted text to a file.\n"
        "  $fdisplay(fd, \"fmt\", args);",
        "https://www.chipverify.com/verilog/verilog-file-operations"),

    "$fwrite": ("sysfunc",
        "Writes formatted text to a file without newline.",
        "https://www.chipverify.com/verilog/verilog-file-operations"),

    "$fread": ("sysfunc",
        "Reads binary data from a file into a variable.",
        "https://www.chipverify.com/verilog/verilog-file-operations"),

    "$fscanf": ("sysfunc",
        "Reads formatted text from a file.",
        "https://www.chipverify.com/verilog/verilog-file-operations"),

    # --- Compiler directives ---
    "`define": ("directive",
        "Text macro definition.\n"
        "  `define WIDTH 8\n"
        "  `define ADD(a,b) a+b\n"
        "Use with backtick: `WIDTH, `ADD(x,y)",
        "https://www.chipverify.com/verilog/verilog-macros"),

    "`include": ("directive",
        "Includes another source file.\n"
        "  `include \"file.v\"",
        "https://www.chipverify.com/verilog/verilog-include"),

    "`ifdef": ("directive",
        "Conditional compilation — if macro defined.\n"
        "  `ifdef MACRO\n"
        "    ...\n"
        "  `elsif OTHER\n"
        "    ...\n"
        "  `else\n"
        "    ...\n"
        "  `endif",
        "https://www.chipverify.com/verilog/verilog-ifdef"),

    "`ifndef": ("directive",
        "Conditional compilation — if macro NOT defined.",
        "https://www.chipverify.com/verilog/verilog-ifdef"),

    "`else": ("directive",
        "Alternative branch in conditional compilation.",
        "https://www.chipverify.com/verilog/verilog-ifdef"),

    "`elsif": ("directive",
        "Else-if branch in conditional compilation.",
        "https://www.chipverify.com/verilog/verilog-ifdef"),

    "`endif": ("directive",
        "End of conditional compilation block.",
        "https://www.chipverify.com/verilog/verilog-ifdef"),

    "`timescale": ("directive",
        "Specifies time unit and precision.\n"
        "  `timescale 1ns / 1ps\n"
        "Unit / precision (time unit, time precision).",
        "https://www.chipverify.com/verilog/verilog-timescale"),

    "`default_nettype": ("directive",
        "Sets default net type for undeclared identifiers.\n"
        "  `default_nettype none  // require explicit declarations",
        "https://www.chipverify.com/verilog/verilog-default-nettype"),

    # --- Other ---
    "automatic": ("keyword",
        "Makes a function/task re-entrant (each call has its own stack).\n"
        "  function automatic ...",
        "https://www.chipverify.com/verilog/verilog-function"),

    "signed": ("keyword",
        "Declares a port or net as signed (two's complement).\n"
        "  wire signed [7:0] data;",
        "https://www.chipverify.com/verilog/verilog-signed"),

    "unsigned": ("keyword",
        "Declares a net/variable as unsigned (default).",
        "https://www.chipverify.com/verilog/verilog-signed"),

    "supply0": ("keyword",
        "Net type — constant supply 0 (ground).",
        "https://www.chipverify.com/verilog/verilog-net-types"),

    "supply1": ("keyword",
        "Net type — constant supply 1 (VDD/VCC).",
        "https://www.chipverify.com/verilog/verilog-net-types"),

    "tri": ("keyword",
        "Net type — three-state net (same as wire).",
        "https://www.chipverify.com/verilog/verilog-net-types"),

    "wand": ("keyword",
        "Net type — wired-AND (multiple drivers).",
        "https://www.chipverify.com/verilog/verilog-net-types"),

    "wor": ("keyword",
        "Net type — wired-OR (multiple drivers).",
        "https://www.chipverify.com/verilog/verilog-net-types"),
}


VHDL_DOCS = {

    # --- Structure ---
    "entity": ("keyword",
        "Declares an entity — the interface of a design unit.\n"
        "  entity name is\n"
        "    port ( ... );\n"
        "  end entity;",
        "https://www.chipverify.com/vhdl/vhdl-entity"),

    "architecture": ("keyword",
        "Declares the body/implementation of an entity.\n"
        "  architecture rtl of entity_name is\n"
        "    ... declarations ...\n"
        "  begin\n"
        "    ... concurrent statements ...\n"
        "  end architecture;",
        "https://www.chipverify.com/vhdl/vhdl-architecture"),

    "configuration": ("keyword",
        "Binds a component instance to a specific architecture.",
        "https://www.chipverify.com/vhdl/vhdl-configuration"),

    "package": ("keyword",
        "Declares a package — shared types, constants, functions.\n"
        "  package name is\n"
        "    ... declarations ...\n"
        "  end package;",
        "https://www.chipverify.com/vhdl/vhdl-package"),

    "package body": ("keyword",
        "Body of a package — implements functions/procedures.",
        "https://www.chipverify.com/vhdl/vhdl-package"),

    "library": ("keyword",
        "Makes a library visible.\n"
        "  library ieee;\n"
        "  use ieee.std_logic_1164.all;",
        "https://www.chipverify.com/vhdl/vhdl-library"),

    "use": ("keyword",
        "Makes library items visible.\n"
        "  use ieee.std_logic_1164.all;",
        "https://www.chipverify.com/vhdl/vhdl-library"),

    # --- Port / Signal ---
    "port": ("keyword",
        "Declares entity ports (inputs/outputs).\n"
        "  port (\n"
        "    clk : in  std_logic;\n"
        "    q   : out std_logic\n"
        "  );",
        "https://www.chipverify.com/vhdl/vhdl-port"),

    "signal": ("keyword",
        "Declares an internal signal.\n"
        "  signal name : std_logic_vector(7 downto 0);",
        "https://www.chipverify.com/vhdl/vhdl-signal"),

    "variable": ("keyword",
        "Declares a local variable in a process or function.\n"
        "  variable name : integer := 0;",
        "https://www.chipverify.com/vhdl/vhdl-variable"),

    "constant": ("keyword",
        "Declares a constant.\n"
        "  constant WIDTH : integer := 8;",
        "https://www.chipverify.com/vhdl/vhdl-constant"),

    "in": ("keyword",
        "Port direction — input.",
        "https://www.chipverify.com/vhdl/vhdl-port"),

    "out": ("keyword",
        "Port direction — output.",
        "https://www.chipverify.com/vhdl/vhdl-port"),

    "inout": ("keyword",
        "Port direction — bidirectional.",
        "https://www.chipverify.com/vhdl/vhdl-port"),

    "buffer": ("keyword",
        "Port direction — output that can be read internally.",
        "https://www.chipverify.com/vhdl/vhdl-port"),

    # --- Types ---
    "std_logic": ("type",
        "Standard logic type ('0', '1', 'Z', 'X', etc.).\n"
        "  signal s : std_logic;",
        "https://www.chipverify.com/vhdl/vhdl-std-logic"),

    "std_logic_vector": ("type",
        "Array of std_logic elements.\n"
        "  signal bus : std_logic_vector(7 downto 0);",
        "https://www.chipverify.com/vhdl/vhdl-std-logic-vector"),

    "std_ulogic": ("type",
        "Unresolved logic type (no multiple drivers allowed).",
        "https://www.chipverify.com/vhdl/vhdl-std-ulogic"),

    "std_ulogic_vector": ("type",
        "Array of std_ulogic elements.",
        "https://www.chipverify.com/vhdl/vhdl-std-ulogic-vector"),

    "signed": ("type",
        "Signed arithmetic type (from ieee.numeric_std).\n"
        "  signal s : signed(7 downto 0);",
        "https://www.chipverify.com/vhdl/vhdl-signed-unsigned"),

    "unsigned": ("type",
        "Unsigned arithmetic type (from ieee.numeric_std).",
        "https://www.chipverify.com/vhdl/vhdl-signed-unsigned"),

    "bit": ("type",
        "Two-value logic type ('0', '1').",
        "https://www.chipverify.com/vhdl/vhdl-bit"),

    "bit_vector": ("type",
        "Array of bit elements.",
        "https://www.chipverify.com/vhdl/vhdl-bit-vector"),

    "boolean": ("type",
        "TRUE / FALSE type.",
        "https://www.chipverify.com/vhdl/vhdl-boolean"),

    "integer": ("type",
        "32-bit integer type.\n"
        "  variable i : integer range 0 to 255;",
        "https://www.chipverify.com/vhdl/vhdl-integer"),

    "natural": ("type",
        "Non-negative integer (0 to +inf).",
        "https://www.chipverify.com/vhdl/vhdl-integer"),

    "positive": ("type",
        "Positive integer (1 to +inf).",
        "https://www.chipverify.com/vhdl/vhdl-integer"),

    "real": ("type",
        "Floating-point type (synthesis limited).",
        "https://www.chipverify.com/vhdl/vhdl-real"),

    "time": ("type",
        "Time type for simulation delays.\n"
        "  constant t : time := 10 ns;",
        "https://www.chipverify.com/vhdl/vhdl-time"),

    # --- Statements ---
    "process": ("keyword",
        "Sequential block inside architecture.\n"
        "  process (clk, rst) is\n"
        "  begin\n"
        "    if rising_edge(clk) then ...\n"
        "  end process;",
        "https://www.chipverify.com/vhdl/vhdl-process"),

    "if": ("keyword",
        "Conditional statement.\n"
        "  if condition then\n"
        "    ...\n"
        "  elsif condition then\n"
        "    ...\n"
        "  else\n"
        "    ...\n"
        "  end if;",
        "https://www.chipverify.com/vhdl/vhdl-if"),

    "else": ("keyword",
        "Alternative branch in if statement.",
        "https://www.chipverify.com/vhdl/vhdl-if"),

    "elsif": ("keyword",
        "Additional condition branch in if statement.",
        "https://www.chipverify.com/vhdl/vhdl-if"),

    "when": ("keyword",
        "Used in when-else and with-select concurrent assignments.\n"
        "  q <= '1' when sel = '1' else '0';",
        "https://www.chipverify.com/vhdl/vhdl-when-else"),

    "case": ("keyword",
        "Multi-way branch inside process.\n"
        "  case expr is\n"
        "    when value => statement;\n"
        "    when others => statement;\n"
        "  end case;",
        "https://www.chipverify.com/vhdl/vhdl-case"),

    "for": ("keyword",
        "Loop statement.\n"
        "  for i in 0 to 7 loop\n"
        "    ...\n"
        "  end loop;",
        "https://www.chipverify.com/vhdl/vhdl-for-loop"),

    "while": ("keyword",
        "Conditional loop (simulation only).\n"
        "  while condition loop\n"
        "    ...\n"
        "  end loop;",
        "https://www.chipverify.com/vhdl/vhdl-while-loop"),

    "loop": ("keyword",
        "Loop body delimiter.",
        "https://www.chipverify.com/vhdl/vhdl-loop"),

    "end": ("keyword",
        "Terminates a block (process, if, loop, case, etc.).",
        "https://www.chipverify.com/vhdl/vhdl-process"),

    "null": ("keyword",
        "No-operation statement.\n"
        "  when others => null;",
        "https://www.chipverify.com/vhdl/vhdl-null"),

    "assert": ("keyword",
        "Checks a condition during simulation.\n"
        "  assert condition report \"msg\" severity failure;",
        "https://www.chipverify.com/vhdl/vhdl-assert"),

    "report": ("keyword",
        "Prints a message during simulation.\n"
        "  report \"message\";",
        "https://www.chipverify.com/vhdl/vhdl-report"),

    # --- Generate ---
    "generate": ("keyword",
        "Compile-time generation of hardware.\n"
        "  gen: for i in 0 to 7 generate\n"
        "    ...\n"
        "  end generate;",
        "https://www.chipverify.com/vhdl/vhdl-generate"),

    "component": ("keyword",
        "Declares a component for instantiation.\n"
        "  component adder is\n"
        "    port ( a, b : in std_logic; ... );\n"
        "  end component;",
        "https://www.chipverify.com/vhdl/vhdl-component"),

    # --- Functions ---
    "rising_edge": ("function",
        "Returns TRUE on rising edge (0->1 transition).\n"
        "  if rising_edge(clk) then",
        "https://www.chipverify.com/vhdl/vhdl-rising-edge"),

    "falling_edge": ("function",
        "Returns TRUE on falling edge (1->0 transition).\n"
        "  if falling_edge(clk) then",
        "https://www.chipverify.com/vhdl/vhdl-falling-edge"),

    "to_integer": ("function",
        "Converts signed/unsigned to integer.\n"
        "  i := to_integer(signed_val);",
        "https://www.chipverify.com/vhdl/vhdl-numeric-std"),

    "to_unsigned": ("function",
        "Converts integer to unsigned.\n"
        "  u := to_unsigned(i, 8);",
        "https://www.chipverify.com/vhdl/vhdl-numeric-std"),

    "to_signed": ("function",
        "Converts integer to signed.\n"
        "  s := to_signed(i, 8);",
        "https://www.chipverify.com/vhdl/vhdl-numeric-std"),

    "conv_integer": ("function",
        "Converts std_logic_vector to integer (ieee.std_logic_arith).\n"
        "  i := conv_integer(slv);",
        "https://www.chipverify.com/vhdl/vhdl-conv-functions"),

    "conv_std_logic_vector": ("function",
        "Converts integer to std_logic_vector (ieee.std_logic_arith).\n"
        "  slv := conv_std_logic_vector(i, 8);",
        "https://www.chipverify.com/vhdl/vhdl-conv-functions"),

    # --- Attributes ---
    "'event": ("attribute",
        "TRUE if signal just changed.\n"
        "  if clk'event and clk = '1' then",
        "https://www.chipverify.com/vhdl/vhdl-attributes"),

    "'last_value": ("attribute",
        "Previous value of signal before last event.",
        "https://www.chipverify.com/vhdl/vhdl-attributes"),

    "'range": ("attribute",
        "Returns the range of an array.\n"
        "  for i in sig'range loop",
        "https://www.chipverify.com/vhdl/vhdl-attributes"),

    "'high": ("attribute",
        "Highest index of an array or type.",
        "https://www.chipverify.com/vhdl/vhdl-attributes"),

    "'low": ("attribute",
        "Lowest index of an array or type.",
        "https://www.chipverify.com/vhdl/vhdl-attributes"),

    "'left": ("attribute",
        "Leftmost index of an array or type.",
        "https://www.chipverify.com/vhdl/vhdl-attributes"),

    "'right": ("attribute",
        "Rightmost index of an array or type.",
        "https://www.chipverify.com/vhdl/vhdl-attributes"),

    "'length": ("attribute",
        "Length (number of elements) of an array.\n"
        "  n := sig'length;",
        "https://www.chipverify.com/vhdl/vhdl-attributes"),
}


def get_doc(name, language="verilog"):
    name_lower = name.lower()
    if language in ("verilog", "systemverilog"):
        return VERILOG_DOCS.get(name_lower) or VERILOG_DOCS.get("$" + name_lower) or VERILOG_DOCS.get("`" + name_lower)
    elif language == "vhdl":
        return VHDL_DOCS.get(name_lower)
    return None
