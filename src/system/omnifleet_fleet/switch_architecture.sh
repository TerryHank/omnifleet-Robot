#!/usr/bin/env bash
set -euo pipefail

if [ "${EUID}" -ne 0 ]; then
  echo "请使用 sudo 运行此脚本" >&2
  exit 2
fi
mode="${1:-}"
case "${mode}" in
  pure_mola)
    publish_odom_tf=false
    ;;
  rep105)
    publish_odom_tf=true
    ;;
  *)
    echo "用法: sudo $0 pure_mola|rep105" >&2
    exit 2
    ;;
esac

if pgrep -af '[m]ola-cli|[n]av2_direct.launch.py' >/dev/null; then
  echo "请先停止当前 MOLA/Nav2 应用，再切换架构；脚本没有停止它们。" >&2
  exit 3
fi

install -d -m 755 /etc/omnifleet_t2
tmp="$(mktemp /etc/omnifleet_t2/.architecture.env.XXXXXX)"
trap 'rm -f "${tmp}"' EXIT
printf 'OMNIFLEET_ARCHITECTURE=%s\nOMNIFLEET_PUBLISH_ODOM_TF=%s\n' "${mode}" "${publish_odom_tf}" > "${tmp}"
chown root:root "${tmp}"
chmod 644 "${tmp}"
mv -f "${tmp}" /etc/omnifleet_t2/architecture.env
trap - EXIT
systemctl restart omnifleet-t2-chassis.service
echo "已切换到 ${mode}；底盘 odom->base_link 发布=${publish_odom_tf}。现在再启动 unified launch。"
