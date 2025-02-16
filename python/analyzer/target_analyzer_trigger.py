#a Documentation
"""
Classes that contain analyzer trigger configuration and operation
"""

#a Imports
from enum import Enum
from cdl.utils.csr   import Csr, CsrField, CsrFieldZero, Map, MapCsr

#a Trigger classes
#c DataSrc
class DataSrc(Enum):
    D0 = 0
    D1 = 1
    D2 = 2
    D3 = 3
    pass

#c MatchDataSrc
class MatchDataSrc(Enum):
    TIME = 0
    TIME_DELTA = 1
    RECORDED_DATA = 2
    DATA_DELTA= 3
    DATA = 4    
    pass

#c TraceDataSrc
class TraceDataSrc(Enum):
    """
    Data source for an output of the trigger into the trace
    """
    TIME = 0
    TIME_DELTA = 1
    D0 = 2
    D1 = 3
    RECORDED_DATA = 4
    pass

class SimpleByteMatchCond(Enum):
    CHANGING = 3
    NEGEDGE = 2
    POSEDGE = 1
    MATCH = 0
    pass

class SimpleByteMatch:
    ignore_valid = False
    byte_sel = 0
    mask = 0
    value = 0
    cond_sel = SimpleByteMatchCond.MATCH
    def reg_value(self):
        data = int(self.ignore_valid)
        data += self.byte_sel<<8
        data += self.cond_sel.value<<12
        data += self.mask<<16
        data += self.value<<24
        return data
    pass

#c Actions
class Actions:
    halt_capture = False
    record_data = False
    record_time = False
    record_invalidate = False
    capture_data = (False, False)
    def reg_value(self):
        data =  int(self.halt_capture)
        data += int(self.record_data)<<1
        data += int(self.record_time)<<2
        data += int(self.record_invalidate)<<3
        data += int(self.capture_data[0])<<4
        data += int(self.capture_data[1])<<5
        return data
    pass

#c TriggerSimple
class TriggerSimple:
    """Analyzer trace trigger configuration


    """
    data_src = (DataSrc.D0, DataSrc.D1)
    match_data_src = (MatchDataSrc.DATA, MatchDataSrc.DATA)
    byte_match = (SimpleByteMatch(), SimpleByteMatch(), SimpleByteMatch(), SimpleByteMatch())
    actions = [Actions(), Actions(), Actions(), Actions(), Actions(), Actions(), Actions(), Actions()]
    action_sets = [0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0]
    data_sources = [TraceDataSrc.D0, TraceDataSrc.D1]
    #f __init
    def __init__(self):
        pass
    #f reset
    def reset(self):
        pass
    #f apb_writes_control
    def apb_writes_control(self, map, enable, clear, start, stop, timer_divide):
        writes = []
        data = int(enable) + (int(clear) << 1) + (int(start) << 2) + (int(stop) << 3) + (timer_divide << 8)
        writes.append( (map.trigger_base, data ) )
        return writes
    #f apb_writes
    def apb_writes(self, map):
        writes = []
        srcs = self.data_src[0].value + (self.data_src[1].value << 8) + (self.match_data_src[0].value << 16) + (self.match_data_src[1].value << 24)
        writes.append( (map.trigger_srcs, srcs ) )
        writes.append( (map.trigger_match_byte_0, self.byte_match[0].reg_value() ) )
        writes.append( (map.trigger_match_byte_1, self.byte_match[1].reg_value() ) )
        writes.append( (map.trigger_match_byte_2, self.byte_match[2].reg_value() ) )
        writes.append( (map.trigger_match_byte_3, self.byte_match[3].reg_value() ) )
        ts0 = 0
        ts1 = 0
        for i in range(8):
            ts0 += self.action_sets[i]<<(4*i)
            ts1 += self.action_sets[i+8]<<(4*i)
            pass
        writes.append( (map.trigger_set_0,  ts0 ) )
        writes.append( (map.trigger_set_1,  ts1 ) )
        tas0 = 0
        tas1 = 0
        for i in range(4):
            tas0 += self.actions[i].reg_value()<<(8*i)
            tas1 += self.actions[i+4].reg_value()<<(8*i)
            pass
        writes.append( (map.trigger_actions_0,  tas0 ) )
        writes.append( (map.trigger_actions_1,  tas1 ) )
        return writes

    #f apply
    def apply(self, data):
        pass
    pass

