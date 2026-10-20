import fs from "node:fs";
import path from "node:path";

const translations = new Map(Object.entries({
  "No topic selected": "未选择话题",
  "Waiting for next message…": "正在等待下一条消息……",
  "No difference found": "未发现差异",
  "Waiting for data…": "正在等待数据……",
  "Waiting for first GPS point...": "正在等待第一个 GPS 点……",
  "No diagnostic node selected": "未选择诊断节点",
  "Connect to a ROS source to view parameters": "连接 ROS 数据源以查看参数",
  "Connect to a data source that supports publishing": "请连接支持发布功能的数据源",
  "Select a publish topic in the panel settings": "请在面板设置中选择发布话题",
  "General": "通用",
  "Settings": "设置",
  "Misc": "其他",
  "Topic": "话题",
  "Topics": "话题",
  "Field": "字段",
  "Value": "值",
  "Title": "标题",
  "Tooltip": "工具提示",
  "Color": "颜色",
  "Label": "标签",
  "Type": "类型",
  "Parent": "父节点",
  "Child": "子节点",
  "Axis": "轴",
  "Position": "位置",
  "Rotation": "旋转",
  "Calibration": "标定",
  "Source": "来源",
  "Parameter": "参数",
  "File path": "文件路径",
  "File path (Desktop only)": "文件路径（仅桌面端）",
  "Frame prefix": "坐标系前缀",
  "Duplicate": "复制",
  "Delete": "删除",
  "Display mode": "显示模式",
  "Auto": "自动",
  "Visual": "视觉模型",
  "Collision": "碰撞模型",
  "Manual angle": "手动角度",
  "JointState angle": "JointState 角度",
  "Manual position": "手动位置",
  "JointState position": "JointState 位置",
  "Damping": "阻尼",
  "Friction": "摩擦",
  "Limit": "限制",
  "Limit effort": "力矩限制",
  "Limit velocity": "速度限制",
  "Mimic joint": "模仿关节",
  "Mimic multiplier": "模仿系数",
  "Mimic offset": "模仿偏移",
  "Soft limit": "软限制",
  "Joints": "关节",
  "Message path": "消息路径",
  "Message schema": "消息模式",
  "Editing mode": "编辑模式",
  "Button": "按钮",
  "Service name": "服务名称",
  "Layout": "布局",
  "Vertical": "垂直",
  "Horizontal": "水平",
  "Min": "最小值",
  "Max": "最大值",
  "Color mode": "颜色模式",
  "Color map": "色板",
  "Gradient": "渐变",
  "Red to green": "红到绿",
  "Rainbow": "彩虹",
  "Reverse": "反转",
  "Enabled": "已启用",
  "Coloring": "着色",
  "Automatic": "自动",
  "Custom": "自定义",
  "Off": "关闭",
  "Tile layer": "地图图层",
  "Map": "地图",
  "Satellite": "卫星图",
  "Custom map tile URL": "自定义地图瓦片 URL",
  "Max tile level": "最大瓦片层级",
  "Follow topic": "跟随话题",
  "Delete rule": "删除规则",
  "Move up": "上移",
  "Move down": "下移",
  "Add rule above": "在上方添加规则",
  "Add rule below": "在下方添加规则",
  "Comparison": "比较条件",
  "Equal to": "等于",
  "Less than": "小于",
  "Less than or equal to": "小于或等于",
  "Greater than": "大于",
  "Greater than or equal to": "大于或等于",
  "Compare with": "比较值",
  "Delete series": "删除数据系列",
  "Add series": "添加数据系列",
  "Series": "数据系列",
  "Timestamp": "时间戳",
  "Receive Time": "接收时间",
  "Header Stamp": "头时间戳",
  "Sync with other plots": "与其他图表同步",
  "Show points": "显示点",
  "Publish rate": "发布频率",
  "Up Button": "上按钮",
  "Down Button": "下按钮",
  "Left Button": "左按钮",
  "Right Button": "右按钮",
  "Font size": "字体大小",
  "Filter on this value": "按此值筛选",
  "Plot this value on a line chart": "在折线图中绘制此值",
  "Plot this value on a scatter plot": "在散点图中绘制此值",
  "View state transitions for this value": "查看此值的状态转换",
  "Download plot data as CSV": "将图表数据下载为 CSV",
  "Frame lock": "锁定坐标系",
  "Grid": "网格",
  "Alpha": "透明度",
  "Line Width": "线宽",
  "Show outlines": "显示轮廓",
  "Selection Variable": "选择变量",
  "None": "无",
  "Sync annotations": "同步注释",
  "Flip horizontal": "水平翻转",
  "Flip vertical": "垂直翻转",
  "Download image": "下载图像",
  "Stixel view": "条柱视图",
  "Show full msg": "显示完整消息",
  "Menu": "菜单",
  "Profile": "用户资料",
  "Add panel button": "添加面板按钮",
  "User profile menu button": "用户资料菜单按钮",
  "Zoom fit": "缩放至合适大小",
  "Orientation": "方向",
  "Scroll to bottom": "滚动到底部",
  "Search filter": "搜索筛选条件",
  "Toggle diff": "切换差异模式",
  "Diff method": "差异比较方式",
  "Filter": "筛选",
  "Open in Plot panel": "在图表面板中打开",
  "Open in State Transitions panel": "在状态转换面板中打开",
  "Enter message content as JSON": "以 JSON 格式输入消息内容",
  "Enter service request as JSON": "以 JSON 格式输入服务请求",
  "Response": "响应",
  "Toggle visibility": "切换可见性",
  "Submit change": "提交更改",
  "Reset": "重置",
  "Enter tab name": "输入选项卡名称",
  "Remove tab": "删除选项卡",
  "Add tab": "添加选项卡",
  "Download": "下载",
  "Clear": "清除",
  "Show settings": "显示设置",
  "Open in Raw Message panel": "在原始消息面板中打开",
  "Inspect objects": "检查对象",
  "This panel encountered an unexpected error": "此面板遇到意外错误",
  "Reset panel settings to default values": "将面板设置恢复为默认值",
  "Remove this panel from the layout": "从布局中删除此面板",
  "Create event": "创建事件",
  "Seek backward": "向后跳转",
  "Seek forward": "向前跳转",
  "Loop playback": "循环播放",
  "More actions": "更多操作",
  "Rename": "重命名",
  "Exit fullscreen": "退出全屏",
  "Reset to default": "恢复默认值",
  "Automatically install updates": "自动安装更新",
  "Remember my preference": "记住我的选择",
  "Duration": "持续时间",
  "Start": "开始",
  "End": "结束",
  "Date": "日期",
  "Time": "时间",
  "Elapsed": "已用时间",
  "Open new connection": "打开新连接",
  "Get started": "开始使用",
  "WebSocket URL": "WebSocket 地址",
  "Remote file URL": "远程文件地址",
  "JSON Files": "JSON 文件",
}));

const root = path.resolve("packages/studio-base/src");
const files = [];

function visit(directory) {
  for (const entry of fs.readdirSync(directory, { withFileTypes: true })) {
    const fullPath = path.join(directory, entry.name);
    if (entry.isDirectory()) {
      if (fullPath.includes(`${path.sep}i18n${path.sep}en`)) continue;
      visit(fullPath);
    } else if (/\.(ts|tsx)$/.test(entry.name) && !/\.(test|stories)\./.test(entry.name)) {
      files.push(fullPath);
    }
  }
}

visit(root);
let replacements = 0;

for (const file of files) {
  let source = fs.readFileSync(file, "utf8");
  const original = source;
  const replaceValue = (_match, prefix, value, suffix = "") => {
    const translated = translations.get(value);
    if (!translated) return _match;
    replacements++;
    return `${prefix}${translated}${suffix}`;
  };

  source = source.replace(
    /(\b(?:label|title|placeholder|tooltip|help|description|message|noOptionsText)\s*:\s*")([^"]+)(")/g,
    replaceValue,
  );
  source = source.replace(
    /((?:label|title|placeholder|tooltip|aria-label)=")([^"]+)(")/g,
    replaceValue,
  );
  source = source.replace(
    /(<EmptyState(?:\s[^>]*)?>)([^<{]+)(<\/EmptyState>)/g,
    replaceValue,
  );

  if (source !== original) fs.writeFileSync(file, source);
}

console.log(`已替换 ${replacements} 处硬编码界面文案。`);
