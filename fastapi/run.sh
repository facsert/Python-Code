
CURRENT_DIR=$(pwd)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

function kill_process() {
    cd $SCRIPT_DIR
    if [[ ! -f pid ]]; then
        echo -e "\033[31mpid not exists \033[0m"
        return 1
    fi
    local pid=$(cat pid)
    if [[ -z $pid ]]; then
        echo -e "\033[31mpid is empty \033[0m"
        return 1
    fi
    
    kill -15 $pid >/dev/null 2>&1
    rm pid
    return 0
}

function start_process() {
    cd $SCRIPT_DIR
    nohup python main.py >/dev/null 2>&1 &
    local pid=$!
    ps -aux | grep -v grep | grep $pid >/dev/null 2>&1
    echo $pid > pid
    return 0
}

function check_process() {
    cd $SCRIPT_DIR
    if [[ ! -f pid ]]; then
        echo -e "\033[31mpid not exists \033[0m"
        return 1
    fi
    local pid=$(cat pid)
    if [[ -z $pid ]]; then
        echo -e "\033[31mpid is empty \033[0m"
        return 1
    fi

    ps -aux | grep -v grep | grep $pid
    if [[ $? -ne 0 ]]; then 
        echo -e "\033[31mProcess is not running\033[0m"
        return 1
    fi
    echo -e "\033[32mProcess is running\033[0m" 
    return 0
}

usage=$(cat <<EOF
  -h/--help      show help           \n
  --restart      restart service     \n
  --kill         close service       \n
  --check        check service alive \n
EOF
)

declare -a params
while [[ $# -gt 0 ]]; do
    case $1 in
      -h|--help)
        echo -e $usage
        exit 0
        ;;
      --restart)
        cd $SCRIPT_DIR
        kill_process
        start_process
        check_process
        cd $CURRENT_DIR
        shift
        ;;
      --kill)
        cd $SCRIPT_DIR
        kill_process
        check_process
        cd $CURRENT_DIR
        shift
        ;;
      --check)
        cd $SCRIPT_DIR
        check_process
        cd $CURRENT_DIR
        shift
        ;;
      *)
        echo "param $1"
        params+=($1)
        shift
        ;;
    esac
done