### Prompt

```
SYSTEM:
You will be given a GitHub organization name, a repository name, a file path to some code in that repository, the code in that file (delimited by three exclamation marks), and a list of known services. Your task is to find which (if any) services are referenced in the code. If a similar service is in the list of known services, use that. Otherwise, create a human-readable name for the service. Your answer will be used to create a high-level system architecture diagram.

Only consider services that are likely to be external to this application. For example, you should not include dependencies on the language's standard libraries, utility functions, things like that. For each dependency that

Output your answer as a JSON array of strings, where each string is the name of the service referenced in the code. Each one should exactly match the provided service name. Your full response should be JSON-parseable, with no indentation or newlines between objects.
```

```
USER:
GitHub organization: eave-fyi

Repository: eave-monorepo

Known services:
- Eave DevOps
- Eave Development Tools
- Eave Core
- Eave Slack Integration
- Eave Jira Integration
- Eave Github Integration
- Eave Confluence Integration
- Eave Marketing
- Eave Archer
- Eave Standard Libraries
- Google Cloud Platform
File path: /home/bryan/code/eave/eave-monorepo/develop/shared/_functions.bash

Code:
!!!
if test -z "${_SHARED_FUNCTIONS_LOADED:-}"; then

	function ^ci() {
		test -n "${CI:-}"
	}

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

		if ! ^ci && command -v tput >/dev/null && test -v TERM && test -n "$TERM"; then
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
		echo -n "$(basename "$SHELL")"
	}

	function shloginfile() {
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

	function cmd-exists() {
		if command -v "$1" >/dev/null; then
			return 0
		fi

		local usershell
		usershell=$(shellname)
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
			(cd "$path" && $cmd)
		else
			statusmsg -w "File $ex is not executable."
		fi
	)

	function get-os() {
		local kernel
		kernel=$(get-kernel-name)
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

	function get-cpu-arch-normalized() {
		local arch
		arch=$(get-cpu-arch)
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

	function get-cpu-arch-normalized-alt() {
		local arch
		arch=$(get-cpu-arch)
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

	function ^add-shell-variable() {
		local varname=$1
		local value=$2
		local usershell
		usershell=$(shellname)
		local varcmd=("export $varname=\"$value\"")

		case $usershell in
		"bash" | "zsh")
			local loginfile
			loginfile=$(shloginfile)

			if grep "export $varname" "$loginfile"; then
				statusmsg -w "variable $varname already set in $loginfile."
				return 0
			fi

			echo -e "\n${varcmd[*]}" >>"$loginfile"
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

		"${varcmd[*]}"
	}

	function run-with-dotenv() (
		python-validate-version
		python-activate-venv
		PYTHONPATH=. python -m dotenv --file "$EAVE_HOME/.env" run --no-override -- "$@"
	)

	function run-appengine-dev-server() (
		statusmsg -i "This script requires the gcloud SDK to be installed and in your path"
		statusmsg -i "Additionally, a python2 program must be installed and in your PATH."
		statusmsg -i "https://cloud.google.com/appengine/docs/legacy/standard/python/tools/using-local-server"

		local usage="Usage: run-appengine-dev-server -p PORT"
		local port=""
		while getopts "p:h" argname; do
			case "$argname" in
			p) port=$OPTARG ;;
			h)
				statusmsg -i "$usage"
				exit 0
				;;
			*)
				statusmsg -i "$usage"
				exit 1
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

	function verbose() {
		test -n "${VERBOSE:-}"
	}

	# On purpose using curly-braces; this function is meant to be called in a deployment script and puts the script into the correct directory.
	function setup-deployment-workspace() {
		local builddir="$EAVE_HOME/.build"
		local appname
		appname=$(basename "$PWD")
		mkdir -p "$builddir"
		rm -rf "${builddir:?}/${appname:?}"

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
			"$PWD" "$builddir"

		cd "${builddir:?}/${appname:?}" &&
			cp "$EAVE_HOME/.gitignore" . &&
			cp "$EAVE_HOME/.gcloudignore" . &&
			cp "$EAVE_HOME/.gcloudignore-builder" .
	}

	function clean-deployment-workspace() {
		local builddir=$EAVE_HOME/.build
		local appname
		appname=$(basename "$PWD")
		rm -r "${builddir:?}/${appname:?}"
	}

	# Returns the absolute path to the dir of the program currently running
	function ^abspath() (
		cd "$(dirname "$0")" && pwd -P
	)

	function ^parentpath() (
		cd "$(dirname "$0")/.." && pwd -P
	)

	function ^eavepwd() (
		echo -n "\$EAVE_HOME${PWD#"$EAVE_HOME"}"
	)

	function ^gcloudproject() (
		if test -n "${GOOGLE_CLOUD_PROJECT:-}"; then
			echo -n "$GOOGLE_CLOUD_PROJECT"
		else
			gcloud --format=json info | jq -r .config.project
		fi
	)

	_SHARED_FUNCTIONS_LOADED=1
fi

!!!
```

### Request

```json
{
  "model": "gpt-4",
  "messages": [
    {
      "content": "You will be given a GitHub organization name, a repository name, a file path to some code in that repository, the code in that file (delimited by three exclamation marks), and a list of known services. Your task is to find which (if any) services are referenced in the code. If a similar service is in the list of known services, use that. Otherwise, create a human-readable name for the service. Your answer will be used to create a high-level system architecture diagram.\n\nOnly consider services that are likely to be external to this application. For example, you should not include dependencies on the language's standard libraries, utility functions, things like that. For each dependency that\n\nOutput your answer as a JSON array of strings, where each string is the name of the service referenced in the code. Each one should exactly match the provided service name. Your full response should be JSON-parseable, with no indentation or newlines between objects.",
      "role": "system"
    },
    {
      "content": "GitHub organization: eave-fyi\n\nRepository: eave-monorepo\n\nKnown services:\n- Eave DevOps\n- Eave Development Tools\n- Eave Core\n- Eave Slack Integration\n- Eave Jira Integration\n- Eave Github Integration\n- Eave Confluence Integration\n- Eave Marketing\n- Eave Archer\n- Eave Standard Libraries\n- Google Cloud Platform\nFile path: /home/bryan/code/eave/eave-monorepo/develop/shared/_functions.bash\n\nCode:\n!!!\nif test -z \"${_SHARED_FUNCTIONS_LOADED:-}\"; then\n\n\tfunction ^ci() {\n\t\ttest -n \"${CI:-}\"\n\t}\n\n\tfunction statusmsg() (\n\t\tlocal usage=\"\n\t\t\tUsage: statusmsg [-odiwesnh] MESSAGE\n\t\t\tOptions:\n\t\t\t\t-o : [o]ff - No styling (pass-through to echo)\n\t\t\t\t-n : no [n]ewline - Do not emit a newline after the message (same as echo -n)\n\t\t\t\t-d : [d]ebug\n\t\t\t\t-i : [i]nfo (default)\n\t\t\t\t-a : [a]ttention (aka notice)\n\t\t\t\t-w : [w]arn\n\t\t\t\t-e : [e]rror\n\t\t\t\t-s : [s]uccess\n\t\t\t\t-p : no message [p]refix\n\t\t\t\t-h : [h]elp - Prints this message and exits.\n\t\t\tEOS\n\t\t\"\n\n\t\tlocal msgtype=\"info\"\n\t\tlocal noprefix=\"\"\n\t\tlocal nonewline=\"\"\n\t\tlocal OPTIND OPTARG argname\n\n\t\twhile getopts \"odiawesnph\" argname; do\n\t\t\tcase \"$argname\" in\n\t\t\to) msgtype=\"off\" ;;\n\t\t\td) msgtype=\"debug\" ;;\n\t\t\ti) msgtype=\"info\" ;;\n\t\t\ta) msgtype=\"notice\" ;;\n\t\t\tw) msgtype=\"warn\" ;;\n\t\t\te) msgtype=\"error\" ;;\n\t\t\ts) msgtype=\"success\" ;;\n\t\t\tn) nonewline=\"1\" ;;\n\t\t\tp) noprefix=\"1\" ;;\n\t\t\th)\n\t\t\t\techo \"$usage\"\n\t\t\t\texit 0\n\t\t\t\t;;\n\t\t\t*)\n\t\t\t\techo \"$usage\"\n\t\t\t\texit 1\n\t\t\t\t;;\n\t\t\tesac\n\t\tdone\n\n\t\tlocal msg=\"${*:${OPTIND:-1}}\"\n\t\tif test -z \"$msg\"; then\n\t\t\techo \"$usage\"\n\t\t\texit 1\n\t\tfi\n\n\t\tif test \"$msgtype\" = \"off\"; then\n\t\t\tif test -z \"$nonewline\"; then\n\t\t\t\techo -e \"$msg\"\n\t\t\telse\n\t\t\t\techo -en \"$msg\"\n\t\t\tfi\n\t\t\treturn 0\n\t\tfi\n\n\t\tlocal _cc_reset=\"\"\n\n\t\tif ! ^ci && command -v tput >/dev/null && test -v TERM && test -n \"$TERM\"; then\n\t\t\tlocal _cc_black=0\n\t\t\tlocal _cc_red=1\n\t\t\tlocal _cc_green=2\n\t\t\tlocal _cc_yellow=3\n\t\t\tlocal _cc_blue=4\n\t\t\tlocal _cc_magenta=5\n\t\t\tlocal _cc_cyan=6\n\t\t\tlocal _cc_white=7\n\t\t\t_cc_reset=$(tput sgr0)\n\n\t\t\tcase $msgtype in\n\t\t\toff) ;;\n\n\t\t\tdebug)\n\t\t\t\ttput -S <<-EOC\n\t\t\t\t\tsetaf $_cc_white\n\t\t\t\t\trev\n\t\t\t\t\tdim\n\t\t\t\tEOC\n\t\t\t\t;;\n\n\t\t\tinfo)\n\t\t\t\ttput -S <<-EOC\n\t\t\t\t\tsetaf $_cc_cyan\n\t\t\t\t\trev\n\t\t\t\tEOC\n\t\t\t\t;;\n\n\t\t\tnotice)\n\t\t\t\ttput -S <<-EOC\n\t\t\t\t\tsetaf $_cc_magenta\n\t\t\t\t\trev\n\t\t\t\t\tbold\n\t\t\t\tEOC\n\t\t\t\t;;\n\n\t\t\twarn)\n\t\t\t\ttput -S <<-EOC\n\t\t\t\t\tsetaf $_cc_yellow\n\t\t\t\t\trev\n\t\t\t\t\tbold\n\t\t\t\tEOC\n\t\t\t\t;;\n\n\t\t\terror)\n\t\t\t\ttput -S <<-EOC\n\t\t\t\t\tsetab $_cc_red\n\t\t\t\t\tsetaf $_cc_white\n\t\t\t\t\tbold\n\t\t\t\tEOC\n\t\t\t\t;;\n\n\t\t\tsuccess)\n\t\t\t\ttput -S <<-EOC\n\t\t\t\t\tsetaf $_cc_green\n\t\t\t\t\trev\n\t\t\t\t\tbold\n\t\t\t\tEOC\n\t\t\t\t;;\n\t\t\tesac\n\t\tfi\n\n\t\tprefix=\"\"\n\t\tif test -z \"$noprefix\"; then\n\t\t\tprefix=\"[$msgtype] \"\n\t\tfi\n\n\t\tif test -z \"$nonewline\"; then\n\t\t\techo -e \"$prefix$msg$_cc_reset\"\n\t\telse\n\t\t\techo -en \"$prefix$msg$_cc_reset\"\n\t\tfi\n\t\treturn 0\n\t)\n\n\tfunction shellname() {\n\t\techo -n \"$(basename \"$SHELL\")\"\n\t}\n\n\tfunction shloginfile() {\n\t\tcase $usershell in\n\t\t\"bash\")\n\t\t\tif test -f \"$HOME/.bash_profile\"; then\n\t\t\t\techo -n \"$HOME/.bash_profile\"\n\t\t\telse\n\t\t\t\techo -n \"$HOME/.bashrc\"\n\t\t\tfi\n\t\t\t;;\n\t\t\"zsh\")\n\t\t\tif test -f \"$HOME/.zsh_profile\"; then\n\t\t\t\techo -n \"$HOME/.zsh_profile\"\n\t\t\telse\n\t\t\t\techo -n \"$HOME/.zshrc\"\n\t\t\tfi\n\t\t\t;;\n\t\t*)\n\t\t\treturn 0\n\t\t\t;;\n\t\tesac\n\t}\n\n\tfunction cmd-exists() {\n\t\tif command -v \"$1\" >/dev/null; then\n\t\t\treturn 0\n\t\tfi\n\n\t\tlocal usershell\n\t\tusershell=$(shellname)\n\t\tcase $usershell in\n\t\t\"fish\")\n\t\t\tif fish -c \"functions -q $1\"; then\n\t\t\t\treturn 0\n\t\t\telse\n\t\t\t\treturn 1\n\t\t\tfi\n\t\t\t;;\n\t\t\"bash\" | \"zsh\")\n\t\t\treturn 1\n\t\t\t;;\n\t\t*)\n\t\t\treturn 0\n\t\t\t;;\n\t\tesac\n\t}\n\n\tfunction run-in-path() (\n\t\tlocal path=$1\n\t\tlocal cmd=$2\n\n\t\tlocal ex=\"$path/$cmd\"\n\t\tif test -x \"$ex\"; then\n\t\t\t(cd \"$path\" && $cmd)\n\t\telse\n\t\t\tstatusmsg -w \"File $ex is not executable.\"\n\t\tfi\n\t)\n\n\tfunction get-os() {\n\t\tlocal kernel\n\t\tkernel=$(get-kernel-name)\n\t\tcase \"$kernel\" in\n\t\t\"linux\")\n\t\t\tlsb_release -is | tr '[:upper:]' '[:lower:]'\n\t\t\t;;\n\t\t\"darwin\")\n\t\t\techo -n \"macos\"\n\t\t\t;;\n\t\t*)\n\t\t\tstatusmsg -e \"Your OS isn't supported by this script. Please add support!\"\n\t\t\texit 1\n\t\t\t;;\n\t\tesac\n\t}\n\n\tfunction get-kernel-name() {\n\t\tuname -s | tr '[:upper:]' '[:lower:]'\n\t}\n\n\tfunction get-cpu-arch() {\n\t\tlocal arch\n\t\tarch=$(uname -m)\n\t\tif test \"$arch\" = \"unknown\"; then\n\t\t\t# `uname -p` isnt portible/POSIX, so it's often unknown\n\t\t\t# on linux systems. use `uname -m` instead in that case\n\t\t\tuname -m\n\t\telse\n\t\t\techo \"$arch\"\n\t\tfi\n\t}\n\n\tfunction get-cpu-arch-normalized() {\n\t\tlocal arch\n\t\tarch=$(get-cpu-arch)\n\t\tcase $arch in\n\t\t\"arm64\")\n\t\t\techo -n \"arm\"\n\t\t\t;;\n\t\t\"amd64\")\n\t\t\techo -n \"x86_64\"\n\t\t\t;;\n\t\t\"i386\")\n\t\t\techo -n \"x86_64\"\n\t\t\t;;\n\t\t*)\n\t\t\techo -n \"$arch\"\n\t\t\t;;\n\t\tesac\n\t}\n\n\tfunction get-cpu-arch-normalized-alt() {\n\t\tlocal arch\n\t\tarch=$(get-cpu-arch)\n\t\tcase $arch in\n\t\t\"arm\")\n\t\t\techo -n \"arm64\"\n\t\t\t;;\n\t\t\"x86_64\")\n\t\t\techo -n \"amd64\"\n\t\t\t;;\n\t\t*)\n\t\t\techo -n \"$arch\"\n\t\t\t;;\n\t\tesac\n\t}\n\n\tfunction ^add-shell-variable() {\n\t\tlocal varname=$1\n\t\tlocal value=$2\n\t\tlocal usershell\n\t\tusershell=$(shellname)\n\t\tlocal varcmd=(\"export $varname=\\\"$value\\\"\")\n\n\t\tcase $usershell in\n\t\t\"bash\" | \"zsh\")\n\t\t\tlocal loginfile\n\t\t\tloginfile=$(shloginfile)\n\n\t\t\tif grep \"export $varname\" \"$loginfile\"; then\n\t\t\t\tstatusmsg -w \"variable $varname already set in $loginfile.\"\n\t\t\t\treturn 0\n\t\t\tfi\n\n\t\t\techo -e \"\\n${varcmd[*]}\" >>\"$loginfile\"\n\t\t\t;;\n\t\t\"fish\")\n\t\t\tif fish -c \"set -q $varname\"; then\n\t\t\t\tstatusmsg -w \"variable $varname already set in fish environment.\"\n\t\t\t\treturn 0\n\t\t\tfi\n\t\t\tfish -c \"set -Ux $varname $value\"\n\t\t\t;;\n\t\t*)\n\t\t\tstatusmsg -w \"Your shell ($usershell) isn't supported by this script. Please update this script to add support!\"\n\t\t\t;;\n\t\tesac\n\n\t\t\"${varcmd[*]}\"\n\t}\n\n\tfunction run-with-dotenv() (\n\t\tpython-validate-version\n\t\tpython-activate-venv\n\t\tPYTHONPATH=. python -m dotenv --file \"$EAVE_HOME/.env\" run --no-override -- \"$@\"\n\t)\n\n\tfunction run-appengine-dev-server() (\n\t\tstatusmsg -i \"This script requires the gcloud SDK to be installed and in your path\"\n\t\tstatusmsg -i \"Additionally, a python2 program must be installed and in your PATH.\"\n\t\tstatusmsg -i \"https://cloud.google.com/appengine/docs/legacy/standard/python/tools/using-local-server\"\n\n\t\tlocal usage=\"Usage: run-appengine-dev-server -p PORT\"\n\t\tlocal port=\"\"\n\t\twhile getopts \"p:h\" argname; do\n\t\t\tcase \"$argname\" in\n\t\t\tp) port=$OPTARG ;;\n\t\t\th)\n\t\t\t\tstatusmsg -i \"$usage\"\n\t\t\t\texit 0\n\t\t\t\t;;\n\t\t\t*)\n\t\t\t\tstatusmsg -i \"$usage\"\n\t\t\t\texit 1\n\t\t\t\t;;\n\t\t\tesac\n\t\tdone\n\n\t\tif test -z \"$port\"; then\n\t\t\tstatusmsg -e \"$usage\"\n\t\t\texit 1\n\t\tfi\n\n\t\trun-with-dotenv \\\n\t\t\tdev_appserver.py \\\n\t\t\t--host localhost \\\n\t\t\t--port \"$port\" \\\n\t\t\tapp.yaml\n\t)\n\n\tfunction verbose() {\n\t\ttest -n \"${VERBOSE:-}\"\n\t}\n\n\t# On purpose using curly-braces; this function is meant to be called in a deployment script and puts the script into the correct directory.\n\tfunction setup-deployment-workspace() {\n\t\tlocal builddir=\"$EAVE_HOME/.build\"\n\t\tlocal appname\n\t\tappname=$(basename \"$PWD\")\n\t\tmkdir -p \"$builddir\"\n\t\trm -rf \"${builddir:?}/${appname:?}\"\n\n\t\tlocal vflag=\"\"\n\t\tif verbose; then\n\t\t\tvflag=\"-v\"\n\t\tfi\n\n\t\trsync -a $vflag \\\n\t\t\t--exclude='.git' \\\n\t\t\t--exclude 'node_modules' \\\n\t\t\t--exclude '.yalc' \\\n\t\t\t--exclude 'vendor' \\\n\t\t\t--exclude 'dist' \\\n\t\t\t--exclude '.venv' \\\n\t\t\t--exclude '.ruff_cache' \\\n\t\t\t--exclude '.mypy_cache' \\\n\t\t\t--exclude '__pycache__' \\\n\t\t\t--exclude '*.pyc' \\\n\t\t\t\"$PWD\" \"$builddir\"\n\n\t\tcd \"${builddir:?}/${appname:?}\" &&\n\t\t\tcp \"$EAVE_HOME/.gitignore\" . &&\n\t\t\tcp \"$EAVE_HOME/.gcloudignore\" . &&\n\t\t\tcp \"$EAVE_HOME/.gcloudignore-builder\" .\n\t}\n\n\tfunction clean-deployment-workspace() {\n\t\tlocal builddir=$EAVE_HOME/.build\n\t\tlocal appname\n\t\tappname=$(basename \"$PWD\")\n\t\trm -r \"${builddir:?}/${appname:?}\"\n\t}\n\n\t# Returns the absolute path to the dir of the program currently running\n\tfunction ^abspath() (\n\t\tcd \"$(dirname \"$0\")\" && pwd -P\n\t)\n\n\tfunction ^parentpath() (\n\t\tcd \"$(dirname \"$0\")/..\" && pwd -P\n\t)\n\n\tfunction ^eavepwd() (\n\t\techo -n \"\\$EAVE_HOME${PWD#\"$EAVE_HOME\"}\"\n\t)\n\n\tfunction ^gcloudproject() (\n\t\tif test -n \"${GOOGLE_CLOUD_PROJECT:-}\"; then\n\t\t\techo -n \"$GOOGLE_CLOUD_PROJECT\"\n\t\telse\n\t\t\tgcloud --format=json info | jq -r .config.project\n\t\tfi\n\t)\n\n\t_SHARED_FUNCTIONS_LOADED=1\nfi\n\n!!!",
      "role": "user"
    }
  ],
  "frequency_penalty": -1,
  "presence_penalty": -1,
  "temperature": 0,
  "stop": [
    "STOP_SEQUENCE"
  ]
}
```

### Response

```json
{
  "id": "chatcmpl-7bFgDAoqzKft7hjkQWTWMqZPDRHJM",
  "object": "chat.completion",
  "created": 1689112765,
  "model": "gpt-4-0613",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "[\"Google Cloud Platform\"]"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 2933,
    "completion_tokens": 5,
    "total_tokens": 2938
  }
}
```

