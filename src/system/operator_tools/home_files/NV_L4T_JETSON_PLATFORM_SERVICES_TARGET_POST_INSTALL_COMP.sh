#!/bin/bash
set -e
export LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8 LANGUAGE=en_US.UTF-8

exec 3>&1
exec 1>&2
exec 2>&3
function safe_apt_install {
    export DEBIAN_FRONTEND=noninteractive
    echo "*begin $1, $2"
    tmp_log=/tmp/sdkm_apt_install_log.xueqiang.txt
    sudo rm -f $tmp_log
    set +e; $1 2>$tmp_log; CMD_STATUS=${PIPESTATUS[0]}; set -e
    MAX_RETRY=3
    TIMES=1
    while [ ${CMD_STATUS} -ne 0 ]; do
        cat $tmp_log > /dev/stderr
        if [ $TIMES -gt $MAX_RETRY ]; then
            echo "Unhandled error when running $1: `tr '\n' '; ' <$tmp_log`" 1>&2; exit 1
        fi
        if grep -q -e "is locked by another process" -e "E: Could not get lock /var/" -e "Could not open lock" $tmp_log; then
            sudo rm -f $tmp_log
            set +e; $1 2>$tmp_log; CMD_STATUS=${PIPESTATUS[0]}; set -e
            echo "Waiting $2 seconds for apt to be available"; sleep ${2}
        elif grep -q -e "apt --fix-broken install" $tmp_log; then
            echo "safe apt install failed, need to run apt --fix-broken install"
            TIMES=$[ $TIMES + 1 ]
            sudo rm -f $tmp_log
            set +e; sudo apt-get -f -y --allow-downgrades install 2>$tmp_log; CMD_STATUS=${PIPESTATUS[0]}; set -e
            echo "Waiting 5 seconds for apt"; sleep 5
        else
            echo "safe apt install failed: $1, exit code: $CMD_STATUS, retry number: $TIMES"
            echo "will sleep $[ $TIMES*10 ] seconds before next attempt"
            sleep $[ $TIMES*10 ]
            TIMES=$[ $TIMES + 1 ]
            sudo rm -f $tmp_log
            set +e; $1 2>$tmp_log; CMD_STATUS=${PIPESTATUS[0]}; set -e
        fi
    done
    if [ $CMD_STATUS -eq 0 ] && [ $TIMES -ne 1 ]; then
        echo "safe apt install succeed. retry number: $TIMES."
    fi
}
safe_apt_install "sudo apt-get -y update" 5
sleep 0.5
safe_apt_install "sudo -E apt-get -y --allow-downgrades  install /opt/nvidia/deb_repos/nvidia-jetson-services_2.0.0_arm64.deb" 5
sleep 5
sudo rm -f /opt/nvidia/deb_repos/nvidia-jetson-services_2.0.0_arm64.deb
