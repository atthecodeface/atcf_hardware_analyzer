#a Structures
# t_analyzer_data4 */
t_analyzer_data4 = {
    "valid":1,
    "data_0":32,
    "data_1":32,
    "data_2":32,
    "data_3":32,
}

# t_analyzer_filter_cfg
t_analyzer_filter_cfg = {
    "enable":1,
    "accept_unchanging":1,
    "mask": t_analyzer_data4,
    "value": t_analyzer_data4,
}

# t_analyzer_trace_cfg_fifo
t_analyzer_trace_cfg_fifo = {
    "data_width":2,
    "journal":1,
    "enable_push":1,
}

# /*t t_alu_op
# #typedef enum[4] {
# #    alu_op_write8,
# #    alu_op_write16,
# #    alu_op_write32,
# #    alu_op_inc32,
# #    alu_op_sum32,
# #    alu_op_min32,
# #    alu_op_max32,
# #    alu_op_min_max16,
# #    alu_op_inc16_add16
#} t_alu_op;

# t_access_combs
t_access_combs = {
    "op_data":32,
    "read_enable":1,
    "read_ptr": 11,
    "alu_op": 4, # t_alu_op,
    "write_enable":1,
    "write_ptr": 11,
    "byte_of_sram":2,
    }
