# Foxglove Studio 中文桌面版

本项目基于 [AD-EYE/foxglove-opensource](https://github.com/AD-EYE/foxglove-opensource) 开发，面向 Ubuntu 22.04 ARM64 / NVIDIA Jetson Orin 的 ROS 2 机器人可视化场景。

## 主要改动

- 补齐 374 个中文资源键，并翻译常用面板、设置、提示和状态中的硬编码文案。
- 默认界面语言及回退语言均设为简体中文。
- 新增 Electron ARM64 桌面壳与 Debian 打包流程，结构参考 [Lichtblick](https://github.com/Lichtblick-Suite/lichtblick)。
- 安装目录固定为纯 ASCII 路径 `/opt/Foxglove-Studio-CN`。
- 用户配置目录固定为 `~/.config/foxglove-studio-cn`，避免中文运行路径兼容问题。
- 默认连接 `ws://localhost:8765`。
- 兼容 ROS 2 Humble `foxglove_bridge` 3.x 使用的 `foxglove.sdk.v1` 子协议。

## 安装

从本仓库 Releases 下载 ARM64 `.deb`，然后执行：

```bash
sudo apt install ./foxglove-studio-cn_1.86.0-cn.3_arm64.deb
foxglove-studio-cn
```

## 从源码构建

构建机需要 ARM64 Linux、Node.js/Corepack、Yarn，以及 Electron Builder 所需的 Debian 打包依赖。

```bash
git clone https://github.com/TerryHank/foxglove-studio-cn.git
cd foxglove-studio-cn
chmod +x build-desktop-cn.sh desktop-cn/build/linux/deb/postinst
./build-desktop-cn.sh
```

生成的软件包位于：

```text
desktop-cn/dist/foxglove-studio-cn_1.86.0-cn.3_arm64.deb
```

## 汉化审计

```bash
node scripts/audit-zh-translations.mjs
```

当前结果：英文资源键 374、中文资源键 374，没有缺失或 `undefined` 回退项。

## 许可证与上游

本仓库以完整源码快照发布，并保留原项目的 MPL-2.0 许可证、NOTICE 和上游来源说明。Foxglove、ROS、MCAP、WebSocket 等品牌名和协议名保持原文。
