if ! e.cmd-exists "nvm"; then
	_nvm_dir="${NVM_DIR:-$XDG_CONFIG_HOME/nvm}"
	# load nvm (or-ed with true to force non-error return value)
	if test -s "$_nvm_dir/nvm.sh"; then
		source "$_nvm_dir/nvm.sh"
	fi
fi

if test -z "${_JAVASCRIPT_FUNCTIONS_LOADED:-}"; then
	function node-activate-venv() {
		if ! e.cmd-exists "nvm"; then
			statusmsg -w "Automatic environment management is disabled because nvm isn't available from this bash script. nvm-sh (https://github.com/nvm-sh/nvm) must be installed for this to work (even if you use an incompatible shell)."
			return 0
		fi

		nvm install 1>/dev/null 2>&1 || statusmsg -w "nvm install failed. Proceeding anyways."
	}

	function node-lint() (
		node-activate-venv

		local target=$1
		cd "$target" || exit 1
		local logtarget
		logtarget=$(e.pwd)

		statusmsg -i "Linting $logtarget (js/ts)..."
		npx eslint \
			--no-error-on-unmatched-pattern \
			--max-warnings=0 \
			.

		local prettierloglevel="warn"
		if verbose; then
			prettierloglevel="log"
		fi

		npx prettier \
			--check \
			--log-level "$prettierloglevel" \
			--config "${EAVE_HOME}/develop/javascript/es-config/prettier/index.js" \
			--ignore-path "${EAVE_HOME}/develop/javascript/es-config/prettier/prettierignore" \
			--ignore-path ".prettierignore" \
			.

		if test -f "tsconfig.json"; then
			npx tsc --project . --noEmit
		else
			statusmsg -w "No tsconfig.json, skipping TypeScript linting"
		fi

		statusmsg -s "Linting $logtarget passed"
		echo
	)

	function node-format() (
		node-activate-venv

		local target=$1
		cd "$target" || exit 1
		local logtarget
		logtarget=$(e.pwd)

		statusmsg -i "Formatting $logtarget (js/ts)..."

		local prettierloglevel="warn"
		if verbose; then
			prettierloglevel="log"
		fi

		npx prettier \
			--write \
			--log-level "$prettierloglevel" \
			--config "${EAVE_HOME}/develop/javascript/es-config/prettier/index.js" \
			--ignore-path "${EAVE_HOME}/develop/javascript/es-config/prettier/prettierignore" \
			--ignore-path ".prettierignore" \
			.

		statusmsg -s "Formatting $logtarget completed"
		echo
	)

	function node-test() (
		node-activate-venv

		local usage="Usage: bin/test [-p path] [-f file] [-h]"
		local targetpath
		local testfile=""

		targetpath="$(e.parentpath)"

		while getopts "p:f:h" argname; do
			case "$argname" in
			p) targetpath=$OPTARG ;;
			f) testfile=$OPTARG ;;
			h)
				echo "$usage"
				return 0
				;;
			*)
				echo "$usage"
				exit 1
				;;
			esac
		done

		cd "$targetpath" || exit 1

		if verbose; then
			set -x
		fi

		# shellcheck disable=2086
		node "${EAVE_HOME}/node_modules/ava/entrypoints/cli.mjs" \
			--config="${EAVE_HOME}/develop/javascript/es-config/ava/ava.config.mjs" \
			${testfile:-}

		set +x
	)

	_JAVASCRIPT_FUNCTIONS_LOADED=1
fi
