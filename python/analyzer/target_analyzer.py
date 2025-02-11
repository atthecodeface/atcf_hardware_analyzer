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

