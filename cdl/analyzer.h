/** Copyright (C) 2020,  Gavin J Stark.  All rights reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 * @file   analyzer.h
 * @brief  Types for the analyzer data/control buses
 *
 * Header file for the types for the analyzer data/control buses
 *
 */

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

/*t t_analyzer_trigger_cfg_byte
 */
typedef struct {
    bit[2] data_sel;
    bit[2] byte_sel;
    bit[8] mask;
    bit[8] match;
} t_analyzer_trigger_cfg_byte;

/*t t_analyzer_trigger_cfg_data_action
 */
typedef struct {
    bit[3] cond_0;
    bit[3] cond_1;
    bit[3] cond_2;
    bit[3] cond_3;
    bit only_if_changing;
    bit record_time;
    bit record_data;
    bit[2] capture_data;
} t_analyzer_trigger_cfg_data_action;

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
    bit[2] timer_div;
    t_analyzer_trigger_cfg_byte tb_0;    
    t_analyzer_trigger_cfg_byte tb_1;    
    t_analyzer_trigger_cfg_byte tb_2;    
    t_analyzer_trigger_cfg_byte tb_3;    
    t_analyzer_trigger_cfg_data_action data_action_0;
    t_analyzer_trigger_cfg_data_action data_action_1;
    t_analyzer_trigger_cfg_data_source data_source_0;
    t_analyzer_trigger_cfg_data_source data_source_1;
} t_analyzer_trigger_cfg;

/*t t_analyzer_trace_data_op
 */
typedef struct {
    bit capture;
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

