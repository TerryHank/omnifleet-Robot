# RMF Web 简体中文部署

2026-10-14，已在本机 Ubuntu-22.04 WSL 原生部署。入口：[http://localhost:3000](http://localhost:3000)。

## 汉化方式

检查了 Open-RMF 官方仓库文档、当前 Humble 源码和新 Dashboard Framework 的依赖，未找到适用于此版本的完整官方中文语言包。Humble 原来只根据浏览器语言加载日期区域设置。

表格、分页、筛选、日期选择器优先使用已安装 MUI 的官方 `zhCN`；日期区域设置使用 date-fns 的 `zhCN`。MUI 旧版本中文日期包遗漏的标题与时钟辅助提示已补齐。RMF 业务文案直接在源码汉化，没有安装非官方汉化包，也没有用 DOM 替换覆盖页面文字。

官方参考：[RMF Web Humble](https://github.com/open-rmf/rmf-web/tree/humble)、[MUI 中文区域设置](https://mui.com/material-ui/guides/localization/)。上游基线提交：`54c9630abdce1eede0d319dc87f3a740ca1faed4`。

## 覆盖范围

导航菜单、系统概览、地图图层、机器人/自动门/电梯/工作站界面、任务创建与收藏、计划日历、任务详情/日志界面的固定文案、用户/角色/权限管理、设置、确认弹窗、提示、辅助标签和常见运行状态。

页面语言与标题设为简体中文；日期显示固定为 `zh-CN`，日历使用中文星期与 24 小时制。原有工作区面板 ID、地图图层键、任务类别、ROS 枚举和请求字段保留原值。车辆、地点、用户自定义名称、品牌和后端原始日志不改写。

只读 API 提示也已中文化；写入与控制请求继续返回 403。未启用实车任务、修改车辆服务或注册可调度车队。

## 验证

- 生产构建及 TypeScript 检查通过，`git diff --check` 通过。
- 静态兼容检查通过：协议值、类型联合、分支常量、保存的面板 ID、地图图层键及电梯方向判断保留。
- 浏览器实际检查了分辨率提示、系统概览、任务创建、日期选择器、任务队列、周历、用户管理、角色页和主题菜单。
- 所有概览表格的排序与分页文字已确认中文。最终浏览器错误检查见 `browser-verification.txt`。
- 页面/API、实际时间、Socket.IO 订阅、轨迹 WebSocket、SQLite 和控制请求拦截的回归检查通过，见 `acceptance-zh-cn.json`。

当前车队和地图仍为空，因此未以实车数据验收任务详情、日志或车辆状态；其固定文案与常见状态显示已在源码处理。后端提供的自由文本日志保留原文。

## 文件与运行

源码：`/home/zhangwnag/workspaces/omnifleet_ws/src/visualization/rmf-web`

中文构建：`/home/zhangwnag/workspaces/omnifleet_ws/build/rmf_web_zh_cn`

实际服务目录：`/home/zhangwnag/workspaces/omnifleet_ws/install/rmf_web_dashboard/zh-CN`

服务与原来相同：

```bash
systemctl --user restart omnifleet-rmf-web.target
journalctl --user -u omnifleet-rmf-web-dashboard.service -f
```

汉化修改见 `rmf-web-zh-CN.patch`；新显示标签模块也包含在补丁中。部署启动脚本与只读 API 包装器快照位于 `native/`。

## 回滚显示为英文

完整英文源码与构建副本：`/home/zhangwnag/workspaces/omnifleet_ws/data/rmf_web/backup_before_zh_cn/`。原先的英文 `packages/dashboard/build` 仍保留。

下面只切换正在服务的前端和提示文案，保留中文源码与数据库，方便重新部署：

```bash
cp /home/zhangwnag/workspaces/omnifleet_ws/data/rmf_web/backup_before_zh_cn/run.bash \
  /home/zhangwnag/workspaces/omnifleet_ws/src/visualization/omnifleet_rmf_web/run.bash
cp /home/zhangwnag/workspaces/omnifleet_ws/data/rmf_web/backup_before_zh_cn/read_only_api.py \
  /home/zhangwnag/workspaces/omnifleet_ws/src/visualization/omnifleet_rmf_web/read_only_api.py
systemctl --user restart omnifleet-rmf-web-dashboard.service omnifleet-rmf-web-api.service
```

重新构建中文前端时，设置 `BUILD_PATH=/home/zhangwnag/workspaces/omnifleet_ws/build/rmf_web_zh_cn`，并将构建内容复制到实际服务目录。构建时不会清空正在服务的目录。
