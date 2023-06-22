if test -z "${_JAVASCRIPT_FUNCTIONS_LOADED:-}"; then
	EAVE_NODE_VERSION=$(cat "${EAVE_HOME}/.node-version")

	function node-validate-version() {
		local current_version=$(node --version)
		if ! $(echo -n "$current_version" | grep -q "v$EAVE_NODE_VERSION"); then
			echo "ERROR: The 'node' executable in your path must be version $EAVE_NODE_VERSION. Your current version: $current_version"
			exit 1
		fi
	}

	function node-activate-venv() {
		if ! cmd-exists "nvm"; then
			statusmsg -w "automatic environment management is disabled because nvm was not found in your PATH. It is recommended to install nvm."
			return 0
		fi

		local usershell=$(shellname)
		case $usershell in
		"fish")
			# This is necessary because `nvm` in Fish might be a function, which can't be used from Bash.
			fish -c "nvm install $EAVE_NODE_VERSION 1>/dev/null 2>&1"
			;;
		*)
			nvm install $EAVE_NODE_VERSION 1>/dev/null 2>&1
			;;
		esac
	}

	function node-lint() (
		node-validate-version
		node-activate-venv

		local target=$1
		cd $target
		local logtarget=$(~eavepwd)

		statusmsg -in "Linting $logtarget (js/ts)"
		npx eslint --max-warnings=0 .

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
		cd $target
		local logtarget=$(~eavepwd)

		statusmsg -in "Formatting $logtarget (js/ts)"
		npx eslint . --fix
		statusmsg -sp " ✔ "
	)

	function node-test() (
		node-validate-version
		node-activate-venv

		local target=${1:-tests}
		cd $target

		npx ava \
			--config=${EAVE_HOME}/develop/javascript/es-config/typescript/ava.config.mjs .
	)

	_JAVASCRIPT_FUNCTIONS_LOADED=1
fi
