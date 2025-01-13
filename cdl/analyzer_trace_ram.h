/*t t_word_address */
typedef bit[11] t_word_address;

/*t t_full_byte_address */
typedef bit[14] t_full_byte_address;

/*t t_alu_op
 */
typedef enum[4] {
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

/*t t_access_combs
 */
typedef struct
{
    bit[32] op_data;
    bit read_enable;
    t_word_address read_ptr;
    t_alu_op alu_op;
    bit     write_enable;
    t_word_address write_ptr;
    bit[2]  byte_of_sram;
} t_access_combs;

/*a modules
 */
extern
module analyzer_trace_ram_data_path( clock clk,
                                     input bit reset_n,

                                     input t_access_combs access_combs,

                                     output t_fifo_status fifo_status,
                                     input  t_analyzer_trace_cfg_fifo trace_cfg_fifo
    )
{
    timing to   rising clock clk access_combs, trace_cfg_fifo;
    timing from rising clock clk fifo_status;
}
