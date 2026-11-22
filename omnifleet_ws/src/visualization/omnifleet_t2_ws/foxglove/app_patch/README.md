# OmniFleet T2 Foxglove 语义导航卡片补丁

Foxglove Studio 中文版 `1.87.0-cn.8` 的桌面壳未启用本地 ExtensionLoader，
因此仅执行 `foxglove-extension install` 不会让自定义面板出现在“添加面板”列表。
生产版将语义导航组件注册为内置 `SemanticWaypointPanel`，并删除旧顶栏浮动窗入口。

目标运行块：

```text
/opt/Foxglove-Studio-CN/resources/app-web/4936.33f3ad98e1e1f7b86b00.js
```

应用顺序：

```bash
node remove_semantic_floating.cjs INPUT step1.js
node embed_semantic_panel.cjs step1.js step2.js
node update_semantic_card_text.cjs step2.js step3.js
node fix_semantic_panel_registration.cjs step3.js FINAL.js
node --check FINAL.js
```

2026-09-02生产结果：

- 内置Panel类型：`SemanticWaypointPanel`；
- 活动实例：`SemanticWaypointPanel!gkn4rm`；
- 默认位置：`Plot!linearVelocity`正下方；
- 旧“打开语义导航”顶栏按钮和浮动窗入口已删除；
- 最终运行块 SHA-256：`3205a49606e13392b22eddfd65ef59953c0783fc686ae249f89e006112dbdcdf`。

回退备份：

```text
/home/iecme/.codex-backups/foxglove/t2-card-20260902_011000/
```
