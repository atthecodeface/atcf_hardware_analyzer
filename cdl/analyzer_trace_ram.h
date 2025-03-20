/*a Includes
 */
include "utils::fifo_status.h"
include "analyzer.h"

/*a modules
 */
extern
module analyzer_trace_ram_data_path( clock clk,
                                     input bit reset_n,

                                     input t_analyzer_trace_access_req access_req,
                                     output t_analyzer_trace_access_resp access_resp,

                                     output t_fifo_status fifo_status,
                                     input  t_analyzer_trace_cfg_fifo trace_cfg_fifo
    )
{
    timing to   rising clock clk access_req, trace_cfg_fifo;
    timing from rising clock clk access_resp, fifo_status;
}
