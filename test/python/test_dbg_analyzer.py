#a Imports
from regress.apb.structs import t_apb_request, t_apb_response
from regress.apb         import Script
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

#c FifoScript
class FifoScript(DbgMasterMuxScript):
    select = 1
    def __init__(self, *args, **kwargs):
        subscript = DbgMasterFifoScript(*args, **kwargs)
        super().__init__(select=self.select, clear=False, subscript=subscript)
        pass
    pass

#c ApbScript
class ApbScript(DbgMasterMuxScript):
    select = 2
    def __init__(self, subscript):
        super().__init__(select=self.select, clear=False, subscript=subscript)
        pass
    pass

#c DbgAnalyzerTest_Base
class DbgAnalyzerTest_Base(ThExecFile):
    
    th_name = "Dbg script analyzer trigger test harness"
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

        self.dbg_master = DbgMaster(self, "dbg_master_req", "dbg_master_resp")
        self.apb_map = TbApbAddressMap()

        self.bfm_wait(10)

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

        self.verbose.message(f"Clear control")
        self.verbose.message(f"Enable src as analyzer tgt")
        self.verbose.message(f"Set mux to drive id")
        script = [
            Script.op_set("addr1",(self.apb_map.analyzer_ctl.select.Address()>>8)&0xff),
            Script.op_write(self.apb_map.analyzer_ctl.select.Address() & 0xff, 32, [1<<31]),
            Script.op_write(self.apb_map.analyzer_ctl.select_at.Address() & 0xff, 32, [0]),
            Script.op_read(self.apb_map.analyzer_ctl.status.Address() & 0xff, 32),
            Script.op_write(self.apb_map.analyzer_ctl.wrd.Address() & 0xff, 32, [self.tgt_mux_sel]),
            ]

        addr = -1
        for (r,wd) in writes:
            if r.Address() & 0xff00 != addr & 0xff00:
                addr = r.Address()
                script.append(Script.op_set("addr1",(addr>>8)&0xff))
                pass
            addr = r.Address()
            script.append(Script.op_write(addr & 0xff,32,[wd]))
            pass

        script = Script.compile_script(script)
        script = ApbScript(script)
        (completion, res_data) = self.dbg_master.invoke_script_bytes(
            script.as_bytes(),
            self.bfm_wait,
            lambda :0,
            1000)

        self.bfm_wait(40)
        script_num = 1
        for (script) in [
                FifoScript(["status"]
                           )
                ]:
            (completion, res_data) = self.dbg_master.invoke_script_bytes(
                script.as_bytes(),
                self.bfm_wait,
                lambda :0,
                1000)
            #    self.compare_expected(f"Completion of script {script_num}", exp_c, completion)
            is_empty = res_data[0] & 1
            num_available = (res_data[0]>>4) & 0x3fff
            self.compare_expected("Should be not empty", is_empty, 0)
            self.verbose.message(f"Found {num_available} entries in the FIFO")
            self.bfm_wait(4)
            pass

        for (script) in [
                FifoScript([("read",32,25),
                           ])]:
            (completion, res_data) = self.dbg_master.invoke_script_bytes(
                script.as_bytes(),
                self.bfm_wait,
                lambda :0,
                1000)
            self.compare_expected_list("Data read", [3+2*i for i in range(25)], res_data)
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

#c DbgAnalyzerTest_0
class DbgAnalyzerTest_0(DbgAnalyzerTest_Base):
    pass

#a Hardware and test instantiation
#c DbgAnalyzerHardware
class DbgAnalyzerHardware(HardwareThDut):
    clock_desc = [("clk",(0,2,2)),
    ]
    reset_desc = {"name":"reset_n", "init_value":0, "wait":5}
    module_name = "tb_analyzer_dbg"
    dut_inputs  = {"dbg_master_req":t_dbg_master_request,
    }
    dut_outputs = {"dbg_master_resp":t_dbg_master_response,
    }
    loggers = { # "dprintf": {"modules":"dut.dut", "verbose":1}
                }
    pass

#c TestDbgAnalyzer
class TestDbgAnalyzer(TestCase):
    hw = DbgAnalyzerHardware
    _tests = {"0": (DbgAnalyzerTest_0, 2*1000, {}),
              "smoke": (DbgAnalyzerTest_0, 80*1000, {}),
    }

