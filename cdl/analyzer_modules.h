/*a Includes */
include "std::valid_data.h"
include "utils::fifo_status.h"
include "apb::apb.h"
include "clocking::clock_timer.h"
include "analyzer.h"
include "analyzer_trigger.h"

/*a Modules */
/*m analyzer_mux_8 */
extern
module analyzer_mux_8( clock clk,
                       input bit reset_n,
                       input  t_analyzer_mst  analyzer_mst,
                       output t_analyzer_tgt  analyzer_tgt,

                       output  t_analyzer_mst  analyzer_mst_a,
                       input   t_analyzer_tgt  analyzer_tgt_a,

                       output  t_analyzer_mst  analyzer_mst_b,
                       input   t_analyzer_tgt  analyzer_tgt_b,

                       output  t_analyzer_mst  analyzer_mst_c,
                       input   t_analyzer_tgt  analyzer_tgt_c,

                       output  t_analyzer_mst  analyzer_mst_d,
                       input   t_analyzer_tgt  analyzer_tgt_d,

                       output  t_analyzer_mst  analyzer_mst_e,
                       input   t_analyzer_tgt  analyzer_tgt_e,

                       output  t_analyzer_mst  analyzer_mst_f,
                       input   t_analyzer_tgt  analyzer_tgt_f,

                       output  t_analyzer_mst  analyzer_mst_g,
                       input   t_analyzer_tgt  analyzer_tgt_g,

                       output  t_analyzer_mst  analyzer_mst_h,
                       input   t_analyzer_tgt  analyzer_tgt_h

    )
{
    timing to     rising clock clk analyzer_mst;
    timing from   rising clock clk analyzer_tgt;

    timing to     rising clock clk analyzer_tgt_a, analyzer_tgt_b, analyzer_tgt_c, analyzer_tgt_d;
    timing to     rising clock clk analyzer_tgt_e, analyzer_tgt_f, analyzer_tgt_g, analyzer_tgt_h;
    timing from   rising clock clk analyzer_mst_a, analyzer_mst_b, analyzer_mst_c, analyzer_mst_d;
    timing from   rising clock clk analyzer_mst_e, analyzer_mst_f, analyzer_mst_g, analyzer_mst_h;

}
/*m analyzer_mux_2 */
extern
module analyzer_mux_2( clock clk,
                       input bit reset_n,
                       input  t_analyzer_mst  analyzer_mst,
                       output t_analyzer_tgt  analyzer_tgt,

                       output  t_analyzer_mst  analyzer_mst_a,
                       input   t_analyzer_tgt  analyzer_tgt_a,

                       output  t_analyzer_mst  analyzer_mst_b,
                       input   t_analyzer_tgt  analyzer_tgt_b

    )
{
    timing to     rising clock clk analyzer_mst;
    timing from   rising clock clk analyzer_tgt;

    timing to     rising clock clk analyzer_tgt_a, analyzer_tgt_b;
    timing from   rising clock clk analyzer_mst_a, analyzer_mst_b;
}

/*m analyzer_target_stub */
extern
module analyzer_target_stub( clock clk,
                           input bit reset_n,
                           input  t_analyzer_mst  analyzer_mst,
                           output t_analyzer_tgt  analyzer_tgt
    )
{
    timing to     rising clock clk analyzer_mst;
    timing from   rising clock clk analyzer_tgt;
}

/*m analyzer_target */
extern
module analyzer_target( clock clk,
                        input bit reset_n,
                        input  t_analyzer_mst  analyzer_mst,
                        output t_analyzer_tgt  analyzer_tgt,
                        output t_analyzer_ctl analyzer_ctl,
                        input t_analyzer_data4 analyzer_data,
                        input bit[32] analyzer_tgt_id
    )
{
    timing to     rising clock clk analyzer_mst;
    timing from   rising clock clk analyzer_tgt;

    timing from   rising clock clk analyzer_ctl;
    timing to     rising clock clk analyzer_data, analyzer_tgt_id;
}


/*m analyzer_control_master */
extern module analyzer_control_master( clock clk,
                                input bit reset_n,

                                input t_analyzer_mst_ctl mst_ctl,
                                output t_analyzer_mst_ctl_resp mst_ctl_resp,

                                output  t_analyzer_mst  analyzer_mst,
                                input t_analyzer_tgt  analyzer_tgt "Data not used"

    )
{
    timing to   rising clock clk mst_ctl;
    timing from rising clock clk mst_ctl_resp;

    timing to   rising clock clk analyzer_tgt;
    timing from rising clock clk analyzer_mst;
}

/*m apb_target_analyzer */
extern module apb_target_analyzer( clock analyzer_clock,
                            clock async_trace_read_clock,
                            clock apb_clock,

                            input bit reset_n,

                            input  t_apb_request  apb_request  "APB request",
                            output t_apb_response apb_response "APB response",

                            output bit trace_ready,
                            output bit trace_done,

                            output  t_analyzer_mst  analyzer_mst,
                            input t_analyzer_tgt  analyzer_tgt,

                            input bit ext_trigger_reset,
                            input bit ext_trigger_enable,

                            input bit async_trace_read_enable,
                            output bit async_trace_valid_out,
                            output bit[32] async_trace_out )
{
    timing to   rising clock apb_clock apb_request;
    timing from rising clock apb_clock apb_response;

    timing from rising clock analyzer_clock trace_ready, trace_done;
    timing from rising clock analyzer_clock analyzer_mst;
    timing to   rising clock analyzer_clock analyzer_tgt;
    timing to   rising clock analyzer_clock ext_trigger_reset, ext_trigger_enable;

    timing to   rising clock async_trace_read_clock async_trace_read_enable;
    timing from rising clock async_trace_read_clock async_trace_valid_out, async_trace_out;
}

/*m apb_target_analyzer_ctl */
extern module apb_target_analyzer_ctl( clock clk,
                                       input bit reset_n,

                                       input  t_apb_request  apb_request  "APB request",
                                       output t_apb_response apb_response "APB response",

                                       output  t_analyzer_mst  analyzer_mst,
                                       input t_analyzer_tgt  analyzer_tgt )
{
    timing to   rising clock clk apb_request;
    timing from rising clock clk apb_response;

    timing from rising clock clk analyzer_mst;
    timing to   rising clock clk analyzer_tgt;
}

/*m apb_target_analyzer_cfg */
extern module apb_target_analyzer_cfg( clock clk,
                                input bit reset_n,

                                input  t_apb_request  apb_request  "APB request",
                                output t_apb_response apb_response "APB response",

                                output  t_analyzer_filter_cfg filter_cfg,
                                output  t_analyzer_trigger_cfg trigger_cfg,
                                output  t_analyzer_trace_cfg trace_cfg
    )
{
    timing to   rising clock clk apb_request;
    timing from rising clock clk apb_response;

    timing from rising clock clk filter_cfg, trigger_cfg, trace_cfg;
}

/*m analyzer_trigger_simple
 */
extern
module analyzer_trigger_simple( clock clk,
                           input bit reset_n,

                           input  t_analyzer_data4  din,
                           output  t_analyzer_data4 dout,

                           output  t_analyzer_trace_op4 trace_op,
                           input t_timer_value timer_value,

                           input  t_analyzer_trigger_cfg trigger_cfg_in
    ) {
    timing to rising clock clk  din, timer_value;
    timing from rising clock clk  dout, trace_op;
    timing to rising clock clk  trigger_cfg_in;
}

/*m analyzer_trigger_simple_byte
 */
extern
module analyzer_trigger_simple_byte( clock clk,
                                     input bit reset_n,

                                     input  t_vdata_32 match_data_0,
                                     input  t_vdata_32 match_data_1,
                                     output bit matched,
                                     input  t_analyzer_trigger_cfg_byte trigger_cfg_byte
    ) {
    timing to rising clock clk  match_data_0, match_data_1;
    timing from rising clock clk  matched;
    timing to rising clock clk  trigger_cfg_byte;
    timing comb input trigger_cfg_byte;
    timing comb output matched;
}

/*m analyzer_trigger_control
 */
extern
module analyzer_trigger_control( clock clk,
                                 input bit reset_n,

                                 input  t_analyzer_trigger_cfg trigger_cfg,
                                 input bit halt_trigger,
                                 output t_analyzer_trigger_ctl trigger_ctl
 )
{
    timing to rising clock clk  trigger_cfg, halt_trigger;
    timing from rising clock clk  trigger_ctl;
}

/*m analyzer_trigger_timer
 */
extern
module analyzer_trigger_timer( clock clk,
                               input bit reset_n,

                               input  t_analyzer_trigger_cfg trigger_cfg,
                               input  t_analyzer_trigger_ctl trigger_ctl,
                               input t_timer_value timer_value,
                               input bit record_time,
                               output t_analyzer_trigger_timer trigger_timer
    )
{
    timing to rising clock clk  trigger_cfg, trigger_ctl, timer_value, record_time;
    timing from rising clock clk  trigger_timer;
}

/*m analyzer_trace_data_value_bound
 */
extern module analyzer_trace_data_value_bound( clock clk,
                                               input bit reset_n,
                                               input  t_vdata_32  din,

                                               input  t_analyzer_trace_cfg_value trace_cfg,
                                               output t_vdata_32 p2_data_value
 )
 {
    timing to rising clock clk  trace_cfg, din;
    timing from rising clock clk  p2_data_value;
}

/*m analyzer_trace_data_offset_bound
 */
extern
module analyzer_trace_data_offset_bound( clock clk,
                                         input bit reset_n,
                                         input  t_analyzer_data4 p0_data,

                                         input  t_analyzer_trace_cfg_ofs trace_cfg,

                                         output t_vdata_32 p2_data
 )
 {
    timing to rising clock clk  trace_cfg, p0_data;
    timing from rising clock clk  p2_data;
}

/*m analyzer_trace_filter
 */
extern
module analyzer_trace_filter( clock clk,
                           input bit reset_n,

                           input  t_analyzer_data4  din,
                           output  t_analyzer_data4 dout,

                           input  t_analyzer_filter_cfg filter_cfg
 )
 {
     timing to rising clock clk  din, filter_cfg;
     timing from rising clock clk  dout;
}

/*m analyzer_trace_data_offset_bound
 */
extern
module analyzer_trace_ram( clock clk,
                           input bit reset_n,

                           input  t_analyzer_trace_op4  trace_op "Includes data to use for address calculation",
                           input  t_analyzer_data4  din "Only bottom two words are used here",

                           output t_fifo_status fifo_status_l,
                           output t_fifo_status fifo_status_h,

                           input t_analyzer_trace_req trace_req,
                           output t_analyzer_trace_resp trace_resp,

                           input  t_analyzer_trace_cfg trace_cfg
 )
 {
     timing to rising clock clk  trace_op, din;
     timing from rising clock clk  fifo_status_l, fifo_status_h;

     timing to rising clock clk  trace_req;
     timing from rising clock clk  trace_resp;

     timing to rising clock clk  trace_cfg;
}
