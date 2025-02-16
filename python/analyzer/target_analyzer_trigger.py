#a Documentation
"""
Classes that contain analyzer trigger configuration and operation
"""

#a Imports
from enum import Enum
from cdl.utils.csr   import Csr, CsrField, CsrFieldZero, Map, MapCsr

#a Enum classes
#c DataSrc
class DataSrc(Enum):
    D0 = 0
    D1 = 1
    D2 = 2
    D3 = 3
    def select_data(self, d):
        return d[self.value]
    pass

#c MatchDataSrc
class MatchDataSrc(Enum):
    TIME = 0
    TIME_DELTA = 1
    RECORDED_DATA = 2
    DATA_DELTA= 3
    DATA = 4
    def select(self, trigger, d, is_valid):
        return [(trigger.time, True),
                (trigger.time-trigger.recorded_time, True),
                (trigger.recorded_data, True),
                (trigger.recorded_data ^ d, is_valid),
                (d, is_valid)][self.value]
         
    pass

#c TraceDataSrc
class TraceDataSrc(Enum):
    """
    Data source for an output of the trigger into the trace
    """
    TIME = 0
    TIME_DELTA = 1
    RECORDED_DATA = 2
    D0 = 3
    D1 = 4
    D2 = 5
    D3 = 6
    pass

#c TraceDataOp
class TraceDataOp(Enum):
    """
    Trace data operation if actions indicate it
    """
    PUSH = 0
    WRITE = 1
    INC = 2
    SUM = 3
    MIN = 4
    MAX = 5
    MIN_MAX = 6
    INC_ADD = 7
    pass

#a SimpleByteMatch classes
#c SimpleByteMatchCond
class SimpleByteMatchCond(Enum):
    CHANGING = 3
    NEGEDGE = 2
    POSEDGE = 1
    MATCH = 0
    def result(self, matched, last_matched):
        match self:
            case SimpleByteMatchCond.MATCH: return matched
            case SimpleByteMatchCond.POSEDGE: return matched and not last_matched
            case SimpleByteMatchCond.NEGEDGE: return not matched and last_matched
            case SimpleByteMatchCond.CHANGING: return matched != last_matched
        pass
    pass

#c SimpleByteMatch
class SimpleByteMatch:
    ignore_valid = False
    byte_sel = 0
    mask = 0
    value = 0
    cond_sel = SimpleByteMatchCond.MATCH
    def reset(self):
        self.one_must_be_nonzero = self.value & ~self.mask
        self.must_match_value = self.value & self.mask
        self.last_matched = False
        pass
    def reg_value(self):
        data = int(self.ignore_valid)
        data += self.byte_sel<<8
        data += self.cond_sel.value<<12
        data += self.mask<<16
        data += self.value<<24
        return data
    def do_match(self, md0, md1):
        d = md0
        if self.byte_sel >= 4: d = md1
        if not self.ignore_valid and not d[1]:
            return False
        bd = (md0[0] >> ((self.byte_sel & 3) * 8)) & 0xff
        mismatch = False
        if self.one_must_be_nonzero != 0:
            if (bd & self.one_must_be_nonzero) == 0:
                mismatch = True
                pass
            pass
        if bd & self.mask != self.must_match_value:
            mismatch = True
            pass
        matched = not mismatch
        result = self.cond_sel.result(matched, self.last_matched)
        self.last_matched = matched
        return result
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

#a Trigger classes
#c TriggerSimple
class TriggerSimple:
    """Analyzer trace trigger configuration


    """
    data_src = (DataSrc.D0, DataSrc.D1)
    match_data_src = (MatchDataSrc.DATA, MatchDataSrc.DATA)
    byte_match = (SimpleByteMatch(), SimpleByteMatch(), SimpleByteMatch(), SimpleByteMatch())
    actions = [Actions(), Actions(), Actions(), Actions(), Actions(), Actions(), Actions(), Actions()]
    action_sets = [0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0]
    trace_data_sources = [TraceDataSrc.D0, TraceDataSrc.D1, TraceDataSrc.D2, TraceDataSrc.D3 ]
    trace_ops = [TraceDataOp.PUSH] * 4
    #f __init
    def __init__(self, data_srcs=None, match_data_srcs=None, trace_ops=None, trace_data_srcs=None):
        self.data_srcs = self.as_enums(DataSrc, data_srcs, "d0", 4)
        self.match_data_src = self.as_enums(MatchDataSrc, match_data_srcs, "data", 2)
        self.trace_data_sources = self.as_enums(TraceDataSrc, trace_data_srcs, "d0", 4)
        self.trace_ops = self.as_enums(TraceDataOp, trace_ops, "push", 4)
        pass

    #f as_enums
    def as_enums(self, enum_type, values, default, n,):
        result = [enum_type[default.upper()]] * n
        if values is None:
            return result
        i = 0
        for v in values:
            if i>=n:
                raise Exception("Too many values provided in seting trigger")
            try:
                value = enum_type[v.upper()]
                result[i] = value
                pass
            except:
                raise Exception(f"Unknown value type {t} for {enum_type}")
            i += 1
            pass
        return result

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
        tds = 0
        for i in range(4):
            tds += self.trace_data_sources[i].value<<(8*i)
            pass
        writes.append( (map.trace_data_source,  tds ) )
        tops = 0
        for i in range(4):
            tops += self.trace_ops[i].value<<(8*i)
            pass
        writes.append( (map.trace_op,  tops ) )
        return writes

    #f reset
    def reset(self):
        self.time = 0
        self.recorded_data = 0
        self.recorded_time = 0
        for d in self.byte_match:
            d.reset()
            pass
        pass
    #f apply
    def apply(self, data, is_valid:True):
        td0 = self.data_src[0].select_data(data)
        td1 = self.data_src[1].select_data(data)
        md0 = self.match_data_src[0].select(self, td0, is_valid)
        md1 = self.match_data_src[1].select(self, td1, is_valid)
        matched = 0
        for i in range(4):
            if self.byte_match[i].do_match(md0, md1):
                matched += (1<<i)
                pass
            pass
        action_set = self.action_sets[matched]
        actions = self.actions[action_set]
        op_valid = 0
        if actions.capture_data[0]: op_valid += 1
        if actions.capture_data[1]: op_valid += 2
        if op_valid != 0:
            return (op_valid, self.trace_ops[0].value, self.trace_ops[1].value, data[0], data[1], 0, 0)
        return None
    pass

