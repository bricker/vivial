if test -z "${_SHARED_FUNCTIONS_LOADED:-}"; then
	function ~ci () (
		test -n "${CI:-}"
	)

	function statusmsg() (
		local usage="
			Usage: statusmsg [-odiwesnh] MESSAGE
			Options:
				-o : [o]ff - No styling (pass-through to echo)
				-n : no [n]ewline - Do not emit a newline after the message (same as echo -n)
				-d : [d]ebug
				-i : [i]nfo (default)
				-a : [a]ttention (aka notice)
				-w : [w]arn
				-e : [e]rror
				-s : [s]uccess
				-p : no message [p]refix
				-h : [h]elp - Prints this message and exits.
			EOS
		"

		local msgtype="info"
		local noprefix=""
		local nonewline=""
		local OPTIND OPTARG argname

		while getopts "odiawesnph" argname
		do
			case "$argname" in
				o) msgtype="off";;
				d) msgtype="debug";;
				i) msgtype="info";;
				a) msgtype="notice";;
				w) msgtype="warn";;
				e) msgtype="error";;
				s) msgtype="success";;
				n) nonewline="1";;
				p) noprefix="1";;
				h)
					echo $usage
					exit 0
					;;
			esac
		done

		local msg="${@:${OPTIND:-1}}"
		if test -z "$msg"; then
			echo $usage
			exit 1
		fi

		if test "$msgtype" = "off"
		then
			if test -z "$nonewline"; then
				echo -e $msg
			else
				echo -en $msg
			fi
			return 0
		fi

		local _cc_reset=""

		if ! ~ci && command -v tput >/dev/null && test -v TERM && test -n "$TERM"; then
			local _cc_black=0
			local _cc_red=1
			local _cc_green=2
			local _cc_yellow=3
			local _cc_blue=4
			local _cc_magenta=5
			local _cc_cyan=6
			local _cc_white=7
			_cc_reset=$(tput sgr0)

			case $msgtype in
			off) ;;

			debug)
				tput -S <<-EOC
					setaf $_cc_white
					rev
					dim
				EOC
				;;

			info)
				tput -S <<-EOC
					setaf $_cc_cyan
					rev
				EOC
				;;

			notice)
				tput -S <<-EOC
					setaf $_cc_magenta
					rev
					bold
				EOC
				;;

			warn)
				tput -S <<-EOC
					setaf $_cc_yellow
					rev
					bold
				EOC
				;;

			error)
				tput -S <<-EOC
					setab $_cc_red
					setaf $_cc_white
					bold
				EOC
				;;

			success)
				tput -S <<-EOC
					setaf $_cc_green
					rev
					bold
				EOC
				;;
			esac
		fi

		prefix=""
		if test -z "$noprefix"; then
			prefix="[$msgtype] "
		fi

		if test -z "$nonewline"; then
			echo -e "$prefix$msg$_cc_reset"
		else
			echo -en "$prefix$msg$_cc_reset"
		fi
		return 0
	)

	function shellname() {
		echo -n "$(basename $SHELL)"
	}

	function shloginfile() {
		case $usershell in
		"bash")
			echo -n ~/.bashrc
			;;
		"zsh")
			echo -n ~/.zshrc
			;;
		*)
			return 0
			;;
		esac
	}

	function cmd-exists() {
		if command -v "$1" >/dev/null; then
			return 0
		fi

		local usershell=$(shellname)
		case $usershell in
		"fish")
			if fish -c "functions -q $1"; then
				return 0
			else
				return 1
			fi
			;;
		"bash" | "zsh")
			return 1
			;;
		*)
			return 0
			;;
		esac
	}

	function run-in-path() (
		local path=$1
		local cmd=$2

		local ex="$path/$cmd"
		if test -x "$ex"; then
			(cd $path && $cmd)
		else
			statusmsg -w "File $ex is not executable."
		fi
	)

	function get-os() {
		local kernel=$(get-kernel-name)
		case "$kernel" in
		"linux")
			lsb_release -is | tr '[:upper:]' '[:lower:]'
			;;
		"darwin")
			echo -n "macos"
			;;
		*)
			statusmsg -e "Your OS isn't supported by this script. Please add support!"
			exit 1
			;;
		esac
	}

	function get-kernel-name() {
		uname -s | tr '[:upper:]' '[:lower:]'
	}

	function get-cpu-arch() {
		local arch=$(uname -p)
		if test "$arch" = "unknown"; then
			# `uname -p` isnt portible/POSIX, so it's often unknown
			# on linux systems. use `uname -m` instead in that case
			uname -m
		else
			echo "$arch"
		fi
	}

	function get-cpu-arch-normalized() {
		local arch=$(get-cpu-arch)
		case $arch in
		"arm64")
			echo -n "arm"
			;;
		"amd64")
			echo -n "x86_64"
			;;
		*)
			echo -n "$arch"
			;;
		esac
	}

	function get-cpu-arch-normalized-alt() {
		local arch=$(get-cpu-arch)
		case $arch in
		"arm")
			echo -n "arm64"
			;;
		"x86_64")
			echo -n "amd64"
			;;
		*)
			echo -n "$arch"
			;;
		esac
	}

	function ~add-shell-variable() {
		local varname=$1
		local value=$2
		local usershell=$(shellname)
		local varcmd="export $varname=\"$value\""

		case $usershell in
		"bash" | "zsh")
			local loginfile=$(shloginfile)

			if cat $loginfile | grep "export $varname"; then
				statusmsg -w "variable $varname already set in $loginfile."
				return 0
			fi

			echo -e "\n$varcmd" >>"$loginfile"
			;;
		"fish")
			if fish -c "set -q $varname"; then
				statusmsg -w "variable $varname already set in fish environment."
				return 0
			fi
			fish -c "set -Ux $varname $value"
			;;
		*)
			statusmsg -w "Your shell ($usershell) isn't supported by this script. Please update this script to add support!"
			;;
		esac

		$varcmd
	}

	function run-with-dotenv() (
		python-validate-version
		python-activate-venv
		PYTHONPATH=. python -m dotenv --file $EAVE_HOME/.env run --no-override -- "$@"
	)

	function run-appengine-dev-server() (
		statusmsg -i "This script requires the gcloud SDK to be installed and in your path"
		statusmsg -i "Additionally, a python2 program must be installed and in your PATH."
		statusmsg -i "https://cloud.google.com/appengine/docs/legacy/standard/python/tools/using-local-server"

		local usage="Usage: run-appengine-dev-server -p PORT"
		local port=""
		while getopts "p:" argname; do
			case "$argname" in
			p) port=$OPTARG ;;
			h)
				statusmsg -i "$usage"
				exit 0
				;;
			esac
		done

		if test -z "$port"; then
			statusmsg -e "$usage"
			exit 1
		fi

		run-with-dotenv \
			dev_appserver.py \
			--host localhost \
			--port "$port" \
			app.yaml
	)

	function verbose () (
		test -n "${VERBOSE:-}"
	)

	# On purpose using curly-braces; this function is meant to be called in a deployment script and puts the script into the correct directory.
	function setup-deployment-workspace () {
		local builddir=$EAVE_HOME/.build
		local appname=$(basename $PWD)
		mkdir -p $builddir
		rm -rf $builddir/$appname

		local vflag=""
		if verbose; then
			vflag="-v"
		fi

		rsync -a $vflag \
			--exclude='.git' \
			--exclude 'node_modules' \
			--exclude '.yalc' \
			--exclude 'vendor' \
			--exclude 'dist' \
			--exclude '.venv' \
			--exclude '.ruff_cache' \
			--exclude '.mypy_cache' \
			--exclude '__pycache__' \
			--exclude '*.pyc' \
			$PWD $builddir

		cd $builddir/$appname && \
		cp $EAVE_HOME/.gitignore . && \
		cp $EAVE_HOME/.gcloudignore . && \
		cp $EAVE_HOME/.gcloudignore-builder .
	}

	function clean-deployment-workspace () {
		local builddir=$EAVE_HOME/.build
		local appname=$(basename $PWD)
		rm -r $builddir/$appname
	}

	# Returns the absolute path to the dir of the program currently running
	function ~abspath () (
		cd $(dirname $0) && pwd -P
	)

	function ~parentpath () (
		cd $(dirname $0)/.. && pwd -P
	)

	function ~eavepwd () (
		echo -n "\$EAVE_HOME${PWD#"$EAVE_HOME"}"
	)

	function ~gcloudproject() (
		if test -n "${GOOGLE_CLOUD_PROJECT:-}"; then
			echo -n "$GOOGLE_CLOUD_PROJECT"
		else
			gcloud --format=json info | jq -r .config.project
		fi
	)

	_SHARED_FUNCTIONS_LOADED=1
fi
