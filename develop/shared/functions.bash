function statusmsg () {
	local usage="
		Usage: statusmsg [-odiwesnh] MESSAGE
		Options:
			-o : [o]ff - No styling (pass-through to echo)
		  -d : [d]ebug
		  -i : [i]nfo (default)
		  -w : [w]arn
		  -e : [e]rror
		  -s : [s]uccess
			-n : [n]o message prefix
		  -h : [h]elp - Prints this message and exits.
		EOS
	"

	local _cc_black=0
	local _cc_red=1
	local _cc_green=2
	local _cc_yellow=3
	local _cc_blue=4
	local _cc_magenta=5
	local _cc_cyan=6
	local _cc_white=7
	local _cc_reset=$(tput sgr0)

	local msgtype="info"
	local noprefix=""
	local OPTIND OPTARG argname

	while getopts "odiwesnh" argname
	do
		case "$argname" in
			o) msgtype="off";;
			d) msgtype="debug";;
			i) msgtype="info";;
			w) msgtype="warn";;
			e) msgtype="error";;
			s) msgtype="success";;
			n) noprefix="1";;
			h)
				echo $usage
				exit 0
				;;
		esac
	done

	local msg="${@:${OPTIND:-1}}"
	if test -z "$msg"
	then
		echo $usage
		exit 1
	fi

	if test "$msgtype" = "off"
	then
		echo -e $msg
		return 0
	fi

	if command -v tput > /dev/null
	then
		case $msgtype in
			off)
				;;

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
	if test -z "$noprefix"
	then
		prefix="[$msgtype] "
	fi

	echo -e "$prefix$msg$_cc_reset"
	return 0
}

function shellname () {
	echo -n "$(basename $SHELL)"
}

function command_exists () {
	if command -v "$1" > /dev/null
	then
		return 0
	fi

	local usershell=$(shellname)
	case $usershell in
		"fish")
			if fish -c "functions -q $1"
			then
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

function activate_venv () {
	if test -f .venv/bin/activate
	then
		source .venv/bin/activate
	fi
}

function run_in_all_projects () {
	if test -z "$1"
	then
		statusmsg -e "Usage: run_in_all_projects bin/lint"
		exit 1
	fi

	local cmd=$1

	for dir in $(ls -d ./apps/*/ ./libs/*/)
	do
		statusmsg -i "$dir"

		if test -x $dir$cmd
		then
			cd $dir
			activate_venv
			$cmd
			cd - > /dev/null
		else
			statusmsg -w "No $cmd executable found in $dir"
		fi

		echo -e "\n"
	done
}