if test -z "${_SHARED_FUNCTIONS_LOADED:-}"; then

	export CHAR_CHECK=" ✔ "
	export CHAR_X=" X "

	function e.ci() {
		test -n "${CI:-}"
	}

	function e.onlythismodule() {
		test -n "${_ONLY_THIS_MODULE:-}"
	}

	function e.norecurse() (
		grep -qE "node_modules|\.venv|vendor" <<<"$1"
	)

	function e.status() (
		local proj
		proj="$(e.gcloudproject)"

		local url
		url="$(jq -r ".googleCloudProjects.\"$proj\".url" eavevars.json)"

		curl -s "$url/status" | jq .
	)

	function e.diff-deployed() (
		local liveversion
		liveversion="$(e.status | jq -r .version)"
		git log --oneline --reverse "$liveversion"..HEAD . "$EAVE_HOME"/libs/eave-stdlib-py
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

		while getopts "odiawesnph" argname; do
			case "$argname" in
			o) msgtype="off" ;;
			d) msgtype="debug" ;;
			i) msgtype="info" ;;
			a) msgtype="notice" ;;
			w) msgtype="warn" ;;
			e) msgtype="error" ;;
			s) msgtype="success" ;;
			n) nonewline="1" ;;
			p) noprefix="1" ;;
			h)
				echo "$usage"
				exit 0
				;;
			*)
				echo "$usage"
				exit 1
				;;
			esac
		done

		local msg="${*:${OPTIND:-1}}"
		if test -z "$msg"; then
			echo "$usage"
			exit 1
		fi

		if test "$msgtype" = "off"; then
			if test -z "$nonewline"; then
				echo -e "$msg"
			else
				echo -en "$msg"
			fi
			return 0
		fi

		local _cc_reset=""

		if ! e.ci && command -v tput >/dev/null && test -v TERM && test -n "$TERM"; then
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

			# NOTE: different terminals have different capabilities, so before adding something here, make sure it'll work on all common terminals. For example, macOS Terminal doesn't support `dim` by default, so using `dim` here causes a failure when using the macOS Terminal.
			debug)
				tput -S <<-EOC
					setaf $_cc_white
					rev
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

	function e.verify-clean-git-index() {
		if ! test -z "$(git status --porcelain)"; then
			statusmsg -e "Dirty git index!"
			exit 1
		fi
	}

	function e.shellname() {
		echo -n "$(basename "$SHELL")"
	}

	function e.shloginfile() {
		local usershell
		usershell=$(e.shellname)
		case $usershell in
		"bash")
			if test -f "$HOME/.bash_profile"; then
				echo -n "$HOME/.bash_profile"
			else
				echo -n "$HOME/.bashrc"
			fi
			;;
		"zsh")
			if test -f "$HOME/.zsh_profile"; then
				echo -n "$HOME/.zsh_profile"
			else
				echo -n "$HOME/.zshrc"
			fi
			;;
		*)
			return 0
			;;
		esac
	}

	function e.import-loginfile() {
		local loginfile
		loginfile=$(e.shloginfile)
		if test -n "$loginfile"; then
			# shellcheck disable=SC1090
			source "$loginfile"
		fi
	}

	function e.cmd-exists() {
		if command -v "$1" >/dev/null; then
			return 0
		fi

		if which "$1" >/dev/null; then
			return 0
		fi

		return 1
	}

	function e.run-in-path() (
		local path=$1
		local cmd=$2

		local ex="$path/$cmd"
		if test -x "$ex"; then
			(cd "$path" && $cmd)
		else
			statusmsg -w "File $ex is not executable."
		fi
	)

	function e.get-os() {
		local kernel
		kernel=$(e.get-kernel-name)
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

	function e.get-kernel-name() {
		uname -s | tr '[:upper:]' '[:lower:]'
	}

	function e.get-cpu-arch() {
		local arch
		arch=$(uname -m)
		if test "$arch" = "unknown"; then
			# `uname -p` isnt portible/POSIX, so it's often unknown
			# on linux systems. use `uname -m` instead in that case
			uname -m
		else
			echo "$arch"
		fi
	}

	function e.get-cpu-arch-normalized() {
		local arch
		arch=$(e.get-cpu-arch)
		case $arch in
		"arm64")
			echo -n "arm"
			;;
		"amd64")
			echo -n "x86_64"
			;;
		"i386")
			echo -n "x86_64"
			;;
		*)
			echo -n "$arch"
			;;
		esac
	}

	function e.get-cpu-arch-normalized-alt() {
		local arch
		arch=$(e.get-cpu-arch)
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

	function e.add-shell-variable() {
		local varname=$1
		local value=$2
		local usershell
		usershell=$(e.shellname)
		local varcmd=("export $varname=\"$value\"")

		case $usershell in
		"bash" | "zsh")
			local loginfile
			loginfile=$(e.shloginfile)

			if grep "export $varname" "$loginfile"; then
				statusmsg -w "variable $varname already set in $loginfile."
				return 0
			fi

			echo -e "\n${varcmd[*]}" >>"$loginfile"
			# set for this shell.
			# shellcheck disable=SC2048
			${varcmd[*]}
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
	}

	function verbose() {
		test -n "${VERBOSE:-}"
	}

	# Returns the absolute path to the dir of the program currently running
	function e.abspath() (
		cd "$(dirname "$0")" && pwd -P
	)

	# Returns the parent path of the currently _executing_ file.
	# This is useful for things in bin directories especially, when you want to call another script.
	# eg: "$(e.parentpath)/bin/lint"
	function e.parentpath() (
		cd "$(dirname "$0")/.." && pwd -P
	)

	function e.pwd() (
		# Returns the absolute path to the working directory, with the value of EAVE_HOME replaced with the literal "$EAVE_HOME", to be evaluated later.
		echo -n "\$EAVE_HOME${PWD#"$EAVE_HOME"}"
	)

	function e.gcloudproject() (
		if test -n "${GOOGLE_CLOUD_PROJECT:-}"; then
			echo -n "$GOOGLE_CLOUD_PROJECT"
		else
			gcloud --format=json info | jq -r .config.project
		fi
	)

	function e.confirm() (
		if test -n "${NOPROMPT:-}"; then
			exit 0
		fi

		statusmsg -wpn "Proceed? y/[n]:"
		statusmsg -no " "
		read -r proceed
		test "$proceed" = "y"
	)

	function e.force() {
		test -n "${FORCE:-}"
	}

	_SHARED_FUNCTIONS_LOADED=1
fi
