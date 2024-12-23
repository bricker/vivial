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
		if ! e.ci; then
			local ved="${EAVE_HOME}/.venv"
			if ! test -d "$ved"; then
				statusmsg -e "Python virtualenv not installed in $EAVE_HOME. Run $EAVE_HOME/bin/setup to create it."
				exit 1
			fi

			# Reminder that this function is expected to be run from bin/* scripts, which are usually bash scripts,
			# so the file being sourced here is for bash, not the user's shell.
			# shellcheck disable=SC1091
			source "$ved/bin/activate"
		fi
	}

	function python-lint() (
		python-validate-version
		python-activate-venv

		local target=$1

		cd "$target" || exit 1
		local logtarget
		logtarget=$(e.pwd)

		local verboseflag=""
		local pipquietflag="-qq"
		if verbose; then
			verboseflag="--verbose"
			pipquietflag=""
		fi

		if test -z "${SKIP_PYRIGHT_UPDATE:-}"; then
			# pyright is updated frequently, like multiple times per week,
			# so we add this here so that we automatically use the latest version.
			pip install $verboseflag $pipquietflag -U pyright
		fi

		statusmsg -i "Linting $logtarget (py)..."

		local ruffconfig="${EAVE_HOME}/develop/python/configs/ruff.toml"
		python -m ruff check $verboseflag --config="$ruffconfig" .
		python -m ruff format --check $verboseflag --config="$ruffconfig" .
		python -m pyright --project "$EAVE_HOME" --warnings .

		statusmsg -s "Linting $logtarget passed"
		echo
	)

	function python-format() (
		python-validate-version
		python-activate-venv

		local target=$1

		cd "$target" || exit 1
		local logtarget
		logtarget=$(e.pwd)

		local verboseflag=""
		if verbose; then
			verboseflag="--verbose"
		fi

		statusmsg -i "Formatting $logtarget (py)..."

		local ruffconfig="${EAVE_HOME}/develop/python/configs/ruff.toml"
		python -m ruff format $verboseflag --config="$ruffconfig" .
		python -m ruff check --fix-only $verboseflag --config="$ruffconfig" --show-fixes .

		statusmsg -s "Formatting $logtarget completed"
		echo
	)

	function python-test() (
		python-validate-version
		python-activate-venv

		local target=$1
		local testfile=${2:-.}
		local exitfirst=""
		if e.ci; then
			exitfirst="--exitfirst"
		fi

		cd "$target" || exit 1
		# "${EAVE_HOME}"/bin/run-with-dotenv -- python -m coverage run --rcfile=$configfile -m pytest -c=$configfile $target
		# python -m coverage lcov --rcfile=$configfile
		python -m pytest \
			--cov \
			--cov-report=html \
			--cov-context=test \
			--cov-config="${EAVE_HOME}/develop/python/configs/coverage.toml" \
			--config-file="${EAVE_HOME}/develop/python/configs/pytest.pyproject.toml" \
			--rootdir="${EAVE_HOME}" $exitfirst "$testfile"
	)

	_PYTHON_FUNCTIONS_LOADED=1
fi
