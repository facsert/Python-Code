
CURRENT_PATH=$(pwd)
SCRIPT_DIR=$(cd $(dirname $0) && pwd)
CONFIG="requirements.txt"

function restart_service() {
    cd $SCRIPT_DIR
    nohup python main.py >/dev/null 2>&1 &
    local pid=$!
    echo $pid > pid
    return 0
}

function kill_service() {
    cd $SCRIPT_DIR
    if [[ ! -f pid ]]; then
        echo -e "\033[31mpid not exist\033[0m"
        return 1
    fi

    local pid=$(cat pid)
    local pid=$(cat pid)    
    if [[ -z $pid ]]; then
        echo -e "\033[31mpid is empty\033[0m"
        return 1
    fi

    kill -15 $pid
    if [[ $? -ne 0 ]]; then
        echo -e "\033[31mKill $pid Service failed\033[0m"
        return 1
    fi

    echo -e "\033[32mService $pid is killed\033[0m"
    rm pid
    return 0
}

function check_service() {
    if [[ ! -f pid ]]; then
        echo -e "\033[31mpid not exist\033[0m"
        return 1
    fi
    
    local pid=$(cat pid)    
    if [[ -z $pid ]]; then
        echo -e "\033[31mpid is empty\033[0m"
        return 1
    fi

    ps -aux | grep -v grep | grep "$pid"
    if [[ $? -ne 0 ]]; then
        echo -e "\033[31mService $pid is not Running\033[0m"
        return 1
    fi

    echo -e "\033[32mService $pid is Running\033[0m"
    return 0
}

function install() {
  cd $SCRIPT_DIR

  if [[ ! -f $CONFIG ]]; then
      echo -e "\033[31m $CONFIG not exist \033[0m"
      return 1
  fi

  python -m pip install -r $CONFIG
  if [[ $? -ne 0 ]]; then
    echo -e "\033[31m pip install package failed \033[0m"
    return 1
  fi

  echo -e "\033[32m install python package success\033[0m"
  return 0
}


usage=$(cat <<EOF
    -h/--help      show help      \n
    --restart      restart service \n
    --check        check service alive \n
    --kill         kill service
    --install      install package dependency
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
        kill_service
        restart_service
        check_service
        shift 1
        ;;
      --kill)
        kill_service
        shift 1
        ;;
      --check)
        check_service
        shift 1
        ;;
      --install)
        install
        shift 1
        ;;
      *)
        echo "param $1"
        params+=($1)
        shift
        ;;
    esac
done