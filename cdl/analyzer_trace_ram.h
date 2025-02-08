/*a Includes
 */
include "utils::fifo_status.h"

/*a Types
 */
/*t t_word_address */
typedef bit[11] t_word_address;

/*t t_full_byte_address */
typedef bit[14] t_full_byte_address;

/*t t_alu_op
 */
typedef enum[4] {
    alu_op_clear,
    alu_op_write8,
    alu_op_write16,
    alu_op_write32,
    alu_op_inc32,
    alu_op_sum32,
    alu_op_min32,
    alu_op_max32,
    alu_op_min_max16,
    alu_op_inc16_add16
} t_alu_op;

/*t t_address_op
 */
typedef enum[3] {
    address_op_access,
    address_op_reset_ptrs,
    address_op_push,
    address_op_pop,
} t_address_op;

/*t t_access_resp
 */
typedef struct
{
    bit            valid;
    bit[2]         id;
    bit[32]        data;
} t_access_resp;

/*t t_access_combs
 */
typedef struct
{
    bit            read_enable;
    bit            write_enable;
    bit[2]         id;
    t_address_op   address_op;
    bit[32]        op_data;
    t_word_address address;
    t_alu_op       alu_op;
    bit[2]         byte_of_sram;
} t_access_combs;

/*a modules
 */
extern
module analyzer_trace_ram_data_path( clock clk,
                                     input bit reset_n,

                                     input t_access_combs access_req,
                                     output t_access_resp access_resp,

                                     output t_fifo_status fifo_status,
                                     input  t_analyzer_trace_cfg_fifo trace_cfg_fifo
    )
{
    timing to   rising clock clk access_req, trace_cfg_fifo;
    timing from rising clock clk access_resp, fifo_status;
}
