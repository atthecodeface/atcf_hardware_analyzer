Q=@
CDL_REGRESS = ${CDL_ROOT}/libexec/cdl/cdl_regress.py

.PHONY:regression regression_batch regression_python
.PHONY:smoke smoke_batch smoke_python

WAVES =

SMOKE_OPTIONS = --only-tests 'smoke'
SMOKE_TESTS   = test_analyzer test_analyzer_filter
REGRESS_TESTS = test_analyzer test_analyzer_filter
CDL_REGRESS_PACKAGE_DIRS = --package-dir regress:${SRC_ROOT}/python --package-dir regress:${GRIP_ROOT_PATH}/atcf_hardware_utils/python --package-dir regress:${GRIP_ROOT_PATH}/atcf_hardware_apb/python

#smoke_mifs
smoke:
	${CDL_REGRESS} --pyengine-dir=${BUILD_ROOT}  ${CDL_REGRESS_PACKAGE_DIRS} --suite-dir=python ${SMOKE_OPTIONS} ${SMOKE_TESTS} ${WAVES}

.PHONY:regress
regress:
	${CDL_REGRESS} --pyengine-dir=${BUILD_ROOT} ${CDL_REGRESS_PACKAGE_DIRS} --suite-dir=python ${REGRESS_TESTS}
