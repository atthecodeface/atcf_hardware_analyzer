# atcf_hardware_analyzer

This provides a suite of modules and types that provide for an
in-silicon or in-FPGA logic analyzer, which can capture signal traces
or statistics about signal arrival times

## Analyzer trace bus

Fundamentally the logic analyzer system operates on signals provided
by the design itself, delivered by an endpoint on a `t_analyzer_tgt`
bus. The endpoint is implemented using the `analyzer_target` module,
which drives out to the client logic the `t_analyzer_ctl` control bus and
which takes in the `t_analyzer_data` in response.

The control bus provides an `enable` signal, which can be used to turn
off (when deasserted) any logic driving the trace bus. It also
supplies a 'mux_control' output, which can be used to select one of
many possible input trace sources from the client. The data should be
zero when not enabled, and is synchronous to the client's clock.

The control bus is constructed as a tree driven by the root, which can
be an `apb_target_analyzer_ctl`. The nodes in the tree must be
`analyzer_mux_8` or `analyzer_mux_2` nodes, with the leaves being
`analyzer_target_stub` or `analyzer_target` modules; the resultant
data from the endpoints is wire-ored in the multiplexer modules (and
registered) and delivered back to the root of the tree.

Note: need to use `t_analyzer_data4` up through the tree, and deliver
the data out from `apb_target_analyzer_ctl`.

Note: need to add async crossing for analyzer data (and ctl)? Needs to
be a *fixed* number of cycles downstream and upstream.

## Analyzer data at the root

The data of the analyzer bus is fed (as a `t_analyzer_data4`) through
a trigger module, which copies its input to its output after a fixed
number of cycles, and presenting at the same time (matching the input)
a `t_analyzer_trace_op4` which aligns to the data.

The data and the analyzer trace op are fed into a trace module (such
as an `analyzer_trace_ram`). This captures the data when it is enabled the the trace ops indicate it; the captured data can be interrogated by a module (such as an `apb_target_analyer_access` module, which issues `t_analyzer_trace_req` and which gets `t_analyzer_trace_resp` in response.

## Access to the trace data

A module such as the `apb_target_analyer_access` drives the
`t_analyzer_trace_req` in to a trace module, and it takes back the
`t_analyzer_trace_resp` in response. It is also responsible for
sourcing the `t_analyzer_trace_cfg` to configure the trace and trigger
modules.

## Status

The repository is in use in the ATCF RISC-V systems grip repository

# Analyzer trigger modules

## `analyzer_trigger_simple` module

This trigger is made to be relatively simple but powerful; it is
stateless, and can only really utilize bottom two 32-bit values of the
analyzer data.

This module takes a `t_analyzer_data4` bus and registers it
(pretrigger). This is fed into four identical *byte* matching modules;
each one selects one of the 16 input bytes from the `t_analyzer_data4`
and uses a TCAM-style match with 8 bits of configured mask and 8 bits
of configured value. The value of this is stored when the data in is
valid, and the *previous* value is copied.

The output of this module only drives the bottom two 32-bit values on
the output `t_analyzer_data4` (the top two are zeroed); it does this
based on the trigger.

Each byte matcher then presents 6 possible conditions: true; the match
bit has changed; rising edge of the match; falling edge of the match;
the match bit; *not* of the match bit.

The next stage of the trigger selects one of each of the six match
conditions from all four of the byte matchers, and *ANDs* them
together. It does this for *two* match test bits.

Each of the match test bits can be configured (separately) to record
the time, record the data, or capture the data, if it has fired.

Recording the data records the data from the lower two 32-bit data
values of the `t_analyzer_data4` pipe. It does not use them currently
(should it be used for changing?)

Capturing the time records the current `t_timer_value`.

Capturing the data stores one of the lower two 32-bit values from the
input data pipeline in the output data, or 32-bits of the current
timer value, or the delta between the current timer value and the
previously recorded timer value.

## `analyzer_trigger_simple` use cases

The most common use case is just to capture the data on the data bus,
based on some simple conditions. More complex use cases can record the
time it takes an operation to be performed.

### Capture continuously

The four byte matchers configuration is irrelevant; the selectors
choose 'true' from each of the four byte matchers, to generate two
'match test' bits that are always true. The action for the match test
bits is set to 'capture data' for both, capturing their own data
(bottom 32-bits, and next 32-bits, of incoming data).

### Capture on change

The four byte matchers configuration is irrelevant; the selectors
choose 'true' from each of the four byte matchers, to generate two
'match test' bits that are always true *when the data is
changing*. The action for the match test bits is set to 'capture data'
for both, capturing their own data (bottom 32-bits, and next 32-bits,
of incoming data).

### Capture continuously when particular values are present

The four byte matchers configuration is set to pick out the particular values; this can be a single 32-bit value, or a number of possible values on particular bytes of the input data, etc.

The selectors choose 'matched' (or its inverse) from each of the four
byte matchers, to generate two 'match test' bits that are always
true. The action for the match test bits is set to 'capture data' for
both, capturing their own data (bottom 32-bits, and next 32-bits, of
incoming data).

### Time spent in and time of leaving an FSM state

A byte matcher is configured to monitor the state bits of the input
bus for the particular state value.

One selector is configured to fire on just the *rising* edge of this
being matched, and when this occurs to record the time.

The other selector is configured to fire on just the *falling* edge of
this being matched, and when this occurs to capture both 32-bits of
the output data with the sources being the time delta, and the timer
value.

### FSM state and its transitions

TBD

### Two independent traces

TBD

### Fifo occupancy (16-bits) changes

TBD

# Commonmark notes

Heading: #; subheading ##; subsubheading ###.

*Italics*, **Bold**, and `inline code`. Or _italics_, __bold__.

> Block quotes

* Item list

1. Numeric list

2. Numeric list

```
Code block
```

[link](http://stuff "Title for link")

![Image description](http://a.jpg "Image title")
