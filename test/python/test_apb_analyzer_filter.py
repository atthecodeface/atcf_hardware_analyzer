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
from regress.analyzer import TbApbAddressMap, Filter, t_analyzer_data4, FilterAcceptAll, FilterChanging

from cdl.utils   import csr
from cdl.sim     import ThExecFile, LogEventParser
from cdl.sim     import HardwareThDut
from cdl.sim     import TestCase
from typing import Optional

#c ApbAnalyzerTest_Base
class ApbAnalyzerTest_Base(ThExecFile):
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
        self.apb_map = TbApbAddressMap()
        self.analyzer_map    = self.apb_map.analyzer_cfg
        self.bfm_wait(10)
        pass
    #f run
    def run(self) -> None:
        self.verbose.message(f"Test {self.__class__.__name__}")
        self.verbose.set_level(self.verbose.level_info)

        self.apb.reg(self.apb_map.analyzer_ctl.select).write(1<<31)
        self.bfm_wait(10)
        status = self.apb_map.analyzer_ctl.status
        # assert top bit set
        print("%08x"%self.apb.reg(status).read())

        self.apb.reg(self.apb_map.analyzer_ctl.select_at).write(0)
        self.bfm_wait(10)
        # assert top bit set
        print("%08x"%self.apb.reg(status).read())

        self.apb.reg(self.apb_map.analyzer_ctl.write_data).write(0)
        self.bfm_wait(10)

        x = FilterAcceptAll()
        writes = x.apb_writes(self.apb_map.analyzer_cfg)
        for (reg, value) in writes:
            self.apb.reg(reg).write(value)
            pass
        
        self.bfm_wait(4)

        x = FilterChanging()
        writes = x.apb_writes(self.apb_map.analyzer_cfg)
        for (reg, value) in writes:
            self.apb.reg(reg).write(value)
            pass
        
        self.bfm_wait(4)

        x = Filter(mc=[4,0,0,0])
        writes = x.apb_writes(self.apb_map.analyzer_cfg)
        for (reg, value) in writes:
            self.apb.reg(reg).write(value)
            pass
        
        self.bfm_wait(4)
        self.die_event.reset()

        self.verbose.info("Reading status, should be 0 to start with")

        self.verbose.info("Selected; write the data out")
        self.bfm_wait_until_test_done(100)
        self.die_event.fire()
        self.bfm_wait(10)
        pass
    #f run__finalize
    def run__finalize(self) -> None:
        self.passtest("Test completed")
        pass
    pass

#c ApbAnalyzerTest_0
class ApbAnalyzerTest_0(ApbAnalyzerTest_Base):
    pass

#a Hardware and test instantiation
#c ApbAnalyzerHardware
class ApbAnalyzerHardware(HardwareThDut):
    clock_desc = [("clk",(0,2,2)),
    ]
    reset_desc = {"name":"reset_n", "init_value":0, "wait":5}
    module_name = "tb_analyzer_filter"
    dut_inputs  = {"apb_request":t_apb_request,
    }
    dut_outputs = {"apb_response":t_apb_response,
                   "analyzer_data4":t_analyzer_data4,
                   "analyzer_data_filtered":t_analyzer_data4,
    }
    loggers = { # "dprintf": {"modules":"dut.dut", "verbose":1}
                }
    pass

#c TestApbAnalyzer
class TestApbAnalyzer(TestCase):
    hw = ApbAnalyzerHardware
    _tests = {"0": (ApbAnalyzerTest_0, 2*1000, {}),
    }

