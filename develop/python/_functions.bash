if test -z "${_PYTHON_FUNCTIONS_LOADED:-}"; then
	EAVE_PYTHON_VERSION=$(cat "${EAVE_HOME}/.python-version")

	function python-validate-version() {
		local current_version
		current_version=$(python --version)
		if ! echo -n "$current_version" | grep -q "Python $EAVE_PYTHON_VERSION"; then
			echo "ERROR: The 'python' executable in your path must be version $EAVE_PYTHON_VERSION. Your current version: $current_version"
			exit 1
		fi
	}

	function python-activate-venv() {
		if ! ^ci; then
			ved="${EAVE_HOME}/.venv"
			if ! test -d "$ved"; then
				statusmsg -e "Python virtualenv not installed in $EAVE_HOME. Run $EAVE_HOME/bin/setup to create it."
				exit 1
			fi

			# Reminder that this function is expected to be run from a bin/* scripts, which are usually bash scripts,
			# so the file being sourced here is for bash, not the user's shell.
			# shellcheck disable=SC1091
			source "$ved/bin/activate"
		fi
	}

	function python-lint() (
		python-validate-version
		python-activate-venv

		local target=$1
		local configfile=${EAVE_HOME}/develop/python/configs/pyproject.toml

		cd "$target" || exit 1
		local logtarget
		logtarget=$(^eavepwd)

		statusmsg -i "Linting $logtarget (py)..."

		python -m ruff --config="$configfile" .
		python -m pyright --project "$EAVE_HOME" .
		python -m black --config="$configfile" --check .

		statusmsg -s "Linting $logtarget passed"
		echo
	)

	function python-format() (
		python-validate-version
		python-activate-venv

		local target=$1
		local configfile=${EAVE_HOME}/develop/python/configs/pyproject.toml

		cd "$target" || exit 1
		local logtarget
		logtarget=$(^eavepwd)

		statusmsg -i "Formatting $logtarget (py)..."

		python -m black --config="$configfile" .

		# Ruff could change code semantics. The auto-formatter is intended to be completely safe.
		# but it also removes unused import which we want.
		# TODO: can we configure it to only fix the unused imports?
		python -m ruff --fix --config="$configfile" .

		statusmsg -s "Formatting $logtarget completed"
		echo
	)

	function python-test() (
		python-validate-version
		python-activate-venv

		local target=$1
		local testfile=${2:-.}
		local configfile=${EAVE_HOME}/develop/python/configs/pyproject.toml
		local exitfirst=""
		if ^ci; then
			exitfirst="--exitfirst"
		fi

		cd "$target" || exit 1
		# run-with-dotenv python -m coverage run --rcfile=$configfile -m pytest -c=$configfile $target
		# python -m coverage lcov --rcfile=$configfile
		run-with-dotenv python -m pytest -c="$configfile" --rootdir=. $exitfirst "$testfile"
	)

	_PYTHON_FUNCTIONS_LOADED=1
fi
