#!/usr/bin/env bash
set -eo pipefail

stamp="${1:?backup timestamp required}"
backup_dir="/home/iecme/backups"
base="tank-state-${stamp}"
archive="${backup_dir}/${base}.tar.zst"
checksum="${archive}.sha256"
metadata="/home/iecme/.tank_backup_metadata_${stamp}"

cleanup() {
  resolved_metadata="$(realpath -m -- "${metadata}")"
  case "${resolved_metadata}" in
    /home/iecme/.tank_backup_metadata_[0-9]*)
      sudo rm -rf -- "${resolved_metadata}"
      ;;
  esac
}
trap cleanup EXIT

mkdir -p "${backup_dir}"
sudo mkdir -p "${metadata}"
sudo chown -R iecme:iecme "${metadata}"

{
  echo "backup_name=${base}"
  echo "created=$(date --iso-8601=seconds)"
  echo "hostname=$(hostname)"
  echo "user=iecme"
  echo "kernel=$(uname -a)"
  echo "archive_layout=paths relative to Linux root filesystem"
  echo "excluded=caches, browser profiles, ROS logs, downloads, installers, private SSH/GPG keys"
} > "${metadata}/backup_info.txt"

cat /etc/os-release > "${metadata}/os-release.txt"
dpkg-query -W -f='${binary:Package}\t${Version}\n' > "${metadata}/dpkg-packages.tsv"
apt-mark showmanual > "${metadata}/apt-manual.txt"
python3 -m pip freeze > "${metadata}/python-pip-freeze.txt" 2>&1 || true

(
  source /opt/ros/humble/setup.bash
  for setup_file in /home/iecme/*_ws/install/setup.bash; do
    [[ -f "${setup_file}" ]] && source "${setup_file}"
  done
  ros2 pkg list
) > "${metadata}/ros2-packages.txt" 2>&1 || true

systemctl list-unit-files --no-pager > "${metadata}/systemd-unit-files.txt"
systemctl list-units --all --no-pager > "${metadata}/systemd-units-current.txt"
ip -details -brief address > "${metadata}/network-addresses.txt"
ip route > "${metadata}/network-routes.txt"
lsusb > "${metadata}/usb-devices.txt" 2>&1 || true

{
  while IFS= read -r git_dir; do
    repo="${git_dir%/.git}"
    echo "===== ${repo} ====="
    git -C "${repo}" remote -v 2>/dev/null || true
    git -C "${repo}" rev-parse HEAD 2>/dev/null || true
    git -C "${repo}" status --short --branch 2>/dev/null || true
    echo
  done < <(find /home/iecme -xdev -type d -name .git -prune -print 2>/dev/null | sort)
} > "${metadata}/git-status-all.txt"

{
  while IFS= read -r git_dir; do
    repo="${git_dir%/.git}"
    echo "===== ${repo} ====="
    git -C "${repo}" diff --binary 2>/dev/null || true
    git -C "${repo}" diff --binary --cached 2>/dev/null || true
    echo
  done < <(find /home/iecme -xdev -type d -name .git -prune -print 2>/dev/null | sort)
} > "${metadata}/git-working-tree.patch"

find /home/iecme \
  \( -path /home/iecme/backups -o -path /home/iecme/.cache -o -path /home/iecme/.ros/log \) -prune -o \
  -printf '%y\t%s\t%TY-%Tm-%TdT%TH:%TM:%TS\t%p\n' \
  > "${metadata}/home-file-manifest.tsv"

paths=(
  home/iecme
  etc/systemd/system
  etc/udev/rules.d
  etc/sudoers.d
  etc/netplan
  etc/NetworkManager/conf.d
  etc/modprobe.d
  etc/sysctl.d
  etc/modules-load.d
  etc/ld.so.conf.d
  etc/apt/sources.list
  etc/apt/sources.list.d
  etc/hostname
  etc/hosts
  etc/fstab
  boot/extlinux/extlinux.conf
  opt/MVS
)

existing_paths=()
for path in "${paths[@]}"; do
  [[ -e "/${path}" || -L "/${path}" ]] && existing_paths+=("${path}")
done

sudo tar \
  --numeric-owner \
  --acls \
  --xattrs \
  --sparse \
  -C / \
  --exclude='home/iecme/backups' \
  --exclude='home/iecme/.cache' \
  --exclude='home/iecme/.ros/log' \
  --exclude='home/iecme/*_ws/log' \
  --exclude='home/iecme/slam_overlays/*/log' \
  --exclude='home/iecme/robot_logs' \
  --exclude='home/iecme/.local/share/Trash' \
  --exclude='home/iecme/.mozilla' \
  --exclude='home/iecme/.thunderbird' \
  --exclude='home/iecme/.npm' \
  --exclude='home/iecme/.nv' \
  --exclude='home/iecme/.vscode' \
  --exclude='home/iecme/.pki' \
  --exclude='home/iecme/.gnupg' \
  --exclude='home/iecme/snap' \
  --exclude='home/iecme/Downloads' \
  --exclude='home/iecme/下载' \
  --exclude='home/iecme/.ssh/id_*' \
  --exclude='home/iecme/.ssh/*.pem' \
  --exclude='home/iecme/*.tar.gz' \
  --exclude='home/iecme/*.tar.xz' \
  --exclude='home/iecme/*.deb' \
  --exclude='home/iecme/*.snap' \
  --exclude='home/iecme/*.assert' \
  -I 'zstd -T0 -7' \
  -cpf "${archive}" \
  "${existing_paths[@]}"

sudo chown iecme:iecme "${archive}"
zstd -q -t "${archive}"
sha256sum "${archive}" | sed "s#  ${archive}#  ${base}.tar.zst#" > "${checksum}"
archive_entries="$(tar -I zstd -tf "${archive}" | wc -l)"
archive_bytes="$(stat -c %s "${archive}")"

{
  echo "archive=${archive}"
  echo "checksum=${checksum}"
  echo "bytes=${archive_bytes}"
  echo "entries=${archive_entries}"
  echo "sha256=$(cut -d' ' -f1 "${checksum}")"
} | tee "${backup_dir}/${base}.result.txt"
