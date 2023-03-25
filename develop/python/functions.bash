EAVE_PYTHON_VERSION=$(cat "${EAVE_HOME}/.python-version")

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
	if ! command_exists pyenv
	then
		statusmsg -w "automatic environment management is disabled because pyenv was not found in your PATH. It is recommended to install pyenv."
		return 0
	fi

	if ! test -d .venv
	then
		python -m venv --upgrade-deps .venv
	fi

	source .venv/bin/activate
}
