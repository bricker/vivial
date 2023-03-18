EAVE_NODE_VERSION=18

function node-validate-version () {
	local current_version=$(node --version)
	if ! $(echo -n "$current_version" | grep -q "v$EAVE_NODE_VERSION")
	then
		echo "ERROR: The 'node' executable in your path must be version $EAVE_NODE_VERSION. Your current version: $current_version"
		exit 1
	fi
}

function node-activate-venv () {
	if command -v nvm
	then
		# FIXME: Install nvm into bash if not already installed
		nvm install $EAVE_NODE_VERSION
	fi
}
