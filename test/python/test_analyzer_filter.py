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
from regress.analyzer import t_analyzer_data4, t_analyzer_filter_cfg

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
    
#c AnalyzerFilterTest_Base
class AnalyzerFilterTest_Base(ThExecFile):
    th_name = "Analyzer trace filter test"
    data_to_feed = [
        ]
    data_to_feed += [
        (1,2,3,4),
        (1,2,3,4),
        (1,2,3,4),
        (1,2,3,4),
        ]
    data_to_feed += [
        (i, i+1, i+2, i+3)
        for i in range(100)
        ]
    data_to_feed += [
        (1,2,3,4),
        (1,2,3,4),
        (1,2,3,4),
        (1,2,3,4),
        ]
    data_to_feed += [
        None,
        None,
        None,
        None,
        None,
        ]
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

        self.din__valid.drive(0)
        self.all_data_out = []

        self.bfm_wait(4)
        self.die_event.reset()

        self.verbose.info("Setting filter cfg")
        self.filter_cfg__enable.drive(0)
        self.test_filter.write_filter_cfg(self, "filter_cfg")

        self.bfm_wait(4)
        self.filter_cfg__enable.drive(1)
        self.bfm_wait(4)

        self.verbose.info("Feeding in data")
        self.expected_data = []
        accepted = 0
        rejected = 0
        received = 0
        for d in self.data_to_feed:
            if d is None:
                self.din__valid.drive(0)
                pass
            else:
                self.din__valid.drive(1)
                self.din__data_0.drive(d[0])
                self.din__data_1.drive(d[1])
                self.din__data_2.drive(d[2])
                self.din__data_3.drive(d[3])
                if self.test_filter.apply(d):
                    self.expected_data.append(d)
                    accepted += 1
                    pass
                else:
                    rejected += 1
                pass
            self.bfm_wait(1)
            if self.dout__valid.value():
                dout = (self.dout__data_0.value(),
                        self.dout__data_1.value(),
                        self.dout__data_2.value(),
                        self.dout__data_3.value()
                        )
                if len(self.expected_data) == 0:
                    self.failtest(f"Filter produced data out {dout} but did not expect that")
                    return
                e = self.expected_data.pop(0)
                self.compare_expected("Filter out data 0", dout[0], e[0])
                self.compare_expected("Filter out data 1", dout[1], e[1])
                self.compare_expected("Filter out data 2", dout[2], e[2])
                self.compare_expected("Filter out data 3", dout[3], e[3])
                received += 1
                pass
            pass

        self.verbose.message(f"Expected to have rejected {rejected}, and {accepted} accepted, and it delivered {received}")
        self.compare_expected("Accepted", accepted, received)
        self.bfm_wait_until_test_done(100)
        self.die_event.fire()
        self.bfm_wait(10)
        pass
    #f run__finalize
    def run__finalize(self) -> None:
        self.passtest("Test completed")
        pass
    pass

#c AnalyzerFilterTest_0
class AnalyzerFilterTest_0(AnalyzerFilterTest_Base):
    test_filter = FilterAcceptAll()
    pass

#c AnalyzerFilterTest_1
class AnalyzerFilterTest_1(AnalyzerFilterTest_Base):
    test_filter = FilterChanging()
    pass

#c AnalyzerFilterTest_2
class AnalyzerFilterTest_2(AnalyzerFilterTest_Base):
    test_filter = Filter((3,0,0,0), (1,0,0,0), None)
    pass

#c AnalyzerFilterTest_3
class AnalyzerFilterTest_3(AnalyzerFilterTest_Base):
    test_filter = Filter((3,0,0,0), (1,0,0,0), (0,6,0,0))
    pass

#a Hardware and test instantiation
#c AnalyzerFilterHardware
class AnalyzerFilterHardware(HardwareThDut):
    clock_desc = [("clk",(0,2,2)),
    ]
    reset_desc = {"name":"reset_n", "init_value":0, "wait":5}
    module_name = "analyzer_trace_filter"
    dut_inputs  = {"din":t_analyzer_data4,
                   "filter_cfg":t_analyzer_filter_cfg,
    }
    dut_outputs = {"dout":t_analyzer_data4,
    }
    loggers = { }
    pass

#c TestAnalyzerFilter
class TestAnalyzerFilter(TestCase):
    hw = AnalyzerFilterHardware
    _tests = {"0": (AnalyzerFilterTest_0, 2*1000, {}),
              "1": (AnalyzerFilterTest_1, 2*1000, {}),              
              "2": (AnalyzerFilterTest_2, 2*1000, {}),              
              "3": (AnalyzerFilterTest_3, 2*1000, {}),              
              "smoke": (AnalyzerFilterTest_3, 2*1000, {}),              
    }

