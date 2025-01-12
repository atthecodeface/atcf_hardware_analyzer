# atcf_hardware_analyzer

This provides a suite of modules and types that provide for an
in-silicon or in-FPGA logic analyzer, which can capture signal traces
or statistics about signal arrival times

The concept behind the ATCF analyzer is:

* Any component on a device can source an analyzer trace bus,
  controlled by a standard mechanism (to allow the component to select
  one of many potential data sources), which can be disables with a
  clock gate so that it only consumes power when debugging is
  required.

* The sources are combined by registered wire-ored pipeline stages,
  with clock gating provided to maintain low power when debugging is
  disabled.

* The combined data is analyzed by a *trigger* mechanism, which sits
  alongside a pipeline of the analyzer data and produces a *trigger
  action* to coincide with some data

* The *trigger action* and data are fed to a *trace* module; this
  terminates the data in some fashion - perhaps by storing one or more
  traces in an SRAM, or just counting occurrences of triggers.

* An analyzer controller that is connected to CSRs can: drive the
  control portion of the analyzer bus (to enable particular components
  and select potential data sources); configure the trigger; configure
  the trace; request the trace data and present it over CSR reads.

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
as an `analyzer_trace_ram`). This captures the data when it is enabled
the the trace ops indicate it; the captured data can be interrogated
by a module (such as an `apb_target_analyer_access` module, which
issues `t_analyzer_trace_req` and which gets `t_analyzer_trace_resp`
in response.

## Access to the trace data

A module such as the `apb_target_analyer_access` drives the
`t_analyzer_trace_req` in to a trace module, and it takes back the
`t_analyzer_trace_resp` in response. It is also responsible for
sourcing the `t_analyzer_trace_cfg` to configure the trace and trigger
modules.

# Analyzer trace modules

An endpoint on the analyzer trace bus should output its data with
little filtering; it can drive the bus valid on every cycle unless
there is a good reason not to do so (it might be purely mirroring
internal state of counters and state machines, for example). A good
reason might be as it is only capturing valid accesses or data cycles.

As the endpoint may drive the bus on every cycle, but for a particular
trace setup only a small subset of trace data may need to be
interrogated, the trace bus can be *filtered* before entering an async
clock crossing or a trigger module.

The `analyzer_trace_filter` module provides a configurable filter that
is a pipeline of analyzer data; the filter can be configured so that
the trace data is invalidated if any of the bits do not match a
configured value (TCAM-style). Furthermore, the filter can be
configured to invalidate a trace cycle if the *last* *valid* data has
the same bit values in a configured set of bits as the new data; this
enables a trace to only consist of data where certain bits are
changing (and intermediate trace data where those bits are constant
are dropped). This is very useful to monitor changes in FSM states;
the filter is configured to only accept trace data with changing values on
the bits correspondiong to the FSM state.

Another possiblity is to have a rate-limiter on the trace bus; if a
filter is only going to produce data on average every 100 cycles, then
an analyzer trigger might be configurable which takes four or five
cycles to 'process'; the input data to the trigger should not exceed
the rate of one-every-five cycles, but the bus might normally
instantaneously deliver two back-to-back. The analyzer trace bus has
no *ack*, but the trigger can be treated as virtually driving an *ack*
signal always high; a generic valid-ack module can then be used, such
as the double-buffer, with a rate-limited output. This *may* benefit
from having a small FIFO preceding the rate limiter; the rate of that
double buffer is configurable at run-time.

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


# Analyzer trace modules

## `analyzer_trace_ram` module

This module contains a pair of 8kB dual-port SRAMs which can store
traces or histograms of captured data values from a trigger (which can
include times, if the trigger produces data which includes times).

The module takes a trigger operation and two 32-bit trigger data
values; it produces from these two data values a histogram index
value.

The two SRAMs are then independently fed the two data values and the
histogram index; each SRAM can be configured to capture a trace (in
which case it ignores the histogram index, and uses FIFO pointers) or
to use the histogram index and combine the SRAM data with one of the
two data values to update the SRAM (e.g. by adding the data value).

The SRAMs can thus be configured to operate (for example):

* As one database recording the number of occurrences and min, max,
  total data access time for 2k different DRAM addresses.

* As a database recording the number of occurrences and total data
  access time for 2k different DRAM addresses while separately
  capturing a trace of DRAM access requests for only those addresses

* As a histogram of the residence times of a specific set of states of
  a state machine, while capturing a trace of the other data

* As a single 16k entry trace of 8-bits of data from the analyzer data
  bus (e.g. capturing the last 16k state transitions of a state
  machine)

* As a 2k entry trace of 32-bit absolute time and 32-bits of trace
  data for every cycle the trace data changes.

and infinitely more...

### Pretreatment of trigger data (data value selection)

The trigger data is a pair of 32-bit data. A pretreatment is applied
to this data to generate the data used for an index into the SRAM or
that is used in the actual trace.

Both of the trigger data are treated in the same
manner (with separate configuration).

The basic treatment is to subtract a base value, shift the result
down, and then mask this to bound the data within a certain
range. However, the treatment can be configured to *bound* the value,
such that if the input is less than the base then the output is *0*,
and if the input is too large then the output is *mask* (rather than
purely ANDing with the mask).

The simplest treatment is just to pass the trigger data through: this
is configured with a base of 0, a shift of 0, and a mask size of 0.

A range of bits from the trigger data can be selected directly, if
required; to select 7 bits starting at bit 12 the configuration would
be a base of 0, a shift of 12, and a mask size of 32-7=25.

The trigger data might be a residence time (from a time delta
generated in the trigger), and a histogram of residence times may be
required. The smallest possible residence time might be 100, and the
largest expected 1000. A base of 100, a shift of 0, and a mask of
32-10=22 would perform:

```
value = ((trigger data - 100) >> 0) % 1024
```

which would be correct *except* for outlier values of the trigger data
for residence time; these need to be bounded, so setting the *max_min*
configuration would do this:

```
value = ((trigger data - 100) >> 0).min_max(0,1023)
```

If bits 17 to 27 of the trigger data contain the residence time then
the configuration could be a base of 100<<17, a shift of 17, and
min-max of 2k (11 bits):

```
value = ((trigger data - (100<<17)) >> 17).min_max(0,2047)
      = ((trigger data >> 17) - 100).min_max(0,2047)
```

If bits 13 to 31 of the trigger data contain the residence time then the
configuration could be a base of 100<<13, a shift of 13, and min-max
of 512k-1 (19 bits):

```
value = ((trigger data >> 13) - 100).min_max(0,512k-1)
```

### Data offset for capturing (histogram index selection)

The pretreatment is designed to extract the relevant data from the
trigger data; this data may be required to be stored in an SRAM trace,
or it might be a residence time, or it might be a state number or
transaction id, DRAM address, or whatever.

The analyzer might be required to generate a histogram where the
residence time of different states needs to be recorded in different
histogram entries; it might be required to generate min/max/total
access times for different DRAM addresses in different table
entries. Hence a second treatment phase is required to (potentially)
generate the histogram index for a trigger data from the pretreatment
data.

Hence, once the pretreatment of data has been performed a *second*
calculation is performed ('bucketing'), which can be used for
addressing the SRAM(s). The output of this stage is an 11 bit value
(for use in the 2k entry SRAMs).

This takes either of the pretreated trigger data; it subtracts a base
value and shifts it down by a configurable shift (of up to 20) - producing a value *X*. It
then performs a range compression on this *X* value:

* If *X* < 0 the the result is 0

* else if 0 <= *X* < 512 the the result is *X*

* else if 0 <= (*X* - 512)/4 < 512 the the result is (*X* - 512)/4 + 512

* else if 0 <= (*X* - 2560)/16 < 512 the the result is (*X* - 2560)/16 + 1024

* else if 0 <= (*X* - 10752)/64 < 512 the the result is (*X* - 10752)/64 + 1536

* else the result is 2047

This 'bucketing' operation effectively uses offsets 0 to 0x1ff as a
bucket size of 1; 0x200 to 0x3ff as a bucket size of 4; 0x400 to 0x5ff
as a bucket size of 16; 0x600 to 0x7fe as a bucket size of 64. Entry 0
also holds any value that was below the 'base', and entry 0x7ff holds
any value more than 0xa9c0 (approx 43000) above the base.

This 'bucketing' stage can disabled - i.e. the data offset is taken
directly from the bottom 11 bits of ((*X* - base)>>shift) (except if
*X* is less than base then 0 is used). To just pass through the
pretreated data directly, configure the base and shift to be 0.

### SRAM operation

The result of the pretreatment of the data and the data offset
calculations are two 32-bit data values, and one index value (derived
from one of those two 32-bit data values). Each SRAM selects *one* of
the two data values to be used for its data.

Each SRAM is contained within an `analyzer_trace_ram_data_path`
module. This contains logic that for FIFO read and write pointers, if
the SRAM is to be used as a trace RAM. This logic can be configured to
support *halt on full*, or it can be configured to *journal* - that
is, it keeps recording after becoming full by dragging the 'read'
pointer along as it continues to increase the 'write' pointer on every
push. In *journal* mode the tracing should be stopped explicitly by
the control interface.

The SRAM can be used to capture traces or generate histograms; to
support this it has an ALU pipeline that has SRAM read request, SRAM
read data, ALU operation, SRAM writeback pipeline stages. The ALU
operations supported include `write8`, `write16`, `write32`, `inc32`, `sum32`,
`min32`, `max32`, `min_max16`, and `inc16_add16`.

The *address* for a trace SRAM operation is taken from the FIFO `write
pointer` if a trace is being captured; however, to generate histograms
the address is taken from the data offset.

The write operations just write the selected data over the current
contents of the SRAM; this allows for SRAM traces to record only 8
bits or 16 bits from the selected bus.

The increment operations add 1 to the SRAM contents (but saturating at
'intmax') and stores that back in the SRAM. This is used to *count*
the number of operations. (This does not use the 'selected data').

The add operation adds the *selected data* to the SRAM contents (but saturating at
'intmax') and stores that back in the SRAM.

The min operation compares the *selected data* to the SRAM contents;
if it is less then it stores the value in the SRAM, but if it is
greater then it does not change the SRAM contents.

The max operation compares the *selected data* to the SRAM contents;
if it is greater then it stores the value in the SRAM, but if it is
less then it does not change the SRAM contents.

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
