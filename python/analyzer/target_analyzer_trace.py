#a Documentation
"""

"""

#a Imports
from .analyzer import t_atr_address_op, t_atr_alu_op

#a Trace configuration classes
#c TraceCfgValue
class TraceCfgValue:
    base = 0
    shift = 0
    mask_size = 0
    max_min = False
    def __init__(self):
        pass
    def reg_values(self):
        value = self.shift + (self.mask_size<<8) + (int(self.max_min)<<16)
        return (self.base, value)
    pass

#c TraceCfgOffset
class TraceCfgOffset:
    base = 0
    shift = 0
    use_data_1 = False
    no_bkts = False
    def __init__(self):
        pass

    def reg_values(self):
        value = self.shift + (int(self.use_data_1)<<8) + (int(self.no_bkts)<<9)
        return (self.base, value)
    pass

#c TraceCfgFifo
class TraceCfgFifo:
    data_width = 32
    journal = False
    fifo_per_ram = True
    ram_of_fifo = 0
    enable_push = False
    def __init__(self):
        pass

    def reg_value(self):
        value = {32:3, 16:2, 8:1}[self.data_width]
        value += int(self.journal)<<2
        value += int(self.fifo_per_ram)<<3
        value += self.ram_of_fifo<<4
        value += int(self.enable_push)<<5
        return value
    pass

#c TraceCfg
class TraceCfg:
    def __init__(self):
        self.offset = TraceCfgOffset()
        self.values = (TraceCfgValue(), TraceCfgValue())
        self.fifos = (TraceCfgFifo(), TraceCfgFifo())
        self.fifos[0].enable_push = True
        self.fifos[1].enable_push = True
        pass
    
    #f apb_writes_control
    def apb_writes_control(self, map, enable:False):
        # write enable
        pass

    #f apb_writes
    def apb_writes(self, map):
        writes = []
        fifos = self.fifos[0].reg_value()
        fifos += self.fifos[1].reg_value()<<16
        writes.append( (map.trace_fifos, fifos ) )
        (base, etc) = self.offset.reg_values()
        writes.append( (map.trace_offset_base, base) )
        writes.append( (map.trace_offset_shift_size, etc) )
        (base, etc) = self.values[0].reg_values()
        writes.append( (map.trace_value_0_base, base) )
        writes.append( (map.trace_value_0_shift_size, etc) )
        (base, etc) = self.values[1].reg_values()
        writes.append( (map.trace_value_1_base, base) )
        writes.append( (map.trace_value_1_shift_size, etc) )
        return writes

#a Trace access classes
#c AtrAccessOp
class AtrAccessOp:
    """
    A trace RAM access operation
    """
    read_enable = 0
    write_enable = 0
    id = 0
    address_op = t_atr_address_op.access
    address = 0
    alu_op = t_atr_alu_op.clear
    data = 0
    byte_of_sram = 0
    def __init__(self, id=None, address_or_op=None, data=None, alu_op=None, write_enable=0, read_enable=0):
        if id is not None:
            self.id = id
            pass
        if type(address_or_op) == t_atr_address_op:
            self.address_op = address_or_op
            pass
        elif address_or_op != None:
            self.address_op = t_atr_address_op.access
            self.address = address_or_op
            pass
        if data is not None:
            self.data = data
            pass
        if alu_op is not None:
            self.alu_op = alu_op
            pass
        self.write_enable = write_enable
        self.read_enable = read_enable
        pass

    #f drive_access_req
    def drive_access_req(self, obj, pfx):
        getattr(obj, pfx+"__read_enable").drive(self.read_enable)
        getattr(obj, pfx+"__write_enable").drive(self.write_enable)
        getattr(obj, pfx+"__id").drive(self.id)
        getattr(obj, pfx+"__address_op").drive(self.address_op.value)
        getattr(obj, pfx+"__word_address").drive(self.address)
        getattr(obj, pfx+"__alu_op").drive(self.alu_op.value)
        getattr(obj, pfx+"__op_data").drive(self.data)
        getattr(obj, pfx+"__byte_of_sram").drive(self.byte_of_sram)
        pass

    #f classmethod atomic
    @classmethod
    def atomic(cls, address, data, alu_op):
        return cls(address_or_op=address, data=data, alu_op=alu_op, write_enable=1, read_enable=1)

    #f classmethod write
    @classmethod
    def write(cls, address, data, width=32):
        alu_op = {8:t_atr_alu_op.write8, 16:t_atr_alu_op.write16, 32:t_atr_alu_op.write32}[width]
        return cls(address_or_op=address, data=data, alu_op=alu_op, write_enable=1, read_enable=0)
    @classmethod
    def read(cls, address, id=1):
        return cls(id, address_or_op=address, alu_op=t_atr_alu_op.clear, write_enable=0, read_enable=1)
    @classmethod
    def push(cls, data, width=32):
        alu_op = {8:t_atr_alu_op.write8, 16:t_atr_alu_op.write16, 32:t_atr_alu_op.write32}[width]
        read_enable = 0
        if width!=32: read_enable = 1
        return cls(address_or_op=t_atr_address_op.push, data=data, alu_op=alu_op, write_enable=1, read_enable=read_enable)
    @classmethod
    def pop(cls, id=1):
        return cls(id, address_or_op=t_atr_address_op.pop, alu_op=t_atr_alu_op.clear, write_enable=0, read_enable=1)
    @classmethod
    def clear(cls, address, id=1):
        read_enable = 0
        if id != 0: read_enable = 1
        return cls(id, address_or_op=address, alu_op=t_atr_alu_op.clear, write_enable=1, read_enable=read_enable)
    pass

