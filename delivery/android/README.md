# 视觉跟随 App v28

`robot-follow-v28-unified.apk` 是本次部署链路配套的签名 APK；本轮手掌/NanoTrack 改动在机器人端，无需重新安装 App。

`source/assets/www/` 从该 APK 原样提取，保留与 APK 一致的页面源码与资源；APK 自带原生 WebView 外壳。这里不把反编译结果冒充完整 Java 工程。

机器人连接继续使用接收机地址 `ws://192.168.144.108:8765/`。网页端按各机器人现有部署配置连接。

安装：`adb install -r robot-follow-v28-unified.apk`。重签名需要自行提供原签名密钥；备份不包含密钥、密码或会话历史中的签名信息。
