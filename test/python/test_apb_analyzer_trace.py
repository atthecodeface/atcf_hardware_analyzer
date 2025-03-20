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
from regress.analyzer import t_analyzer_data4, t_analyzer_trace_op4
from regress.analyzer import TbApbAddressMap, Filter, FilterAcceptAll, FilterChanging, TraceCfg
from regress.analyzer import AnalyzerSrc, TriggerSimple

from cdl.utils   import csr
from cdl.sim     import ThExecFile, LogEventParser
from cdl.sim     import HardwareThDut
from cdl.sim     import TestCase
from typing import Optional

#c ApbAnalyzerTest_Base
class ApbAnalyzerTest_Base(ThExecFile):
    
    th_name = "Apb target analyzer trigger test harness"
    tgt_mux_sel = 0
    test_filter = Filter((1,0,0,0), (1,0,0,0), None, None)
    test_trace = TraceCfg()
    num_triggers = 50
    src = AnalyzerSrc([1,2,3,4])
    timeout = 300
    trigger = TriggerSimple(
        data_srcs = ("d0", "d1"),
        trace_data_srcs=["d0", "d1"],
        trace_ops=["push", "write"],
    )
    trigger.byte_match[0].value = 0xff
    trigger.action_sets[15] = 1
    trigger.actions[1].record_time = True
    trigger.actions[1].capture_data = (True, True)

    #f __init__
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
        self.verbose.set_level(self.verbose.level_info)
        self.verbose.message(f"Test {self.__class__.__name__}")

        self.apb = ApbMaster(self, "apb_request",  "apb_response")
        self.apb_map = TbApbAddressMap()
        self.bfm_wait(10)

        self.verbose.message(f"Clear control")
        self.apb.reg(self.apb_map.analyzer_ctl.select).write(1<<31)

        self.bfm_wait(4)

        self.verbose.message(f"Enable src as analyzer tgt")
        self.apb.reg(self.apb_map.analyzer_ctl.select_at).write(0)

        self.bfm_wait(4)

        status = self.apb.reg(self.apb_map.analyzer_ctl.status).read()
        self.compare_expected("Completed and selected",status>>30,3)

        self.bfm_wait(4)

        self.verbose.message(f"Set mux to drive id")
        self.apb.reg(self.apb_map.analyzer_ctl.wrd).write(self.tgt_mux_sel)
        
        pass
    #f run
    def run(self) -> None:

        self.verbose.info("Setting up test")

        writes = []
        writes += self.trigger.apb_writes(self.apb_map.analyzer_cfg)
        writes += self.trigger.apb_writes_control(self.apb_map.analyzer_cfg, enable=0, clear=1, start=0, stop=0, timer_divide=0)
        writes += self.trigger.apb_writes_control(self.apb_map.analyzer_cfg, enable=1, clear=1, start=0, stop=0, timer_divide=0)
        writes += self.trigger.apb_writes_control(self.apb_map.analyzer_cfg, enable=1, clear=0, start=0, stop=0, timer_divide=0)
        writes += self.trigger.apb_writes_control(self.apb_map.analyzer_cfg, enable=1, clear=0, start=1, stop=0, timer_divide=0)
        writes += self.test_filter.apb_writes(self.apb_map.analyzer_cfg)
        writes += self.test_trace.apb_writes(self.apb_map.analyzer_cfg)
        writes += self.src.apb_writes(self.apb_map.analyzer_src)
        
        for (r,wd) in writes:
            self.apb.reg(r).write(wd)
            pass

        triggered_count = 0
        time = 0
        while triggered_count < self.num_triggers:
            self.bfm_wait(1)
            time += 1
            if time > self.timeout:
                self.failtest(f"Timeout waiting for trigger data {triggered_count}")
                break
            if self.analyzer_trace_op__op_valid.value() != 0:
                triggered_count += 1
                pass
            pass

        self.bfm_wait(10)
        
        self.verbose.info("Check data out")
        fs0 = self.apb.reg(self.apb_map.analyzer_trace.fifo_status_0).read()
        self.verbose.info(f"Read fifo status 0 {fs0} (using as FIFO so not empty)")
        fs1 = self.apb.reg(self.apb_map.analyzer_trace.fifo_status_1).read()
        self.verbose.info(f"Read fifo status 1 {fs1} (using as histogram so empty)")

        self.compare_expected("Fifo 0 should be not empty",fs0&1, 0)
        self.compare_expected("Fifo 1 should be empty",fs1, 1)

        d0 = self.apb.reg(self.apb_map.analyzer_trace.pop0).read()
        self.compare_expected("Data captured",d0,3)

        d0 = self.apb.reg(self.apb_map.analyzer_trace.pop0).read()
        self.compare_expected("Data captured",d0,5)
        d0 = self.apb.reg(self.apb_map.analyzer_trace.pop0).read()
        self.compare_expected("Data captured",d0,7)
        d0 = self.apb.reg(self.apb_map.analyzer_trace.pop0).read()
        self.compare_expected("Data captured",d0,9)

        self.verbose.info("Data compared")
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
    module_name = "tb_analyzer"
    dut_inputs  = {"apb_request":t_apb_request,
    }
    dut_outputs = {"apb_response":t_apb_response,
                   "analyzer_data4":t_analyzer_data4,
                   "analyzer_data_filtered":t_analyzer_data4,
                   "analyzer_trace_op":t_analyzer_trace_op4,
                   "analyzer_data_triggered":t_analyzer_data4,
    }
    loggers = { # "dprintf": {"modules":"dut.dut", "verbose":1}
                }
    pass

#c TestApbAnalyzer
class TestApbAnalyzer(TestCase):
    hw = ApbAnalyzerHardware
    _tests = {"0": (ApbAnalyzerTest_0, 2*1000, {}),
              "smoke": (ApbAnalyzerTest_0, 80*1000, {}),
    }

