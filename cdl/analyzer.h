/*a Includes
 */
include "std::valid_data.h"

/*a Types for the analyzer bus (ctl and data) */
/*t t_analyzer_mst - Master interface towards target */
typedef struct {
    bit    valid  "If asserted, shift in the data to the control registers";
    bit[4] data   "Data for control - N bits shifted in from low to high, with data out of 0 until valid is deasserted";
    bit    enable "If high and selected then node is enabled - chained through bus joiners and targets; if seen as low, then do not drive data bus";
    bit    select "If high when enable is seen to go high at a node then that node is selected and enabled";
} t_analyzer_mst;

/*t t_analyzer_data4
 */
typedef struct {
    bit valid  "High if the data is valid from the target";
    bit[32] data_0;
    bit[32] data_1;
    bit[32] data_2;
    bit[32] data_3;
} t_analyzer_data4;

/*t t_analyzer_tgt - Target interface back towards master */
typedef struct {
    bit     enable_return "If high and selected then node is enabled - chained through bus joiners and targets; if seen as low, then do not drive data bus";
    bit     selected      "Asserted if node is selected - for status only";
    t_analyzer_data4 data  "Data from node; all zeros if not selected";
} t_analyzer_tgt;

/*t t_analyzer_ctl - Control information to a target */
typedef struct {
    bit     enable;
    bit[32] mux_control "Shifted in from valid/data - cleared when a node becomes selected";
} t_analyzer_ctl;

/*a Types for control master */
/*t t_actl_op
 * APB control op
 */
typedef enum [3] {
    actl_op_none,
    actl_op_clear_enable,
    actl_op_select,
    actl_op_select_all,
    actl_op_select_none,
    actl_op_write_data,
} t_actl_op;

/*t t_analyzer_mst_ctl
 * Analyzer control operation
 */
typedef struct {
    t_actl_op actl_op;
    bit[64] data;
} t_analyzer_mst_ctl;

/*t t_analyzer_mst_ctl_resp
 * Analyzer control response
 */
typedef struct {
    bit[16] count;
    bit selected;
    bit completed;
} t_analyzer_mst_ctl_resp;

/*a Types for the trace */
/*t t_analyzer_filter_cfg
 */
typedef struct {
    bit enable;
    bit accept_unchanging;
    t_analyzer_data4 mask;
    t_analyzer_data4 value;
} t_analyzer_filter_cfg;

/*t t_analyzer_trace_cfg_value
 */
typedef struct {
    bit[24] base;
    bit[5] shift;
    bit[5] mask_size;
    bit max_min;
} t_analyzer_trace_cfg_value;

/*t t_analyzer_trace_cfg_ofs
 */
typedef struct {
    bit[24] base;
    bit[5] shift;
    bit use_data_1;
    bit no_bkts;
} t_analyzer_trace_cfg_ofs;

/*t t_analyzer_trace_cfg_fifo
 */
typedef struct {
    bit[2] data_width;
    bit journal;
    bit fifo_per_ram;
    bit ram_of_fifo;
    bit enable_push;
} t_analyzer_trace_cfg_fifo;

/*t t_analyzer_trace_cfg
 */
typedef struct {
    bit enable;
    t_analyzer_trace_cfg_value value_0;
    t_analyzer_trace_cfg_value value_1;
    t_analyzer_trace_cfg_ofs offset;
    t_analyzer_trace_cfg_fifo fifo_0;
    t_analyzer_trace_cfg_fifo fifo_1;
    bit[2] timer_div;
} t_analyzer_trace_cfg;

/*a Types for analyzer trigger */
/*t t_analyzer_trigger_timer
 */
typedef struct
{
    bit[32] value;
    bit[32] timer_delta "Valid if recorded_delta is valid";
    t_vdata_32 recorded_value;
    t_vdata_32 recorded_delta;
} t_analyzer_trigger_timer;

/*t t_analyzer_trigger_ctl
 */
typedef struct {
    bit enable;
    bit clear;
    bit running;
} t_analyzer_trigger_ctl;

/*t t_analyzer_trigger_cfg_actions
 */
typedef struct {
    bit  halt_capture;
    bit  record_data;
    bit  record_time;
    bit  record_invalidate;
    bit[2]  capture_data;
} t_analyzer_trigger_cfg_actions;

/*t t_analyzer_trigger_cfg_byte
 */
typedef struct {
    bit ignore_valid;
    bit[3] byte_sel;
    bit[8] mask;
    bit[8] match;
    bit[2] cond_sel;
} t_analyzer_trigger_cfg_byte;

/*t t_analyzer_trigger_cfg_data_src
 */
typedef enum[2] {
    atc_ds_data_0,
    atc_ds_data_1,
    atc_ds_data_2,
    atc_ds_data_3,
} t_analyzer_trigger_cfg_data_src;

/*t t_analyzer_trigger_cfg_match_data_src
 */
typedef enum[3] {
    blah,
} t_analyzer_trigger_cfg_match_data_src;


/*t t_analyzer_trigger_cfg_data_source
 */
typedef enum[3] {
    atc_data_source_timer,
    atc_data_source_timer_delta,
    atc_data_source_din_0,
    atc_data_source_rd_0,
    atc_data_source_din_1,
    atc_data_source_rd_1
} t_analyzer_trigger_cfg_data_source;

/*t t_analyzer_trigger_cfg
 */
typedef struct {
    bit enable;
    bit clear;
    bit start;
    bit stop;
    bit[2] timer_div;
    t_analyzer_trigger_cfg_match_data_src match_data_src_0;
    t_analyzer_trigger_cfg_match_data_src match_data_src_1;
    t_analyzer_trigger_cfg_byte tb_0;    
    t_analyzer_trigger_cfg_byte tb_1;    
    t_analyzer_trigger_cfg_byte tb_2;    
    t_analyzer_trigger_cfg_byte tb_3;    
    bit[48] action_set "Sixteen 3-bit action sets; the index is taken from bundling the 4 matched bits";
    t_analyzer_trigger_cfg_actions actions_0 "Actions used based on action_set";
    t_analyzer_trigger_cfg_actions actions_1 "Actions used based on action_set";
    t_analyzer_trigger_cfg_actions actions_2 "Actions used based on action_set";
    t_analyzer_trigger_cfg_actions actions_3 "Actions used based on action_set";
    t_analyzer_trigger_cfg_actions actions_4 "Actions used based on action_set";
    t_analyzer_trigger_cfg_actions actions_5 "Actions used based on action_set";
    t_analyzer_trigger_cfg_actions actions_6 "Actions used based on action_set";
    t_analyzer_trigger_cfg_actions actions_7 "Actions used based on action_set";
    t_analyzer_trigger_cfg_data_src data_src_0;
    t_analyzer_trigger_cfg_data_src data_src_1;
    t_analyzer_trigger_cfg_data_source data_source_0;
    t_analyzer_trigger_cfg_data_source data_source_1;
} t_analyzer_trigger_cfg;

/*t t_analyzer_trace_data_op
 */
typedef enum[3] {
    alu_op_push,
    alu_op_write,
    alu_op_inc,
    alu_op_sum,
    alu_op_min,
    alu_op_max,
    alu_op_min_max,
    alu_op_inc_add
} t_analyzer_trace_data_op;

/*t t_analyzer_trace_op4
 *
 * Currently just a capture bit for each 'port'
 *
 */
typedef struct {
    bit[4] capture;
} t_analyzer_trace_op4;

/*t t_analyzer_trace_req
 */
typedef struct {
    bit x;
} t_analyzer_trace_req;

/*t t_analyzer_trace_resp
 */
typedef struct {
    bit x;
} t_analyzer_trace_resp;

