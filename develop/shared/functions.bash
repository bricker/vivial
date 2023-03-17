function statusmsg () {
	local usage="
		Usage: statusmsg [-diwesh] MESSAGE
		Options:
		  -d : Debug
		  -i : Info (default)
		  -w : Warn
		  -e : Error
		  -s : Success
		  -h : Prints this message and exits.
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
	local OPTIND OPTARG argname

	while getopts "diwesh" argname
	do
		case "$argname" in
			d) msgtype="debug";;
			i) msgtype="info";;
			w) msgtype="warn";;
			e) msgtype="error";;
			s) msgtype="success";;
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

	if command -v tput > /dev/null
	then
		case $msgtype in
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

	echo "[$msgtype] $msg$_cc_reset"
	return 0
}