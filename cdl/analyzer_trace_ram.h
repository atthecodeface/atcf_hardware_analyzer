/*a Includes
 */
include "utils::fifo_status.h"

/*a Types
 */
/*t t_atr_alu_op
 */
typedef enum[4] {
    atr_alu_op_clear,
    atr_alu_op_write8,
    atr_alu_op_write16,
    atr_alu_op_write32,
    atr_alu_op_inc32,
    atr_alu_op_sum32,
    atr_alu_op_min32,
    atr_alu_op_max32,
    atr_alu_op_min_max16,
    atr_alu_op_inc16_add16
} t_atr_alu_op;

/*t t_analyzer_trace_address_op
 */
typedef enum[3] {
    atr_address_op_access,
    atr_address_op_reset_ptrs,
    atr_address_op_push,
    atr_address_op_pop,
} t_analyzer_trace_address_op;

/*t t_analyzer_trace_access_resp
 */
typedef struct
{
    bit            valid;
    bit[2]         id;
    bit[32]        data;
} t_analyzer_trace_access_resp;

/*t t_analyzer_trace_access_req
 */
typedef struct
{
    bit            read_enable;
    bit            write_enable;
    bit[2]         id;
    t_analyzer_trace_address_op   address_op;
    bit[32]        op_data;
    bit[16]        address;
    t_atr_alu_op   alu_op;
    bit[2]         byte_of_sram;
} t_analyzer_trace_access_req;

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
