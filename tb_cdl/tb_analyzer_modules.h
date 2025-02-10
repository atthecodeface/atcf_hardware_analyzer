/*a Includes */
include "apb::apb.h"
include "analyzer.h"

/*a Modules */
/*m tb_apb_target_analyzer_src */
extern
module tb_apb_target_analyzer_src( clock clk,
                                   input bit reset_n,

                                   input  t_apb_request  apb_request  "APB request",
                                   output t_apb_response apb_response "APB response",

                                   input  t_analyzer_mst  analyzer_mst,
                                   output t_analyzer_tgt  analyzer_tgt

    ) {
    timing to rising clock clk  apb_request, analyzer_mst;
    timing from rising clock clk  apb_response, analyzer_tgt;
}

