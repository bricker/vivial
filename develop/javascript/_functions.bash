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
			fish -c "nvm --silent install $EAVE_NODE_VERSION"
			;;
		*)
			nvm --silent install $EAVE_NODE_VERSION
			;;
		esac
	}

	function node-lint() (
		node-validate-version
		node-activate-venv

		local target=$1
		local thisdir=$(basename $PWD)

		statusmsg -in "Linting $thisdir..."
		npx eslint $target
		statusmsg -sp " ✔ "
	)

	function node-format() (
		node-validate-version
		node-activate-venv

		local target=$1
		local thisdir=$(basename $PWD)

		statusmsg -in "Formatting $thisdir..."
		npx eslint $target --fix
		statusmsg -sp " ✔ "
	)

	_JAVASCRIPT_FUNCTIONS_LOADED=1
fi
