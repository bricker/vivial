if test -z "${_PYTHON_FUNCTIONS_LOADED:-}"; then
	EAVE_PYTHON_VERSION=$(cat "${EAVE_HOME}/.python-version")

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

	function python-lint () (
		python-validate-version
		python-activate-venv

		local target=$1
		local configfile=${EAVE_HOME}/develop/python/pyproject.toml

		statusmsg -i "Linting ${target}..."

		statusmsg -i "(lint) autoflake..."
		# https://github.com/PyCQA/autoflake/pull/249
		python -m autoflake --check-diff --config ${EAVE_HOME}/develop/python/autoflake.cfg $target

		statusmsg -i "(lint) isort..."
		python -m isort --settings-file=$configfile --check $target

		statusmsg -i "(lint) black..."
		python -m black --config=$configfile --check $target

		statusmsg -i  "(lint) mypy..."
		python -m mypy --config-file=$configfile $target

		statusmsg -s "Linting passed ✔"
	)

	function python-format() (
		python-validate-version
		python-activate-venv

		local target=$1
		local configfile=${EAVE_HOME}/develop/python/pyproject.toml

		statusmsg -i "(format) autoflake..."
		# https://github.com/PyCQA/autoflake/pull/249
		python -m autoflake --in-place --config ${EAVE_HOME}/develop/python/autoflake.cfg $target

		statusmsg -i "(format) isort..."
		python -m isort --settings-file=$configfile $target

		statusmsg -i  "(format) black..."
		python -m black --config=$configfile $target

		statusmsg -s "Formatting completed ✔"
	)

	_PYTHON_FUNCTIONS_LOADED=1
fi
