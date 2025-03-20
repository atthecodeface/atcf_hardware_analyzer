#a Documentation
"""
Tests for 'analyzer_trace_ram_data_path'

* Write(A), clear(A), read(A) zeros the RAM address A and reads it back

* Push(1..100) followed by 100 Pop() pops 1..100, if push enabled

* Clear, Push(1..100) followed by 100 Pop() pops 0 100 times if push not enabled

* Push16(1..100) followed by 100 Pop16() pops 1..100, if push enabled

* Push8(1..100) followed by 100 Pop8() pops 1..100, if push enabled

* Clear, AtomicInc(1..100) followed by 100 Read() returns 100 1s

* Clear, 50 Sum32(x/2,x) + Sum32(x/2,x+1), reads, returns 4x+1

* Clear, 50 Add16Inc16(x/2,x) + Add16Inc16(x/2,x+1), reads, returns 4x+1 / 2

* Clear, 50 Max32(x,k(x)), Min32(x,k(x)), reads works correctly

* Clear, 50 MinMax16(x,k(x)), reads works correctly

* No journal, pop(empty), push(full), pop(full): pop, push * 2100, read, pop*2, push*5, read*5

* Journal, pop(empty), push(full), pop(full): pop, push * 2053, read, pop*2, push*5, read*11

* Atomic data forwarding - paths with delay 0, 1, 2, 3

"""

#a Imports
from queue import Queue
from regress.utils import t_fifo_status
from regress.analyzer import t_analyzer_data4, t_analyzer_filter_cfg
from regress.analyzer import t_analyzer_trace_cfg_fifo
from regress.analyzer import t_analyzer_trace_access_req, t_analyzer_trace_access_resp, t_atr_address_op, t_atr_alu_op
from regress.analyzer import AtrAccessOp

from cdl.sim     import ThExecFile, LogEventParser
from cdl.sim     import HardwareThDut
from cdl.sim     import TestCase
from typing import Optional

#a AnalyzerTraceRamDataPathTests
#c AnalyzerTraceRamDataPathTest_Base
class AnalyzerTraceRamDataPathTest_Base(ThExecFile):
    th_name = "Analyzer trace data ram path test"
    access_ops = [AtrAccessOp.clear(i) for i in range(1)]
    expected_data = []
    access_ops = []
    data_width = 0 # 32-bit
    journal = 0
    fifo_per_ram = 1
    ram_of_fifo = 0
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
        self.expected_data = self.expected_data[:]
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
        self.trace_cfg_fifo__ram_of_fifo.drive(self.ram_of_fifo)
        self.trace_cfg_fifo__fifo_per_ram.drive(self.fifo_per_ram)
        self.trace_cfg_fifo__enable_push.drive(self.enable_push)
        idle = AtrAccessOp()
        idle.drive_access_req(self, "access_req")
        self.tick()

        for a in self.access_ops:
            a.drive_access_req(self, "access_req")
            self.tick()
            pass
        
        idle.drive_access_req(self, "access_req")
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
    access_ops  = [AtrAccessOp.write(i, i) for i in range(100)]
    access_ops += [AtrAccessOp.clear(i, id=1) for i in range(100)]
    access_ops += [AtrAccessOp.read(i) for i in range(100)]
    pass

#c AnalyzerTraceRamDataPathTest_1
class AnalyzerTraceRamDataPathTest_1(AnalyzerTraceRamDataPathTest_Base):
    """
    Check that push works
    """
    expected_data = [i for i in range(100)]
    access_ops = [AtrAccessOp.push(i) for i in range(100)]
    access_ops += [AtrAccessOp.pop() for i in range(100)]
    pass

#c AnalyzerTraceRamDataPathTest_2
class AnalyzerTraceRamDataPathTest_2(AnalyzerTraceRamDataPathTest_Base):
    """
    Check that if enable_push is deasserted, push does not push
    """
    expected_data = [0 for i in range(100)]
    access_ops = [AtrAccessOp.clear(0, id=0)]
    access_ops += [AtrAccessOp.push(i) for i in range(100)]
    access_ops += [AtrAccessOp.pop() for i in range(100)]
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
    access_ops += [AtrAccessOp.push(i, width=16) for i in range(100)]
    access_ops += [AtrAccessOp.pop() for i in range(100)]
    pass

#c AnalyzerTraceRamDataPathTest_4
class AnalyzerTraceRamDataPathTest_4(AnalyzerTraceRamDataPathTest_Base):
    """
    Check that push8 works
    """
    data_width = 1
    expected_data = []
    for i in range(0,100,4):
        expected_data.append(i * 0x01010101 + 0x03020100)
        expected_data.append(i * 0x01010101 + 0x01010101)
        expected_data.append(i * 0x01010101 + 0x03020302)
        expected_data.append(i * 0x01010101 + 0x03030303)
        pass
    access_ops = []
    access_ops += [AtrAccessOp.push(i, width=8) for i in range(100)]
    access_ops += [AtrAccessOp.pop() for i in range(100)]
    pass

#c AnalyzerTraceRamDataPathTest_5
class AnalyzerTraceRamDataPathTest_5(AnalyzerTraceRamDataPathTest_Base):
    """
    Check that inc32 works
    """
    expected_data = []
    for i in range(100):
        expected_data.append(1)
        pass
    access_ops = []
    access_ops += [AtrAccessOp.clear(i, id=0) for i in range(100)]
    access_ops += [AtrAccessOp.atomic(i, i, t_atr_alu_op.inc32) for i in range(100)]
    access_ops += [AtrAccessOp.read(i) for i in range(100)]
    pass

#c AnalyzerTraceRamDataPathTest_6
class AnalyzerTraceRamDataPathTest_6(AnalyzerTraceRamDataPathTest_Base):
    """
    Check that sum32 works
    """
    expected_data = []
    for i in range(50):
        expected_data.append(i*4+1)
        pass
    access_ops = []
    access_ops += [AtrAccessOp.clear(i, id=0) for i in range(100)]
    access_ops += [AtrAccessOp.atomic(i//2, i, t_atr_alu_op.sum32) for i in range(100)]
    access_ops += [AtrAccessOp.read(i) for i in range(50)]
    pass

#c AnalyzerTraceRamDataPathTest_7
class AnalyzerTraceRamDataPathTest_7(AnalyzerTraceRamDataPathTest_Base):
    """
    Check that inc16_add16 works
    """
    expected_data = []
    for i in range(50):
        expected_data.append((i*4+1) + 0x20000)
        pass
    access_ops = []
    access_ops += [AtrAccessOp.clear(i, id=0) for i in range(100)]
    access_ops += [AtrAccessOp.atomic(i//2, i, t_atr_alu_op.inc16_add16) for i in range(100)]
    access_ops += [AtrAccessOp.read(i) for i in range(50)]
    pass

#c AnalyzerTraceRamDataPathTest_8
datav = lambda x: (x*0x12343) & 0xfffff
class AnalyzerTraceRamDataPathTest_8(AnalyzerTraceRamDataPathTest_Base):
    """
    Check that min32 and max32 work
    """
    expected_data = []
    for i in range(50):
        expected_data.append(min(min(max(datav(i), datav(i+50)), datav(i+100)), datav(i+150)))
        pass
    access_ops = []
    access_ops += [AtrAccessOp.clear(i, id=0) for i in range(100)]
    access_ops += [AtrAccessOp.atomic(i%50, datav(i), t_atr_alu_op.max32) for i in range(100)]
    access_ops += [AtrAccessOp.atomic(i%50, datav(i+100), t_atr_alu_op.min32) for i in range(100)]
    access_ops += [AtrAccessOp.read(i) for i in range(50)]
    pass

#c AnalyzerTraceRamDataPathTest_9
class AnalyzerTraceRamDataPathTest_9(AnalyzerTraceRamDataPathTest_Base):
    """
    Check that min_max16 works
    """
    expected_data = []
    for i in range(50):
        m0 = min(datav(i)&0xffff, datav(i+50)&0xffff)
        m1 = max(datav(i)&0xffff, datav(i+50)&0xffff)
        expected_data.append((m1<<16)|m0)
        pass
    access_ops = []
    access_ops += [AtrAccessOp.write(i, 0x0000ffff) for i in range(50)]
    access_ops += [AtrAccessOp.atomic(i%50, datav(i), t_atr_alu_op.min_max16) for i in range(100)]
    access_ops += [AtrAccessOp.read(i) for i in range(50)]
    pass

#c AnalyzerTraceRamDataPathTest_10
class AnalyzerTraceRamDataPathTest_10(AnalyzerTraceRamDataPathTest_Base):
    """
    Check that pop at empty, push at full, pop when full, etc
    """
    expected_data = []
    expected_data += [i for i in range(10)]
    expected_data += [i for i in range(2)]    
    expected_data += [5000,5001,2,3,4]    
    access_ops = []
    access_ops += [AtrAccessOp.pop(id=0) for i in range(10)]
    access_ops += [AtrAccessOp.push(i) for i in range(2100)]
    access_ops += [AtrAccessOp.read(i) for i in range(10)]
    access_ops += [AtrAccessOp.pop() for i in range(2)]
    access_ops += [AtrAccessOp.push(i+5000) for i in range(5)]
    access_ops += [AtrAccessOp.read(i) for i in range(5)]
    pass

#c AnalyzerTraceRamDataPathTest_11
class AnalyzerTraceRamDataPathTest_11(AnalyzerTraceRamDataPathTest_Base):
    """
    Check that pop at empty, push at full, pop when full, etc with journal
    """
    journal = 1
    expected_data = []
    # Journal 5 entries beyond so that mem[0..4] = 2048+(0..4)
    expected_data += [2048+i for i in range(5)]
    # mem[5..9] = 5..9
    expected_data += [5+i for i in range(5)]
    # Pop 2 - which should be 5, 6 since it has moved on write_ptr/read_ptr to 2
    expected_data += [5+i for i in range(2)]    
    # Journal 5 more to mem[5..] (write_ptr is 10 so that is unaffected)
    expected_data += [2048, 2049, 2050, 2051, 2052, 5000, 5001, 5002, 5003, 5004, 10]
    access_ops = []
    access_ops += [AtrAccessOp.pop(id=0) for i in range(10)]
    access_ops += [AtrAccessOp.push(i) for i in range(2053)]
    access_ops += [AtrAccessOp.read(i) for i in range(10)]
    access_ops += [AtrAccessOp.pop() for i in range(2)]
    access_ops += [AtrAccessOp.push(i+5000) for i in range(5)]
    access_ops += [AtrAccessOp.read(i) for i in range(11)]
    pass

#c AnalyzerTraceRamDataPathTest_12
class AnalyzerTraceRamDataPathTest_12(AnalyzerTraceRamDataPathTest_Base):
    """
    Test forwarding paths
    """
    journal = 1
    expected_data = [0x01010101,
                     0x02020202,
                     0x03030303,
                     0x04040404,
                     0x05050505,
                     0x06060606,
                     0x07070707,
                     0x08080808,
                     0x09090909,
                     0x0,
                     ]
    access_ops = []
    access_ops += [AtrAccessOp.clear(i, id=0) for i in range(10)]
    access_ops += [
        AtrAccessOp.atomic(i, (i+1)<<(8*n), t_atr_alu_op.sum32)
        for (i,n) in [(0,0),
                      (1,0),
                      (1,1),
                      (0,1),
                      (1,2),
                      (1,3),
                      (0,2),
                      (0,3),

                      (2,0),
                      (3,0),
                      (4,0),
                      (2,1),
                      (3,1),
                      (4,1),
                      (2,2),
                      (3,2),
                      (4,2),
                      (2,3),
                      (3,3),
                      (4,3),

                      (5,0),
                      (6,0),
                      (7,0),
                      (8,0),
                      (5,1),
                      (6,1),
                      (7,1),
                      (8,1),
                      (5,2),
                      (6,2),
                      (7,2),
                      (8,2),
                      (5,3),
                      (6,3),
                      (7,3),
                      (8,3),
        ]
        ]
    access_ops += [AtrAccessOp.read(i) for i in range(10)]
    pass

#a Hardware and test instantiation
#c AnalyzerTraceRamDataPathHardware
class AnalyzerTraceRamDataPathHardware(HardwareThDut):
    clock_desc = [("clk",(0,2,2)),
    ]
    reset_desc = {"name":"reset_n", "init_value":0, "wait":5}
    module_name = "analyzer_trace_ram_data_path"
    dut_inputs  = {"access_req":t_analyzer_trace_access_req,
                   "trace_cfg_fifo":t_analyzer_trace_cfg_fifo,
    }
    dut_outputs = {"access_resp":t_analyzer_trace_access_resp,
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
              "3": (AnalyzerTraceRamDataPathTest_3, 2*1000, {}),              
              "4": (AnalyzerTraceRamDataPathTest_4, 2*1000, {}),              
              "5": (AnalyzerTraceRamDataPathTest_5, 2*1000, {}),              
              "6": (AnalyzerTraceRamDataPathTest_6, 2*1000, {}),              
              "7": (AnalyzerTraceRamDataPathTest_7, 2*1000, {}),              
              "8": (AnalyzerTraceRamDataPathTest_8, 2*1000, {}),              
              "9": (AnalyzerTraceRamDataPathTest_9, 2*1000, {}),              
              "10": (AnalyzerTraceRamDataPathTest_10, 10*1000, {}),              
              "11": (AnalyzerTraceRamDataPathTest_11, 10*1000, {}),              
              "12": (AnalyzerTraceRamDataPathTest_12, 2*1000, {}),              
              "smoke": (AnalyzerTraceRamDataPathTest_0, 2*1000, {}),              
    }

