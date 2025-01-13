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
from regress.analyzer import t_analyzer_data4, t_analyzer_filter_cfg, t_access_combs, t_analyzer_trace_cfg_fifo, t_address_op, t_alu_op, t_access_resp

from cdl.sim     import ThExecFile, LogEventParser
from cdl.sim     import HardwareThDut
from cdl.sim     import TestCase
from typing import Optional

class AccessOp:
    read_enable = 0
    write_enable = 0
    id = 0
    address_op = t_address_op.access
    address = 0
    alu_op = t_alu_op.clear
    data = 0
    byte_of_sram = 0
    def __init__(self, id=None, address_or_op=None, data=None, alu_op=None, write_enable=0, read_enable=0):
        if id is not None:
            self.id = id
            pass
        if type(address_or_op) == t_address_op:
            self.address_op = address_or_op
            pass
        elif address_or_op != None:
            self.address_op = t_address_op.access
            self.address = address_or_op
            pass
        if data is not None:
            self.data = data
            pass
        if alu_op is not None:
            self.alu_op = alu_op
            pass
        self.write_enable = write_enable
        self.read_enable = read_enable
        pass
    def drive_access_combs(self, obj, pfx):
        getattr(obj, pfx+"__read_enable").drive(self.read_enable)
        getattr(obj, pfx+"__write_enable").drive(self.write_enable)
        getattr(obj, pfx+"__id").drive(self.id)
        getattr(obj, pfx+"__address_op").drive(self.address_op.value)
        getattr(obj, pfx+"__address").drive(self.address)
        getattr(obj, pfx+"__alu_op").drive(self.alu_op.value)
        getattr(obj, pfx+"__op_data").drive(self.data)
        getattr(obj, pfx+"__byte_of_sram").drive(self.byte_of_sram)
        pass
    @classmethod
    def write(cls, address, data, width=32):
        alu_op = {8:t_alu_op.write8, 16:t_alu_op.write16, 32:t_alu_op.write32}[width]
        return cls(address_or_op=address, data=data, alu_op=alu_op, write_enable=1, read_enable=0)
    @classmethod
    def read(cls, address, id=1):
        return cls(id, address_or_op=address, alu_op=t_alu_op.clear, write_enable=0, read_enable=1)
    @classmethod
    def push(cls, data, width=32):
        alu_op = {8:t_alu_op.write8, 16:t_alu_op.write16, 32:t_alu_op.write32}[width]
        read_enable = 0
        if width!=32: read_enable = 1
        return cls(address_or_op=t_address_op.push, data=data, alu_op=alu_op, write_enable=1, read_enable=read_enable)
    @classmethod
    def pop(cls, id=1):
        return cls(id, address_or_op=t_address_op.pop, alu_op=t_alu_op.clear, write_enable=0, read_enable=1)
    @classmethod
    def clear(cls, address, id=1):
        read_enable = 0
        if id != 0: read_enable = 1
        return cls(id, address_or_op=address, alu_op=t_alu_op.clear, write_enable=1, read_enable=read_enable)
    pass

#c AnalyzerTraceRamDataPathTest_Base
class AnalyzerTraceRamDataPathTest_Base(ThExecFile):
    th_name = "Analyzer trace data ram path test"
    access_ops = [AccessOp.clear(i) for i in range(1)]
    expected_data = []
    access_ops = []
    data_width = 0 # 32-bit
    journal = 0
    enable_push = 1
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
        self.data_count = 0
        self.bfm_wait(10)
        pass
    #f tick
    def tick(self):
        if self.access_resp__valid.value() and self.access_resp__id.value() == 1:
            d = self.access_resp__data.value()
            self.data_count += 1
            if len(self.expected_data) == 0:
                self.failtest(f"access_resp had {self.data_count} valid data out {d} but did not expect that")
                return
            e = self.expected_data.pop(0)
            self.compare_expected(f"access_resp {self.data_count} data out", d, e)
            pass                
        self.bfm_wait(1)
        pass
    #f run
    def run(self) -> None:
        self.verbose.message(f"Test {self.__class__.__name__}")
        self.verbose.set_level(self.verbose.level_info)

        self.trace_cfg_fifo__data_width.drive(self.data_width)
        self.trace_cfg_fifo__journal.drive(self.journal)
        self.trace_cfg_fifo__enable_push.drive(self.enable_push)
        idle = AccessOp()
        idle.drive_access_combs(self, "access_req")
        self.tick()

        for a in self.access_ops:
            a.drive_access_combs(self, "access_req")
            self.tick()
            pass
        
        idle.drive_access_combs(self, "access_req")
        for i in range(10):
            self.tick()
            pass

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
    """
    Check that clear works if write works
    """
    expected_data = [i for i in range(100)]
    expected_data += [0] * 100
    access_ops  = [AccessOp.write(i, i) for i in range(100)]
    access_ops += [AccessOp.clear(i, id=1) for i in range(100)]
    access_ops += [AccessOp.read(i) for i in range(100)]
    pass

#c AnalyzerTraceRamDataPathTest_1
class AnalyzerTraceRamDataPathTest_1(AnalyzerTraceRamDataPathTest_Base):
    """
    Check that push works
    """
    expected_data = [i for i in range(100)]
    access_ops = [AccessOp.push(i) for i in range(100)]
    access_ops += [AccessOp.pop() for i in range(100)]
    pass

#c AnalyzerTraceRamDataPathTest_2
class AnalyzerTraceRamDataPathTest_2(AnalyzerTraceRamDataPathTest_Base):
    """
    Check that if enable_push is deasserted, push does not push
    """
    expected_data = [0 for i in range(100)]
    access_ops = [AccessOp.clear(0, id=0)]
    access_ops += [AccessOp.push(i) for i in range(100)]
    access_ops += [AccessOp.pop() for i in range(100)]
    enable_push = 0
    pass

#c AnalyzerTraceRamDataPathTest_3
class AnalyzerTraceRamDataPathTest_3(AnalyzerTraceRamDataPathTest_Base):
    """
    Check that push16 works
    """
    data_width = 2
    expected_data = []
    for i in range(0,100,2):
        expected_data.append(i | ((i+1)<<16))
        expected_data.append((i+1) | ((i+1)<<16))
        pass
    access_ops = []
    access_ops += [AccessOp.push(i, width=16) for i in range(100)]
    access_ops += [AccessOp.pop() for i in range(100)]
    pass

#a Hardware and test instantiation
#c AnalyzerTraceRamDataPathHardware
class AnalyzerTraceRamDataPathHardware(HardwareThDut):
    clock_desc = [("clk",(0,2,2)),
    ]
    reset_desc = {"name":"reset_n", "init_value":0, "wait":5}
    module_name = "analyzer_trace_ram_data_path"
    dut_inputs  = {"access_req":t_access_combs,
                   "trace_cfg_fifo":t_analyzer_trace_cfg_fifo,
    }
    dut_outputs = {"access_resp":t_access_resp,
                   "fifo_status":t_fifo_status,
    }
    loggers = { }
    pass

#c TestAnalyzerTraceRamDataPath
class TestAnalyzerTraceRamDataPath(TestCase):
    hw = AnalyzerTraceRamDataPathHardware
    _tests = {"0": (AnalyzerTraceRamDataPathTest_0, 2*1000, {}),
              "1": (AnalyzerTraceRamDataPathTest_1, 2*1000, {}),              
              "2": (AnalyzerTraceRamDataPathTest_2, 2*1000, {}),              
              "smoke": (AnalyzerTraceRamDataPathTest_3, 2*1000, {}),              
    }

