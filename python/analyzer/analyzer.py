#a Imports
from enum import IntEnum

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

# t_address_op
class t_address_op(IntEnum):
    width = 3
    access = 0
    reset_ptrs = 1
    push = 2
    pop = 3
    pass

# t_alu_op
class t_alu_op(IntEnum):
    width = 4
    clear = 0
    write8 = 1
    write16 = 2
    write32 = 3
    inc32 = 4
    sum32 = 5
    min32 = 6
    max32 = 7
    min_max16 = 8
    inc16_add1 = 9
    pass

# t_access_resp
t_access_resp = {
    "valid": 1,
    "id": 2,
    "data": 32,
}

# t_access_combs
t_access_combs = {
    "read_enable":1,
    "write_enable":1,
    "id": 2,
    "address_op": t_address_op.width.value,
    "address": 11,
    "op_data":32,
    "alu_op": t_alu_op.width.value,
    "byte_of_sram":2,
    }
