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
    modules += [ CdlModule("analyzer_target") ]
    modules += [ CdlModule("analyzer_target_stub") ]
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
    modules += [ CdlModule("apb_target_analyzer_ctl") ]
    modules += [ CdlModule("tb_analyzer_ctl",
                            src_dir=tb_src_dir) ]
    pass

