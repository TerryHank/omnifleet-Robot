#!/bin/bash
# 永久保存标定值 — 修改 URDF 中的 rslidar roll
# 用法: ./save_calibration.sh <roll_deg>
# 如: ./save_calibration.sh 1.873

ROLL_DEG=$1
if [ -z "$ROLL_DEG" ]; then
    echo "用法: ./save_calibration.sh <roll_deg>"
    echo "如: ./save_calibration.sh 1.873"
    exit 1
fi

ROLL_RAD=$(python3 -c "import math; print(math.radians($ROLL_DEG))")
URDF="/home/iecme/hardware_drivers_ws/src/rrc_tank_description/urdf/rrc_tank.urdf"
BACKUP="${URDF}.backup_$(date +%Y%m%d_%H%M%S)"

echo "Roll: ${ROLL_DEG}° = ${ROLL_RAD} rad"
echo "备份: $BACKUP"
cp "$URDF" "$BACKUP"

# 修改 rslidar_joint 的 origin
sed -i "s|<origin xyz=\"-0.041 0 0.15\"/>|<origin xyz=\"-0.041 0 0.15\" rpy=\"${ROLL_RAD} 0 0\"/>|" "$URDF"

echo "已修改 rrc_tank.urdf"
echo "roll=${ROLL_DEG}° → rpy=\"${ROLL_RAD} 0 0\""
echo ""
echo "下一步:"
echo "  cd ~/hardware_drivers_ws && colcon build && source install/setup.bash"
echo "  然后重启所有节点"
