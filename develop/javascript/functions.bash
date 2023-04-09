if test -z "${_JSSCRIPTS_LOADED:-}"
then
	EAVE_NODE_VERSION=18

	source ${EAVE_HOME}/develop/shared/functions.bash

	function node-validate-version () {
		local current_version=$(node --version)
		if ! $(echo -n "$current_version" | grep -q "v$EAVE_NODE_VERSION")
		then
			echo "ERROR: The 'node' executable in your path must be version $EAVE_NODE_VERSION. Your current version: $current_version"
			exit 1
		fi
	}

	function node-activate-venv () {
		if ! command_exists "nvm"
		then
			statusmsg -w "automatic environment management is disabled because nvm was not found in your PATH. It is recommended to install nvm."
			return 0
		fi

		local usershell=$(shellname)
		case $usershell in
			"fish")
				# This is necessary because `nvm` in Fish might be a function, which can't be used from Bash.
				fish -c "nvm install $EAVE_NODE_VERSION"
				;;
			*)
				nvm install $EAVE_NODE_VERSION
				;;
		esac
	}

	_JSSCRIPTS_LOADED=1
fi