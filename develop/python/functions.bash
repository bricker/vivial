if test -z "${_PYTHONSCRIPTS_LOADED:-}"
then
	EAVE_PYTHON_VERSION=3.11

	source ${EAVE_HOME}/develop/shared/functions.bash

	function python-validate-version () {
		local current_version=$(python --version)
		if ! $(echo -n "$current_version" | grep -q "Python $EAVE_PYTHON_VERSION")
		then
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

	_PYTHONSCRIPTS_LOADED=1
fi