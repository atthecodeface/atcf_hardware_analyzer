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
from queue import Queue
from regress.utils import t_fifo_status
from regress.analyzer import t_analyzer_data4, t_analyzer_filter_cfg, t_access_combs, t_analyzer_trace_cfg_fifo

from cdl.sim     import ThExecFile, LogEventParser
from cdl.sim     import HardwareThDut
from cdl.sim     import TestCase
from typing import Optional

#c Filter
class Filter:
    match_mask = (0,0,0,0)
    match_value = (0,0,0,0)
    must_change = (0,0,0,0)
    def __init__(self, mm=None, mv=None, mc=None):
        if mm is not None: self.match_mask = mm
        if mv is not None: self.match_value = mv
        if mc is not None: self.must_change = mc
        self.data = (0,0,0,0)
        self.accept_unchanging = 1
        if self.must_change[0]!=0:self.accept_unchanging = 0 
        if self.must_change[1]!=0:self.accept_unchanging = 0 
        if self.must_change[2]!=0:self.accept_unchanging = 0 
        if self.must_change[3]!=0:self.accept_unchanging = 0
        self.match_value = (self.match_mask[0] & self.match_value[0],
                            self.match_mask[1] & self.match_value[1],
                            self.match_mask[2] & self.match_value[2],
                            self.match_mask[3] & self.match_value[3],
                            )
        pass
    def reset(self):
        self.data = (0,0,0,0)
        pass
    def write_filter_cfg(self, o, pfx):
        getattr(o, pfx+"__accept_unchanging").drive(self.accept_unchanging)
        getattr(o, pfx+"__mask__data_0").drive(self.match_mask[0])
        getattr(o, pfx+"__mask__data_1").drive(self.match_mask[1])
        getattr(o, pfx+"__mask__data_2").drive(self.match_mask[2])
        getattr(o, pfx+"__mask__data_3").drive(self.match_mask[3])
        getattr(o, pfx+"__value__data_0").drive((self.match_value[0] & self.match_mask[0]) | self.must_change[0])
        getattr(o, pfx+"__value__data_1").drive((self.match_value[1] & self.match_mask[1]) | self.must_change[1])
        getattr(o, pfx+"__value__data_2").drive((self.match_value[2] & self.match_mask[2]) | self.must_change[2])
        getattr(o, pfx+"__value__data_3").drive((self.match_value[3] & self.match_mask[3]) | self.must_change[3])
        pass
    def apply(self, data):
        mismatches = False
        for i in range(4):
            if data[i] & self.match_mask[i] != self.match_value[i]: mismatches = True
            pass
        if mismatches:
            return False
        if self.accept_unchanging:
            self.data = data
            return True
        changed = False
        for i in range(4):
            if data[i] & self.must_change[i] != self.data[i] & self.must_change[i]: changed = True
            pass
        if changed:
            self.data = data
            pass
        return changed
    pass

class FilterAcceptAll(Filter):
    match_mask = (0,0,0,0)
    match_value = (0,0,0,0)
    must_change = (0,0,0,0)

class FilterChanging(Filter):
    match_mask = (0,0,0,0)
    match_value = (0,0,0,0)
    must_change = (0xffffffff,0xffffffff,0xffffffff,0xffffffff)
    
#c AnalyzerTraceRamDataPathTest_Base
class AnalyzerTraceRamDataPathTest_Base(ThExecFile):
    th_name = "Analyzer trace filter test"
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
        self.bfm_wait(10)
        pass
    #f run
    def run(self) -> None:
        self.test_filter.reset()
        self.verbose.message(f"Test {self.__class__.__name__}")
        self.verbose.set_level(self.verbose.level_info)
        self.bfm_wait_until_test_done(100)
        self.die_event.fire()
        self.bfm_wait(10)
        pass
    #f run__finalize
    def run__finalize(self) -> None:
        self.passtest("Test completed")
        pass
    pass

#c AnalyzerTraceRamDataPathTest_0
class AnalyzerTraceRamDataPathTest_0(AnalyzerTraceRamDataPathTest_Base):
    test_filter = FilterAcceptAll()
    pass

#a Hardware and test instantiation
#c AnalyzerTraceRamDataPathHardware
class AnalyzerTraceRamDataPathHardware(HardwareThDut):
    clock_desc = [("clk",(0,2,2)),
    ]
    reset_desc = {"name":"reset_n", "init_value":0, "wait":5}
    module_name = "analyzer_trace_ram_data_path"
    dut_inputs  = {"access_combs":t_access_combs,
                   "trace_cfg_fifo":t_analyzer_trace_cfg_fifo,
    }
    dut_outputs = {"fifo_status":t_fifo_status,
    }
    loggers = { }
    pass

#c TestAnalyzerTraceRamDataPath
class TestAnalyzerTraceRamDataPath(TestCase):
    hw = AnalyzerTraceRamDataPathHardware
    _tests = {# "0": (AnalyzerTraceRamDataPathTest_0, 2*1000, {}),
              "smoke": (AnalyzerTraceRamDataPathTest_0, 2*1000, {}),              
    }

