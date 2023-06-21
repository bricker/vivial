if test -z "${_SHARED_FUNCTIONS_LOADED:-}"; then
	function statusmsg() (
		local usage="
			Usage: statusmsg [-odiwesnh] MESSAGE
			Options:
				-o : [o]ff - No styling (pass-through to echo)
				-n : no [n]ewline - Do not emit a newline after the message (same as echo -n)
				-d : [d]ebug
				-i : [i]nfo (default)
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

		while getopts "odiwesnph" argname
		do
			case "$argname" in
				o) msgtype="off";;
				d) msgtype="debug";;
				i) msgtype="info";;
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

		if command -v tput >/dev/null && test -v TERM && test -n "$TERM"; then

			local _cc_black=0
			local _cc_red=1
			local _cc_green=2
			local _cc_yellow=3
			local _cc_blue=4
			local _cc_magenta=5
			local _cc_cyan=6
			local _cc_white=7
			local _cc_reset=$(tput sgr0)

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
			statusmsg -e "Shell $usershell not supported. Please add support!"
			return 1
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

	function run-in-all-projects() (
		if test -z "$1"; then
			statusmsg -e "Usage: run-in-all-projects bin/lint"
			exit 1
		fi

		local cmd=$1

		for dir in $(ls -d ./apps/* ./libs/*); do
			if test "$dir" = "__pycache__"; then
				continue
			fi
			statusmsg -i "$dir"
			run-in-path "$dir" "$cmd"
			echo -e "\n"
		done
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

	function add-shell-variable() {
		local varname=$1
		local value=$2
		local usershell=$(shellname)

		case $usershell in
		"bash" | "zsh")
			local loginfile=$(shloginfile)

			if cat $loginfile | grep "export $varname"; then
				statusmsg -w "variable $varname already set in $loginfile."
				return 0
			fi

			local varcmd="export $varname=\"$value\""
			echo -e "\n$varcmd" >>"$loginfile"
			source "$loginfile"
			;;
		"fish")
			varcmd="set -Ux $varname $value"
			if fish -c "set -q $varname"; then
				statusmsg -w "variable $varname already set in fish environment."
				return 0
			fi
			fish -c "$varcmd"
			;;
		*)
			statusmsg -w "Your shell ($usershell) isn't supported by this script. Please update this script to add support!"
			;;
		esac
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

	function verbose () {
		test -n "${VERBOSE:-}"
	}

	_SHARED_FUNCTIONS_LOADED=1
fi
