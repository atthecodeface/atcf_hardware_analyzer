#a Copyright
#  
#  This file 'test_dprintf.py' copyright Gavin J Stark 2017-2020
#  
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

#a Imports
from regress.apb.structs import t_apb_request, t_apb_response
from regress.apb.bfm     import ApbMaster
from queue import Queue
from regress.utils import t_dprintf_req_4, t_dprintf_byte, Dprintf, t_dbg_master_request, t_dbg_master_response, DprintfBus, SramAccessBus, SramAccessRead, SramAccessWrite, DbgMaster, DbgMasterMuxScript, DbgMasterSramScript, DbgMasterFifoScript, FifoStatus, t_sram_access_req, t_sram_access_resp
from regress.analyzer import target_analyzer_ctl
from cdl.utils   import csr
from cdl.sim     import ThExecFile, LogEventParser
from cdl.sim     import HardwareThDut
from cdl.sim     import TestCase
from typing import Optional

#c ApbAddressMap
class ApbAddressMap(csr.Map):
    _width=32
    _select=0
    _address=0
    _shift=0
    _address_size=0
    _map=[csr.MapMap(offset=0, name="analyzer_ctl", map=target_analyzer_ctl.AnalyzerCtlAddressMap),
         ]
    pass

#c AnalyzerCtlTest_Base
class AnalyzerCtlTest_Base(ThExecFile):
    th_name = "Utils dprintf test harness"
    sram_inter_delay = 0
    # This can be set at initialization time to reduce the number of explicit test cases
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        pass
    #f exec_init
    def exec_init(self) -> None:
        self.die_event         = self.sim_event()
        super().exec_init()
        pass
    #f run__init
    def run__init(self) -> None:
        self.apb = ApbMaster(self, "apb_request",  "apb_response")
        self.apb_map = ApbAddressMap()
        self.analyzer_map    = self.apb_map.analyzer_ctl
        self.analyzer_status = self.apb.reg(self.analyzer_map.status)
        self.analyzer_select = self.apb.reg(self.analyzer_map.select)
        self.analyzer_select_at = self.apb.reg(self.analyzer_map.select_at)
        self.analyzer_write_data = self.apb.reg(self.analyzer_map.write_data)
        self.bfm_wait(10)
        pass
    #f run
    def run(self) -> None:
        self.bfm_wait(4)
        self.die_event.reset()

        self.bfm_wait(4)
        x = self.analyzer_status.read()
        self.compare_expected("Status",0,x)

        self.analyzer_select.write(0)
        self.bfm_wait(100)
        x = self.analyzer_status.read()
        self.compare_expected("Status",0x8000001c,x)

        self.analyzer_select.write(0x80000000)
        self.bfm_wait(100)
        x = self.analyzer_status.read()
        self.compare_expected("Status",0x8000001c,x)

        # Enable tgt 4 (3 is at 9, 2 is at 6, etc)
        self.analyzer_select_at.write(12)
        x = self.analyzer_status.read() & 0x80000000
        self.compare_expected("Status",0,x)
        self.bfm_wait(100)
        x = self.analyzer_status.read() & 0x80000000
        self.compare_expected("Status",0x80000000,x)

        # Write 0x94 to tgt 4 (nybbles are reversed)
        self.analyzer_write_data.write(73)

        self.analyzer_select.write(0x80000000)
        self.bfm_wait(100)
        x = self.analyzer_status.read()
        self.compare_expected("Status",0x8000001c,x)

        self.bfm_wait_until_test_done(100)
        self.die_event.fire()
        self.bfm_wait(10)
        pass
    #f run__finalize
    def run__finalize(self) -> None:
        self.passtest("Test completed")
        pass
    pass

#c AnalyzerCtlTest_0
class AnalyzerCtlTest_0(AnalyzerCtlTest_Base):
    pass

#a Hardware and test instantiation
#c AnalyzerCtlHardware
class AnalyzerCtlHardware(HardwareThDut):
    clock_desc = [("clk",(0,2,2)),
    ]
    reset_desc = {"name":"reset_n", "init_value":0, "wait":5}
    module_name = "tb_analyzer_ctl"
    dut_inputs  = {"apb_request":t_apb_request,
    }
    dut_outputs = {"apb_response":t_apb_response,
    }
    loggers = { # "dprintf": {"modules":"dut.dut", "verbose":1}
                }
    pass

#c TestAnalyzerCtl
class TestAnalyzerCtl(TestCase):
    hw = AnalyzerCtlHardware
    _tests = {"0": (AnalyzerCtlTest_0, 1*1000, {}),
              "smoke": (AnalyzerCtlTest_0, 2*1000, {}),
    }

