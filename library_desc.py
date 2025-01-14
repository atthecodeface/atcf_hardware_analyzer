import cdl_desc
from cdl_desc import CdlModule, CdlSimVerilatedModule, CModel, CSrc

class Library(cdl_desc.Library):
    name="analyzer"
    pass

class AnalyzerModules(cdl_desc.Modules):
    name = "analyzer"
    src_dir      = "cdl"
    tb_src_dir   = "tb_cdl"
    libraries = {"std":True}
    cdl_include_dirs = ["cdl"]
    export_dirs = cdl_include_dirs + [ src_dir ]
    modules = []
    modules += [ CdlModule("analyzer_mux_2") ]
    modules += [ CdlModule("analyzer_mux_8_e", cdl_filename="analyzer_mux_8", constants={"analyzer_config_num_targets":2}) ]
    modules += [ CdlModule("analyzer_mux_8") ]
    modules += [ CdlModule("analyzer_trace_filter") ]
    modules += [ CdlModule("analyzer_trigger_simple_byte") ]
    modules += [ CdlModule("analyzer_trigger_minimal") ]
    modules += [ CdlModule("analyzer_trigger_timer") ]
    modules += [ CdlModule("analyzer_trigger_simple") ]
    modules += [ CdlModule("analyzer_trigger_control") ]
    modules += [ CdlModule("analyzer_target") ]
    modules += [ CdlModule("analyzer_target_stub") ]
    modules += [ CdlModule("analyzer_trace_data_value_bound") ]
    modules += [ CdlModule("analyzer_trace_data_offset_bound") ]
    modules += [ CdlModule("analyzer_trace_ram") ]
    modules += [ CdlModule("analyzer_trace_ram_data_path") ]
    pass

class ApbTargetModules(cdl_desc.Modules):
    name = "apb_target"
    src_dir      = "cdl"
    tb_src_dir   = "tb_cdl"
    libraries = {"std":True, "apb":True}
    cdl_include_dirs = ["cdl"]
    export_dirs = cdl_include_dirs + [ src_dir ]
    modules = []
    modules += [ CdlModule("apb_target_analyzer") ]
    # modules += [ CdlModule("apb_target_simple_analyzer") ]
    modules += [ CdlModule("apb_target_analyzer_ctl") ]
    modules += [ CdlModule("tb_analyzer_ctl",
                            src_dir=tb_src_dir) ]
    pass

