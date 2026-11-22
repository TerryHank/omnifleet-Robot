"""Back up the A2 map and request a fresh stationary map."""
import argparse
import json
from pathlib import Path
import subprocess
import time

import numpy as np
import rclpy
from action_msgs.msg import GoalStatus, GoalStatusArray
from geometry_msgs.msg import Twist
from mola_msgs.srv import MapSave
from nav_msgs.msg import OccupancyGrid
from nav2_msgs.srv import ClearEntireCostmap
from rclpy.qos import DurabilityPolicy, QoSProfile, qos_profile_sensor_data
from rclpy.time import Time
from std_srvs.srv import Trigger
from tf2_ros import Buffer, TransformListener


def note(phase, message, **info):
    print("SLAM_STATE " + json.dumps(dict(phase=phase,message=message,**info),ensure_ascii=False),flush=True)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--grid-only", action="store_true")
    args=parser.parse_args()
    rclpy.init()
    node=rclpy.create_node("omnifleet_124_stationary_map_rebuild")
    buffer=Buffer(); listener=TransformListener(buffer,node)
    latest={}; active={}; motion=[]
    def remember_map(msg):
        latest["map"]=msg
    def remember_motor(msg):
        motion.append((msg.linear.x,msg.angular.z))
    def update_goal(msg,key):
        active[key]=any(x.status in (GoalStatus.STATUS_ACCEPTED,GoalStatus.STATUS_EXECUTING,
                                       GoalStatus.STATUS_CANCELING) for x in msg.status_list)
    node.create_subscription(OccupancyGrid,"/map",remember_map,QoSProfile(
        depth=1,durability=DurabilityPolicy.TRANSIENT_LOCAL))
    node.create_subscription(Twist,"/omnifleet_a2/chassis/motor_command_sent",remember_motor,qos_profile_sensor_data)
    for name in ("navigate_to_pose","navigate_through_poses","follow_path"):
        node.create_subscription(GoalStatusArray,f"/{name}/_action/status",
            lambda m,k=name:update_goal(m,k),QoSProfile(depth=1,durability=DurabilityPolicy.TRANSIENT_LOCAL))

    def now_ns(): return node.get_clock().now().nanoseconds
    def spin(seconds):
        end=time.monotonic()+seconds
        while time.monotonic()<end:
            rclpy.spin_once(node,timeout_sec=.15)
    def call(name,service,req,timeout):
        client=node.create_client(service,name)
        if not client.wait_for_service(timeout_sec=4):
            raise RuntimeError(f"车端服务未就绪：{name}")
        future=client.call_async(req)
        rclpy.spin_until_future_complete(node,future,timeout_sec=timeout)
        if not future.done():
            raise TimeoutError(f"等待 {name} 返回超时")
        return future.result()
    try:
        note("saving","正在保存当前地图")
        spin(1.6)
        if any(active.values()) or any(max(abs(v),abs(w))>.01 for v,w in motion):
            raise RuntimeError("请先停止导航和底盘运动，再重启 SLAM")
        if "map" not in latest:
            spin(2.)
        old=latest.get("map")
        if old is None or not old.data:
            raise RuntimeError("没有收到现有二维地图")
        folder=Path.home()/"omnifleet_a2_backups"/"slam-before-rebuild"/time.strftime("%Y%m%d-%H%M%S")
        folder.mkdir(parents=True,exist_ok=False)
        origin=old.info.origin.position
        np.save(folder/"navigation-grid.npy",np.asarray(old.data,dtype=np.int8).reshape(old.info.height,old.info.width),allow_pickle=False)
        (folder/"navigation-grid.json").write_text(json.dumps(dict(frame=old.header.frame_id,
            resolution=old.info.resolution,width=old.info.width,height=old.info.height,
            origin=[origin.x,origin.y,origin.z]),indent=2))
        if not args.grid_only:
            base=folder/"current-slam"
            result=call("/map_save",MapSave,MapSave.Request(map_path=str(base)),22)
            if not result or not result.success or not base.with_suffix(".mm").is_file():
                raise RuntimeError("当前 SLAM 地图保存失败，保留正在运行的 SLAM")
        note("restarting","正在重建导航栅格" if args.grid_only else "地图已备份，正在重启 SLAM",backup=str(folder))
        stamp=now_ns()
        if args.grid_only:
            result=call("/mola_realtime_nav_grid/clear",Trigger,Trigger.Request(),4)
            if not result or not result.success:
                raise RuntimeError("清理旧导航栅格未确认")
            stamp=now_ns()
        else:
            marker=Path.home()/"omnifleet_a2_backups"/"robot124-mola105-migration-20261121"/"restore-next-start"
            if marker.exists():
                marker.replace(folder/"previous-restore-next-start")
            subprocess.run(["sudo","-n","systemctl","restart","omnifleet-a2-mola.service"],check=True,timeout=65)
        note("waiting","等待本轮地图和定位数据",backup=str(folder))
        end=time.monotonic()+38
        while time.monotonic()<end:
            rclpy.spin_once(node,timeout_sec=.18)
            msg=latest.get("map")
            if msg is None:continue
            when=Time.from_msg(msg.header.stamp).nanoseconds
            if when<=stamp or 0 not in msg.data or 100 not in msg.data:continue
            if not buffer.can_transform("map","base_link",Time()):continue
            tf=buffer.lookup_transform("map","base_link",Time())
            tf_when=Time.from_msg(tf.header.stamp).nanoseconds
            if tf_when<=stamp:continue
            message = "导航栅格已用实时点云重建" if args.grid_only else "SLAM 已重新建图，地图和定位已恢复"
            if not args.grid_only:
                for scope in ("global", "local"):
                    try:
                        call(f"/{scope}_costmap/clear_entirely_{scope}_costmap",
                             ClearEntireCostmap, ClearEntireCostmap.Request(), 3)
                    except (RuntimeError, TimeoutError) as error:
                        node.get_logger().warning(str(error))
                        message += f"；{scope} 代价地图刷新未确认"
            note("done",message,
                 backup=str(folder),known=sum(value>=0 for value in msg.data),
                 occupied=msg.data.count(100),map_stamp=when,localization_stamp=tf_when)
            return
        raise TimeoutError("等待新地图或定位超时，旧地图备份已保留")
    except (OSError,ValueError,RuntimeError,TimeoutError,subprocess.SubprocessError) as error:
        note("failed",str(error))
        raise SystemExit(1)
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__=="__main__":
    main()

