Q=@
CDL_REGRESS = ${CDL_ROOT}/libexec/cdl/cdl_regress.py

.PHONY:regression regression_batch regression_python
.PHONY:smoke smoke_batch smoke_python

# $ WAVES=--waves=dut SMOKE_OPTIONS=--only-tests='0' SMOKE_TESTS=test_apb_analyzer grip make repo.atcf_hardware_analyzer.smoke_test
WAVES ?=

SMOKE_OPTIONS ?= --only-tests 'smoke'
SMOKE_TESTS   ?= test_apb_analyzer_trigger test_apb_analyzer_trace test_apb_analyzer_src test_analyzer_ctl test_analyzer_filter test_analyzer_trace_ram_data_path test_dbg_analyzer test_apb_analyzer
REGRESS_TESTS ?= test_apb_analyzer_trigger test_apb_analyzer_trace test_apb_analyzer_src test_analyzer_ctl test_analyzer_filter test_analyzer_trace_ram_data_path test_dbg_analyzer test_apb_analyzer
CDL_REGRESS_PACKAGE_DIRS = --package-dir regress:${SRC_ROOT}/python --package-dir regress:${GRIP_ROOT_PATH}/atcf_hardware_utils/python --package-dir regress:${GRIP_ROOT_PATH}/atcf_hardware_apb/python

#smoke_mifs
smoke:
	${CDL_REGRESS} --pyengine-dir=${BUILD_ROOT}  ${CDL_REGRESS_PACKAGE_DIRS} --suite-dir=python ${SMOKE_OPTIONS} ${SMOKE_TESTS} ${WAVES}

.PHONY:regress
regress:
	${CDL_REGRESS} --pyengine-dir=${BUILD_ROOT} ${CDL_REGRESS_PACKAGE_DIRS} --suite-dir=python ${REGRESS_TESTS}
