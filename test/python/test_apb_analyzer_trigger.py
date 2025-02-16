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
    test_filter = Filter((1,0,0,0), (1,0,0,0), None, (12,0,0,0))
    test_trace = TraceCfg()
    num_data = 50
    src = AnalyzerSrc([1,2,3,4])
    timeout = 300
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

        self.verbose.info("Setting filter cfg")

        t = TriggerSimple(
            data_srcs = ("d0", "d1"),
            trace_data_srcs=["d0", "d1"],
            trace_ops=["push", "write"],
        )
        t.byte_match[0].value = 0xff
        t.action_sets[15] = 1
        t.actions[1].record_time = True
        t.actions[1].capture_data = (True, True)
                        
        writes = []
        writes += t.apb_writes(self.apb_map.analyzer_cfg)
        writes += t.apb_writes_control(self.apb_map.analyzer_cfg, enable=0, clear=1, start=0, stop=0, timer_divide=0)
        writes += t.apb_writes_control(self.apb_map.analyzer_cfg, enable=1, clear=1, start=0, stop=0, timer_divide=0)
        writes += t.apb_writes_control(self.apb_map.analyzer_cfg, enable=1, clear=0, start=0, stop=0, timer_divide=0)
        writes += t.apb_writes_control(self.apb_map.analyzer_cfg, enable=1, clear=0, start=1, stop=0, timer_divide=0)
        for (r,wd) in writes:
            self.apb.reg(r).write(wd)
            pass

        for (r,wd) in self.test_filter.apb_writes(self.apb_map.analyzer_cfg):
            self.apb.reg(r).write(wd)
            pass

        for (r,wd) in self.test_trace.apb_writes(self.apb_map.analyzer_cfg):
            self.apb.reg(r).write(wd)
            pass

        self.verbose.info("Configure source")
        for (r,wd) in self.src.apb_writes(self.apb_map.analyzer_src):
            self.apb.reg(r).write(wd)
            pass

        t.reset()
        expected_data = []
        while len(expected_data) < self.num_data:
            d = self.src.next_valid()
            valid = self.test_filter.apply(d)
            trace = t.apply(d, valid)
            if trace is not None:
                expected_data.append(trace)
                pass
            pass

        trace_data = []
        time = 0
        while len(trace_data) < self.num_data:
            self.bfm_wait(1)
            time += 1
            if time > self.timeout:
                self.failtest(f"Timeout waiting for trace data {len(trace_data)}")
                break
            if self.analyzer_trace_op__op_valid.value() != 0:
                dout = (self.analyzer_trace_op__op_valid.value(),
                        self.analyzer_trace_op__op_0.value(),
                        self.analyzer_trace_op__op_1.value(),
                        self.analyzer_data_triggered__data_0.value(),
                        self.analyzer_data_triggered__data_1.value(),
                        self.analyzer_data_triggered__data_2.value(),
                        self.analyzer_data_triggered__data_3.value(),
                        )
                trace_data.append(dout)
                pass
            pass

        self.verbose.info("Check data out")
        for i in range(len(trace_data)):
            e = expected_data[i]
            f = trace_data[i]
            self.compare_expected(f"Filter out {i} data 0", e[0], f[0])
            self.compare_expected(f"Filter out {i} data 1", e[1], f[1])
            self.compare_expected(f"Filter out {i} data 2", e[2], f[2])
            self.compare_expected(f"Filter out {i} data 3", e[3], f[3])
            self.compare_expected(f"Filter out {i} data 4", e[4], f[4])
            self.compare_expected(f"Filter out {i} data 5", e[5], f[5])
            self.compare_expected(f"Filter out {i} data 6", e[6], f[6])
            pass
        
        self.bfm_wait_until_test_done(100)
        self.die_event.fire()
        self.bfm_wait(10)
        self.bfm_wait(10000)
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
    _tests = {"0": (ApbAnalyzerTest_0, 1*1000, {}),
              "smoke": (ApbAnalyzerTest_0, 80*1000, {}),
    }

