#a Imports
from cdl.utils.csr   import Csr, CsrField, CsrFieldZero, Map, MapCsr, MapMap

#a CSRs for Ctl
class CtlStatusCsr(Csr):
    _fields = {0:  CsrField(width=24, name="count", brief="cnt", doc="24-bit count"),
               30: CsrField(name="selected", brief="sel", doc="Asserted if a target is selected"),
               31: CsrField(name="completed", brief="comp", doc="Asserted if the state machine has completed"),
              }
class CtlSelectCsr(Csr):
    _fields = {0:  CsrField(width=32, name="count", brief="cnt", doc="32-bit count"),
              }

class CtlSelectAtCsr(Csr):
    _fields = {0:  CsrField(width=32, name="count", brief="cnt", doc="32-bit count"),
              }

class CtlWriteDataCsr(Csr):
    _fields = {0:  CsrField(width=32, name="data", brief="data", doc="32-bit data"),
              }

class AnalyzerCtlAddressMap(Map):
    _map = [ MapCsr(reg=0, name="status", brief="status", csr=CtlStatusCsr, doc=""),
             MapCsr(reg=1, name="select", brief="sel", csr=CtlSelectCsr, doc="""
             Write data of 0 to select none; count will indicate length of enable chain
             Write data of 1<<31 to select run clear, counting until enable return is clear
             """),
             MapCsr(reg=2, name="select_at", brief="sat", csr=CtlSelectAtCsr, doc=""),
             MapCsr(reg=3, name="write_data", brief="wrd", csr=CtlWriteDataCsr, doc=""),
             ]
             

#a CSRs for Cfg
#c Filter
class FilterMaskCsr(Csr):
    _fields = {0:  CsrField(width=32, name="mask", brief="mask", doc="32-bit mask value"),
              }
class FilterMatchCsr(Csr):
    _fields = {0:  CsrField(width=32, name="match", brief="match", doc="32-bit match value"),
              }
class FilterBaseCsr(Csr):
    _fields = {0:  CsrField(width=1, name="enable", brief="en", doc="set to enable filter"),
               1:  CsrField(width=1, name="unchaning", brief="en", doc="set to accept unchanging values"),
              }
#c Trigger
class TriggerSimpleBaseCsr(Csr):
    _fields = {0:  CsrField(width=1, name="enable", brief="en", doc="Set to enable the trigger"),
               1:  CsrField(width=1, name="clear", brief="clr", doc="Set to clear the trigger"),
               2:  CsrField(width=1, name="start", brief="start", doc="Start the trigger"),
               3:  CsrField(width=1, name="stop", brief="stop", doc="Stop the trigger"),
               8:  CsrField(width=2, name="timer_divide", brief="tdiv", doc="Divider configuration for the timer value for the trigger"),
              }

class TriggerSimpleMatchDataCsr(Csr):
    _fields = {0:  CsrField(width=2, name="data_src_0", brief="d0", doc="Analyzer data source 0"),
               8:  CsrField(width=2, name="data_src_1", brief="d1", doc="Analyzer data source 1"),
               16:  CsrField(width=3, name="match_src_0", brief="md0", doc="Which data for byte source word 0"),
               24:  CsrField(width=3, name="match_src_1", brief="md1", doc="Which data for byte source word 1"),
              }

class TriggerSimpleMatchByteCsr(Csr):
    _fields = {0:  CsrField(width=1, name="ignore_valid", brief="iv", doc="Ignore the validity of the data"),
               8:  CsrField(width=3, name="byte_sel", brief="bs", doc="Which byte of 4 of the two data sources"),
               12:  CsrField(width=3, name="cond_sel", brief="cs", doc="Which condition - changing, posedge, negedge, valid"),
               16:  CsrField(width=8, name="mask", brief="mask", doc="Mask of bits that must match"),
               24:  CsrField(width=8, name="value", brief="val", doc="Value of bits that match"),
              }

class TriggerSimpleActionSetCsr(Csr):
    _fields = {0:  CsrField(width=32, name="action_sets", brief="action_sets", doc="Action sets"),
              }

class TriggerSimpleActionsCsr(Csr):
    _fields = {0:  CsrField(width=32, name="actions", brief="actions", doc="Actions"),
              }

class TriggerTraceSourceCsr(Csr):
    _fields = {0:  CsrField(width=3, name="data_source_0", brief="src0", doc="Data source for trace data 0"),
              8:  CsrField(width=3, name="data_source_1", brief="src1", doc="Data source for trace data 1"),
              16:  CsrField(width=3, name="data_source_2", brief="src2", doc="Data source for trace data 2"),
              24:  CsrField(width=3, name="data_source_3", brief="src3", doc="Data source for trace data 3"),
              }

class TriggerTraceOpCsr(Csr):
    _fields = {0:  CsrField(width=3, name="trace_op_0", brief="op0", doc="Trace op for capture 0"),
              8:  CsrField(width=3, name="trace_op_1", brief="op1", doc="Trace op for capture 1"),
              16:  CsrField(width=3, name="trace_op_2", brief="op2", doc="Trace op for capture 2"),
              24:  CsrField(width=3, name="trace_op_3", brief="op3", doc="Trace op for capture 3"),
              }

#c Address map
class AnalyzerCfgAddressMap(Map):
    _map = [ MapCsr(reg=0, name="filter_base", brief="fbase", csr=FilterBaseCsr, doc=""),
             MapCsr(reg=8, name="filter_mask0", brief="fmask0", csr=FilterMaskCsr, doc=""),
             MapCsr(reg=9, name="filter_mask1", brief="fmask1", csr=FilterMaskCsr, doc=""),
             MapCsr(reg=10, name="filter_mask2", brief="fmask2", csr=FilterMaskCsr, doc=""),
             MapCsr(reg=11, name="filter_mask3", brief="fmask3", csr=FilterMaskCsr, doc=""),
             MapCsr(reg=12, name="filter_match0", brief="fmatch0", csr=FilterMatchCsr, doc=""),
             MapCsr(reg=13, name="filter_match1", brief="fmatch1", csr=FilterMatchCsr, doc=""),
             MapCsr(reg=14, name="filter_match2", brief="fmatch2", csr=FilterMatchCsr, doc=""),
             MapCsr(reg=15, name="filter_match3", brief="fmatch3", csr=FilterMatchCsr, doc=""),

             MapCsr(reg=16, name="trigger_base", brief="tbase", csr=TriggerSimpleBaseCsr, doc=""),
             MapCsr(reg=17, name="trigger_srcs", brief="tsrc", csr=TriggerSimpleMatchDataCsr, doc=""),
             MapCsr(reg=20, name="trigger_match_byte_0", brief="tmb0", csr=TriggerSimpleMatchByteCsr, doc=""),
             MapCsr(reg=21, name="trigger_match_byte_1", brief="tmb1", csr=TriggerSimpleMatchByteCsr, doc=""),
             MapCsr(reg=22, name="trigger_match_byte_2", brief="tmb2", csr=TriggerSimpleMatchByteCsr, doc=""),
             MapCsr(reg=23, name="trigger_match_byte_3", brief="tmb3", csr=TriggerSimpleMatchByteCsr, doc=""),
             MapCsr(reg=24, name="trigger_set_0", brief="tset0", csr=TriggerSimpleActionSetCsr, doc="Which actions to use for match_bytes bus 0 to 7; three bits each"),
             MapCsr(reg=25, name="trigger_set_1", brief="tset1", csr=TriggerSimpleActionSetCsr, doc="Which actions to use for match_bytes bus 8 to 15; three bits each"),
             MapCsr(reg=26, name="trigger_actions_0", brief="tas0", csr=TriggerSimpleActionsCsr, doc="8 action sets (halt capture, record data, record time, record invalidate)"),
             MapCsr(reg=27, name="trigger_actions_1", brief="tas1", csr=TriggerSimpleActionsCsr, doc="data capture"),
             MapCsr(reg=28, name="trace_data_source", brief="tds", csr=TriggerTraceSourceCsr, doc="trace data source capture"),
             MapCsr(reg=29, name="trace_op", brief="tds", csr=TriggerTraceOpCsr, doc="trace operations"),
             ]
             
#a CSRs for TbSrc
class TbSrcConfigCsr(Csr):
    _fields = {0:  CsrField(width=4, name="tgt_mode", brief="tgt", doc="Invalid, Valid, ..."),
               16: CsrField(width=3, name="op_mode0", brief="op0", doc="Op mode for data 0"),
               20: CsrField(width=3, name="op_mode1", brief="op1", doc="Op mode for data 1"),
               24: CsrField(width=3, name="op_mode2", brief="op2", doc="Op mode for data 2"),
               28: CsrField(width=3, name="op_mode3", brief="op3", doc="Op mode for data 3"),
              }
class TbSrcDataCsr(Csr):
    _fields = {0:  CsrField(width=32, name="data", brief="data", doc="32-bit data value"),
              }
class TbAnalyzerSrcAddressMap(Map):
    _map = [ MapCsr(reg=0, name="config", brief="cfg", csr=TbSrcConfigCsr, doc=""),
             MapCsr(reg=4, name="data0", brief="d0", csr=TbSrcDataCsr, doc=""),
             MapCsr(reg=5, name="data1", brief="d1", csr=TbSrcDataCsr, doc=""),
             MapCsr(reg=6, name="data2", brief="d2", csr=TbSrcDataCsr, doc=""),
             MapCsr(reg=7, name="data3", brief="d3", csr=TbSrcDataCsr, doc=""),
             ]
             
#c TbApbAddressMap
class TbApbAddressMap(Map):
    _width=32
    _select=0
    _address=0
    _shift=0
    _address_size=0
    _map=[MapMap(offset=0x000, name="analyzer_cfg", map=AnalyzerCfgAddressMap),
          MapMap(offset=0x400, name="analyzer_ctl", map=AnalyzerCtlAddressMap),
          MapMap(offset=0xc00, name="analyzer_src", map=TbAnalyzerSrcAddressMap),
         ]
    pass

