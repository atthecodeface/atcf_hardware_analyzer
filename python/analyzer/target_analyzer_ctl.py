#a Imports
from cdl.utils.csr   import Csr, CsrField, CsrFieldZero, Map, MapCsr

#a CSRs
class StatusCsr(Csr):
    _fields = {0:  CsrField(width=24, name="count", brief="cnt", doc="24-bit count"),
               31: CsrField(name="completed", brief="comp", doc="Asserted if the sate machine has completed"),
              }
class SelectCsr(Csr):
    _fields = {0:  CsrField(width=32, name="count", brief="cnt", doc="32-bit count"),
              }

class SelectAtCsr(Csr):
    _fields = {0:  CsrField(width=32, name="count", brief="cnt", doc="32-bit count"),
              }

class WriteDataCsr(Csr):
    _fields = {0:  CsrField(width=32, name="data", brief="data", doc="32-bit data"),
              }

class AnalyzerCtlAddressMap(Map):
    _map = [ MapCsr(reg=0, name="status", brief="status", csr=StatusCsr, doc=""),
             MapCsr(reg=1, name="select", brief="sel", csr=SelectCsr, doc=""),
             MapCsr(reg=2, name="select_at", brief="sat", csr=SelectAtCsr, doc=""),
             MapCsr(reg=3, name="write_data", brief="wrd", csr=WriteDataCsr, doc=""),
             ]
             
