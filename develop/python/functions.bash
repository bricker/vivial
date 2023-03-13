EAVE_PYTHON_VERSION=3.11

function python-validate-version () {
    local current_version=$(python --version)
    if ! $(echo -n "$current_version" | grep -q "Python $EAVE_PYTHON_VERSION")
    then
        echo "ERROR: The 'python' executable in your path must be version $EAVE_PYTHON_VERSION. Your current version: $current_version"
        exit 1
    fi
}

function python-create-venv () {
    rm -rf .venv
    python -m venv .venv
}

function python-activate-venv () {
    if ! test -d .venv
    then
        python-create-venv
    fi

    source .venv/bin/activate
}
