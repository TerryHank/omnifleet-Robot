# OmniFleet T2 中文语义航点 Foxglove 扩展

面板作为113默认 Foxglove 页面中的固定卡片，为履带实车的每个导航点保存中文语义名称。输入框留空时，后台自动使用
`航点1`、`航点2`……；输入中文名称并点击“应用到下一个点”后，下一次在
3D 地图通过“添加多点航点”放置的姿态会使用该名称。单点导航继续使用
`/goal_pose`，多点导航使用 `/omnifleet_t2/waypoints/*`，两条链路互不混用。

构建与打包：

```bash
npm install
npm run build
npm run package
```

生成的 `.foxe` 文件可由 Foxglove Desktop 安装。默认布局将该卡片固定在
“履带指令 /cmd_vel 与 STM32反馈 /vel_raw 对照”折线图下方，不再使用浮动窗。
