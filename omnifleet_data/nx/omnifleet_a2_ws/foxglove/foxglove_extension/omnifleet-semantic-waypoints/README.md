# OmniFleet 中文语义航点 Foxglove 扩展

面板为每个实车导航点保存中文语义名称。输入框留空时，后台自动使用
`航点1`、`航点2`……；输入中文名称并点击“应用到下一个点”后，下一次在
3D 地图发布的姿态会使用该名称。

构建与打包：

```bash
npm install
npm run build
npm run package
```

生成的 `.foxe` 文件可由 Foxglove Desktop 安装。
