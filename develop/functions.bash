if test -z "${_UMBRELLA_FUNCTIONS_LOADED:-}"; then
	source ${EAVE_HOME}/develop/shared/_functions.bash
	source ${EAVE_HOME}/develop/javascript/_functions.bash
	source ${EAVE_HOME}/develop/python/_functions.bash
	_UMBRELLA_FUNCTIONS_LOADED=1
fi