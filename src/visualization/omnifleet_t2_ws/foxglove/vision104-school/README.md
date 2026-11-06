# 十二中 · Foxglove 104 视觉案例布局

2026-11-07 从十二中电脑 `10.0.0.90` 读取，来源快捷方式：

`C:\Users\十二中\Desktop\Foxglove－104 视觉案例.lnk`

快捷方式目标为：

`C:\Users\Public\OmniFleet\Vision104\releases\vision104-20261024-203517\runtime\Foxglove-Studio-CN.exe`

参数为 `--demo-control --vision-demo`。文件夹名称是部署版本标识，目录内文件可能已被后续更新；本目录保存的是本次读取到的文件。

## 导入布局

在带有对应定制面板的 Foxglove Studio CN 中导入 **[Foxglove-104-Vision.json](Foxglove-104-Vision.json)**，数据源为 `ws://192.168.3.104:8765`。

布局包含“视觉案例”和“104导航永久参数”页签，初始案例为 `04_09_body_tracking`。所需面板类型为 `local.omnifleet-vision.demo`、`local.omnifleet-vision.kcf`、`local.omnifleet-113-panels.nav2-hot-params-panel`；缺少这些定制面板时，仅导入 JSON 无法还原全部功能。

本次读取时专用客户端的本地布局接口未运行。此导入文件由远端原始 `vision-entry.cjs` 的 `buildLayout(base, cases, undefined)` 生成，表示没有用户历史状态覆盖时的快捷方式启动布局，**不是实时窗口或用户最后一次保存状态的导出**。原快捷方式启动时会保留上次选中的案例、分案例参数及部分导航配置。

## 文件内容

- `Foxglove-104-Vision.json`：按快捷方式启动逻辑生成的可导入布局。
- `desktop/vision-layout.json`：远端 `resources/app.asar` 内的原始布局模板。
- `desktop/vision-cases.json`：同一包内的 25 个案例配置。
- `desktop/vision-entry.cjs`：同一包内的布局启动逻辑。
- `app-web/vision-demo-panel.js`：远端实际使用的视觉与交互跟随面板。
- `app-web/vision-cases.js`：远端实际使用的浏览器案例配置。
- `app-web/omnifleet113-panels.js`：远端实际使用的导航参数面板。
- `SHA256SUMS`：上述文件及本说明的 SHA-256 校验值。

`desktop/` 的三个文件从 `app.asar` 提取，`app-web/` 的三个文件从同名资源目录读取，均原样保留。桌面和浏览器案例配置中的部分字段存在差异，本备份保留各自原件，未合并或修改。

`app-web/` 脚本通过该定制客户端的面板注册接口加载，并非可直接安装的 `.foxe` 扩展包。本目录不包含完整客户端、机器人后端、安装包或运行数据。

## 已验证范围

已核对远端原件哈希、JSON 解析、25 个案例 ID 一致性、生成布局的面板引用完整性，以及 JavaScript 语法。上传后逐文件核对 GitHub blob 哈希。未启动案例、发送车辆指令或执行实车功能测试。
