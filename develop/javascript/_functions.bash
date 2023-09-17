if test -z "${_JAVASCRIPT_FUNCTIONS_LOADED:-}"; then
	EAVE_NODE_VERSION=$(cat "${EAVE_HOME}/.node-version")

	function node-validate-version() {
		local current_version
		current_version=$(node --version)
		if ! echo -n "$current_version" | grep -q "v$EAVE_NODE_VERSION"; then
			echo "ERROR: The 'node' executable in your path must be version $EAVE_NODE_VERSION. Your current version: $current_version"
			exit 1
		fi
	}

	function node-activate-venv() {
		# nvm is a pesky collection of functions that needs to be imported every time we
		# want to use it in a new shell process. Assuming the caller has nvm at all,
		# it should be setup by their shell loginfile
		import-loginfile

		if ! ^cmd-exists "nvm"; then
			statusmsg -w "automatic environment management is disabled because nvm was not found in your PATH. It is recommended to install nvm."
			return 0
		fi

		local usershell
		usershell=$(shellname)
		case $usershell in
		"fish")
			# This is necessary because `nvm` in Fish might be a function, which can't be used from Bash.
			fish -c "nvm install $EAVE_NODE_VERSION 1>/dev/null 2>&1"
			;;
		*)
			nvm install "$EAVE_NODE_VERSION" 1>/dev/null 2>&1
			;;
		esac
	}

	function node-lint() (
		node-validate-version
		node-activate-venv

		local target=$1
		cd "$target" || exit 1
		local logtarget
		logtarget=$(^eavepwd)

		statusmsg -in "Linting $logtarget (js/ts)"
		npx eslint --max-warnings=0 .

		local prettierloglevel="silent"
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
		statusmsg -sp " ✔ "
	)

	function node-format() (
		node-validate-version
		node-activate-venv

		local target=$1
		cd "$target" || exit 1
		local logtarget
		logtarget=$(^eavepwd)

		local prettierloglevel="silent"
		if verbose; then
			prettierloglevel="log"
		fi

		statusmsg -in "Formatting $logtarget (js/ts)"
		npx prettier \
			--write \
			--log-level "$prettierloglevel" \
			--config "${EAVE_HOME}/develop/javascript/es-config/prettier/index.js" \
			--ignore-path "${EAVE_HOME}/develop/javascript/es-config/prettier/prettierignore" \
			--ignore-path ".prettierignore" \
			.

		statusmsg -sp " ✔ "
	)

	function node-test() (
		node-validate-version
		node-activate-venv

		local usage="Usage: bin/test [-p path] [-f file] [-h]"
		local targetpath
		local testfile

		targetpath="$(^parentpath)"

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

		# shellcheck disable=SC2086
		node "${EAVE_HOME}/node_modules/ava/entrypoints/cli.mjs" \
			--config="${EAVE_HOME}/develop/javascript/es-config/typescript/ava.config.mjs" ${testfile:-}
	)

	_JAVASCRIPT_FUNCTIONS_LOADED=1
fi
