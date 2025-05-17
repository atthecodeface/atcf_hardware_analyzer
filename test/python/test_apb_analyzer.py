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
from regress.utils import t_dprintf_req_4, t_dprintf_byte, Dprintf, t_dbg_master_request, t_dbg_master_response, DprintfBus, SramAccessBus, SramAccessRead, SramAccessWrite, DbgMaster, DbgMasterMuxScript, DbgMasterSramScript, DbgMasterFifoScript, FifoStatus, t_sram_access_req, t_sram_access_resp
from regress.analyzer import t_analyzer_data4, t_analyzer_trace_op4
from regress.analyzer import TbApbAddressMap, Filter, FilterAcceptAll, FilterChanging, TraceCfg
from regress.analyzer import AnalyzerSrc, TriggerSimple, SimpleByteMatch

from cdl.utils   import csr
from cdl.sim     import ThExecFile, LogEventParser
from cdl.sim     import HardwareThDut
from cdl.sim     import TestCase
from typing import Optional

#c ApbAnalyzerTest_Base
class ApbAnalyzerTest_Base(ThExecFile):
    th_name = "Simple Analyzer Test Harness"

    th_name = "Dbg script analyzer trigger test harness"
    tgt_mux_sel = 0
    test_filter = Filter((1,0,0,0), (1,0,0,0), None, None)
    test_trace = TraceCfg()
    num_triggers = 50
    # Set mode 1 with 100 valid
    src = AnalyzerSrc(data=[1,2,3,4], data_cfg=[1,1,1,1], count=10, tgt_valid_if_count_nz=1)
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
    expected = [3,5,7,9]
    expected_fs = (0,1)

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
        self.verbose.message(f"Test {self.__class__.__name__}")
        self.verbose.set_level(self.verbose.level_info)

        self.apb = ApbMaster(self, "apb_request",  "apb_response")
        self.apb_map = TbApbAddressMap()
        self.bfm_wait(10)
        pass
    #f run
    def run(self) -> None:

        self.verbose.info("Setting up test")

        self.apb.reg(self.apb_map.analyzer_ctl.select).write(1<<31)
        self.bfm_wait(10)
        self.apb.reg(self.apb_map.analyzer_ctl.select_at).write(0)
        self.bfm_wait(10)
        self.apb.reg(self.apb_map.analyzer_ctl.status).read()
        self.bfm_wait(10)
        self.apb.reg(self.apb_map.analyzer_ctl.wrd).write(self.tgt_mux_sel)
        self.bfm_wait(10)
                   
        writes = []
        writes += self.trigger.apb_writes(self.apb_map.analyzer_cfg)
        writes += self.trigger.apb_writes_control(self.apb_map.analyzer_cfg, enable=0, clear=1, start=0, stop=0, timer_divide=0)
        writes += self.trigger.apb_writes_control(self.apb_map.analyzer_cfg, enable=1, clear=1, start=0, stop=0, timer_divide=0)
        writes += self.trigger.apb_writes_control(self.apb_map.analyzer_cfg, enable=1, clear=0, start=0, stop=0, timer_divide=0)
        writes += self.trigger.apb_writes_control(self.apb_map.analyzer_cfg, enable=1, clear=0, start=1, stop=0, timer_divide=0)
        writes += self.trigger.apb_writes_control(self.apb_map.analyzer_cfg, enable=1, clear=0, start=0, stop=0, timer_divide=0)
        writes += self.test_filter.apb_writes(self.apb_map.analyzer_cfg)
        writes += self.test_trace.apb_writes(self.apb_map.analyzer_cfg)
        # Enable the source last!
        writes += self.src.apb_writes(self.apb_map.analyzer_src)

        self.verbose.message(f"Clear control")
        self.verbose.message(f"Enable src as analyzer tgt")
        self.verbose.message(f"Set mux to drive id")
        for (r,wd) in writes:
            self.apb.reg(r).write(wd)
            pass

        self.bfm_wait(200)

        stop_writes = self.trigger.apb_writes_control(self.apb_map.analyzer_cfg, enable=1, clear=0, start=0, stop=1, timer_divide=0)
        stop_writes += self.trigger.apb_writes_control(self.apb_map.analyzer_cfg, enable=0, clear=0, start=0, stop=0, timer_divide=0)
        for (r,wd) in stop_writes:
            self.apb.reg(r).write(wd)
            pass

        
        fs0 = self.apb.reg(self.apb_map.analyzer_trace.fifo_status_0).read()
        self.verbose.info(f"Read fifo status 0 {fs0} (using as FIFO so not empty)")
        fs1 = self.apb.reg(self.apb_map.analyzer_trace.fifo_status_1).read()
        self.verbose.info(f"Read fifo status 1 {fs1} (using as histogram so empty)")

        self.compare_expected("Fifo 0 status",self.expected_fs[0],fs0)
        self.compare_expected("Fifo 1 status",self.expected_fs[1],fs1)

        for e in self.expected:
            d0 = self.apb.reg(self.apb_map.analyzer_trace.pop0).read()
            self.compare_expected("Data captured",e,d0)
            pass

        self.bfm_wait_until_test_done(200)
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
    th_name = "Dbg script analyzer trigger test harness"
    tgt_mux_sel = 0
    test_filter = Filter((1,0,0,0), (1,0,0,0), None, None)
    test_trace = TraceCfg()
    num_triggers = 50
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
    expected = [3,5,7,9]
    pass

#c ApbAnalyzerTest_1
class ApbAnalyzerTest_1(ApbAnalyzerTest_Base):
    th_name = "Testing continuous unstopped capture"
    tgt_mux_sel = 0
    test_filter = Filter(None, None, None, None)
    test_trace = TraceCfg()
    num_triggers = 50
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
    expected = [2,3,4,5,6,7,8,9]
    pass

#c ApbAnalyzerTest_2
class ApbAnalyzerTest_2(ApbAnalyzerTest_Base):
    th_name = "Testing continuous capture with halt"
    tgt_mux_sel = 0
    test_filter = Filter(None, None, None, None)
    test_trace = TraceCfg()
    num_triggers = 50
    timeout = 300
    trigger = TriggerSimple(
        data_srcs = ("d0", "d1"),
        trace_data_srcs=["d0", "d1"],
        trace_ops=["push", "write"],
    )
    trigger.byte_match[0] = SimpleByteMatch().with_byte_sel(0)
    trigger.action_sets[15] = 1
    trigger.actions[1].record_time = True
    trigger.actions[1].halt_capture = True
    trigger.actions[1].capture_data = (True, True)
    expected = [5]
    expected_fs = ((4*1)<<4,1)
    pass

#c ApbAnalyzerTest_3
class ApbAnalyzerTest_3(ApbAnalyzerTest_Base):
    th_name = "Testing one in 16 capture with halt"
    tgt_mux_sel = 0
    test_filter = Filter(None, None, None, None)
    test_trace = TraceCfg()
    num_triggers = 50
    timeout = 300
    trigger = TriggerSimple(
        data_srcs = ("d0", "d1"),
        trace_data_srcs=["d0", "d1"],
        trace_ops=["push", "write"],
    )
    trigger.byte_match[0] = SimpleByteMatch().with_byte_sel(0).with_match_value(mask=0xf, value = 5)
    trigger.action_sets[15] = 1
    trigger.actions[1].record_time = True
    trigger.actions[1].halt_capture = True
    trigger.actions[1].capture_data = (True, True)
    expected = [5]
    expected_fs = ((4*1)<<4,1)
    pass

#a Hardware and test instantiation
#c ApbAnalyzerHardware
class ApbAnalyzerHardware(HardwareThDut):
    clock_desc = [("clk",(0,2,2)),
    ]
    reset_desc = {"name":"reset_n", "init_value":0, "wait":5}
    module_name = "tb_analyzer_simple"
    dut_inputs  = {"apb_request":t_apb_request,
    }
    dut_outputs = {"apb_response":t_apb_response,
                   "analyzer_data4":t_analyzer_data4,
    }
    loggers = { # "dprintf": {"modules":"dut.dut", "verbose":1}
                }
    pass

#c TestApbAnalyzer
class TestApbAnalyzer(TestCase):
    hw = ApbAnalyzerHardware
    _tests = {"0": (ApbAnalyzerTest_0, 2*1000, {}),
              "1": (ApbAnalyzerTest_1, 2*1000, {}),
              "smoke": (ApbAnalyzerTest_2, 2*1000, {}),
    }

