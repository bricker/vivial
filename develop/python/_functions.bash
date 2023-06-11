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

		local qflag="--quiet"
		local mypyout=/dev/null
		if verbose; then
			qflag=""
			mypyout=/dev/stdout
		fi

		local target=$1
		local configfile=${EAVE_HOME}/develop/python/configs/pyproject.toml
		local thisdir=$(basename $PWD)

		statusmsg -in "Linting $thisdir/$target (py)"
		python -m ruff $qflag --config=$configfile $target
		python -m black $qflag --config=$configfile --check $target
		python -m mypy --config-file=$configfile $target > $mypyout
		statusmsg -sp " ✔ "
	)

	function python-format() (
		python-validate-version
		python-activate-venv

		local qflag="--quiet"
		if verbose; then
			qflag=""
		fi

		local target=$1
		local configfile=${EAVE_HOME}/develop/python/configs/pyproject.toml
		local thisdir=$(basename $PWD)

		statusmsg -in "Formatting $thisdir/$target (py)"
		python -m ruff $qflag --fix --config=$configfile $target
		python -m black $qflag --config=$configfile $target
		statusmsg -sp " ✔ "
	)

	function python-test() (
		python-validate-version
		python-activate-venv

		local target=$1
		local configfile=${EAVE_HOME}/develop/python/configs/pyproject.toml
		run-with-dotenv python -m coverage run --rcfile=$configfile -m pytest -c=$configfile $target
		python -m coverage lcov --rcfile=$configfile
	)

	_PYTHON_FUNCTIONS_LOADED=1
fi
