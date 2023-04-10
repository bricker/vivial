if test -z "${_PYTHON_FUNCTIONS_LOADED:-}"; then
	EAVE_PYTHON_VERSION=$(cat "${EAVE_HOME}/.python-version")

	source ${EAVE_HOME}/develop/shared/functions.bash

	function python-validate-version() {
		local current_version=$(python --version)
		if ! $(echo -n "$current_version" | grep -q "Python $EAVE_PYTHON_VERSION"); then
			echo "ERROR: The 'python' executable in your path must be version $EAVE_PYTHON_VERSION. Your current version: $current_version"
			exit 1
		fi
	}

	function python-activate-venv () {
		ved=${EAVE_HOME}/.venv
		if ! test -d $ved
		then
			statusmsg -e "Python virtualenv not installed in $EAVE_HOME. Run $EAVE_HOME/bin/setup to create it."
			exit 1
		fi

		source $ved/bin/activate
	}

	_PYTHON_FUNCTIONS_LOADED=1
fi
