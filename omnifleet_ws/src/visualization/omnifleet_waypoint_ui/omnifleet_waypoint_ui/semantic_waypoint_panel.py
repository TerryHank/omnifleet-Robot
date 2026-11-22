#!/usr/bin/env python3
import json
import tkinter as tk
from tkinter import messagebox, ttk

import rclpy
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, QoSProfile, ReliabilityPolicy
from std_msgs.msg import Empty, String


class SemanticWaypointPanelNode(Node):
    def __init__(self) -> None:
        super().__init__("omnifleet_t2_waypoint_panel")
        self.latest_status = "正在连接语义航点后台……"
        self.latest_catalog = None
        self.catalog_changed = False
        self.status_changed = False

        self.next_name_pub = self.create_publisher(
            String, "/omnifleet_t2/waypoints/next_name", 10
        )
        self.rename_pub = self.create_publisher(
            String, "/omnifleet_t2/waypoints/rename", 10
        )
        self.start_pub = self.create_publisher(Empty, "/omnifleet_t2/waypoints/start", 10)
        self.stop_pub = self.create_publisher(Empty, "/omnifleet_t2/waypoints/stop", 10)
        self.undo_pub = self.create_publisher(Empty, "/omnifleet_t2/waypoints/undo", 10)
        self.clear_pub = self.create_publisher(Empty, "/omnifleet_t2/waypoints/clear", 10)

        latched = QoSProfile(depth=1)
        latched.reliability = ReliabilityPolicy.RELIABLE
        latched.durability = DurabilityPolicy.TRANSIENT_LOCAL
        self.create_subscription(
            String, "/omnifleet_t2/waypoints/status", self.on_status, latched
        )
        self.create_subscription(
            String, "/omnifleet_t2/waypoints/catalog", self.on_catalog, latched
        )

    def on_status(self, message: String) -> None:
        self.latest_status = message.data
        self.status_changed = True

    def on_catalog(self, message: String) -> None:
        try:
            self.latest_catalog = json.loads(message.data)
            self.catalog_changed = True
        except json.JSONDecodeError:
            self.latest_status = "语义航点目录格式错误"
            self.status_changed = True

    def publish_name(self, name: str) -> None:
        message = String()
        message.data = name
        self.next_name_pub.publish(message)

    def publish_rename(self, index: int, name: str) -> None:
        message = String()
        message.data = json.dumps(
            {"index": index, "name": name}, ensure_ascii=False
        )
        self.rename_pub.publish(message)


class SemanticWaypointPanel:
    def __init__(self, root: tk.Tk, node: SemanticWaypointPanelNode) -> None:
        self.root = root
        self.node = node
        self.font = ("Noto Sans CJK SC", 11)
        self.bold_font = ("Noto Sans CJK SC", 11, "bold")
        self.root.title("OmniFleet T2 中文语义航点")
        self.root.geometry("400x820+1310+180")
        self.root.minsize(360, 620)
        self.root.attributes("-topmost", True)
        self.root.configure(bg="#151b23")

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background="#151b23")
        style.configure("TLabel", background="#151b23", foreground="#f1f4f8", font=self.font)
        style.configure("Title.TLabel", font=("Noto Sans CJK SC", 16, "bold"))
        style.configure("Hint.TLabel", foreground="#aeb8c5")
        style.configure("Ready.TLabel", foreground="#45d483", font=self.bold_font)
        style.configure("Waiting.TLabel", foreground="#ffcc66", font=self.bold_font)
        style.configure("TEntry", fieldbackground="#f8f9fb", foreground="#111111", font=self.font)

        outer = ttk.Frame(root, padding=14)
        outer.pack(fill="both", expand=True)
        ttk.Label(outer, text="单实车语义多点导航", style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            outer,
            text="1 输入名称　2 在左侧地图放点　3 一键开始路线",
            style="Hint.TLabel",
        ).pack(anchor="w", pady=(2, 8))

        self.readiness = ttk.Label(outer, text="等待定位和 Nav2 就绪", style="Waiting.TLabel")
        self.readiness.pack(anchor="w")
        self.status = tk.Label(
            outer,
            text="正在连接语义航点后台……",
            anchor="w",
            justify="left",
            wraplength=360,
            padx=9,
            pady=8,
            bg="#202a36",
            fg="#f1f4f8",
            font=self.font,
        )
        self.status.pack(fill="x", pady=(7, 10))

        ttk.Label(outer, text="下一个点名称（支持中文，留空自动编号）").pack(anchor="w")
        name_row = ttk.Frame(outer)
        name_row.pack(fill="x", pady=(5, 3))
        self.next_name = ttk.Entry(name_row)
        self.next_name.pack(side="left", fill="x", expand=True)
        self.next_name.bind("<Return>", lambda _event: self.apply_next_name())
        tk.Button(
            name_row,
            text="应用",
            command=self.apply_next_name,
            bg="#3478f6",
            fg="white",
            activebackground="#2567df",
            relief="flat",
            padx=14,
            pady=5,
            font=self.bold_font,
        ).pack(side="left", padx=(7, 0))
        self.pending = ttk.Label(outer, text="下一点：航点1（自动编号）", style="Hint.TLabel")
        self.pending.pack(anchor="w")

        actions = ttk.Frame(outer)
        actions.pack(fill="x", pady=10)
        self.start_button = self.action_button(
            actions, "开始整条路线", lambda: self.node.start_pub.publish(Empty()), "#3478f6"
        )
        self.start_button.grid(row=0, column=0, padx=(0, 4), pady=4, sticky="ew")
        self.action_button(
            actions, "停止导航", lambda: self.node.stop_pub.publish(Empty()), "#d84a4a"
        ).grid(row=0, column=1, padx=(4, 0), pady=4, sticky="ew")
        self.undo_button = self.action_button(
            actions, "撤销上一点", lambda: self.node.undo_pub.publish(Empty()), "#566171"
        )
        self.undo_button.grid(row=1, column=0, padx=(0, 4), pady=4, sticky="ew")
        self.clear_button = self.action_button(
            actions, "清空全部点", self.clear_route, "#566171"
        )
        self.clear_button.grid(row=1, column=1, padx=(4, 0), pady=4, sticky="ew")
        actions.columnconfigure((0, 1), weight=1)

        self.count = ttk.Label(outer, text="已选 0 个语义点", font=self.bold_font)
        self.count.pack(anchor="w", pady=(2, 4))
        list_outer = ttk.Frame(outer)
        list_outer.pack(fill="both", expand=True)
        self.canvas = tk.Canvas(list_outer, bg="#151b23", highlightthickness=0)
        scrollbar = ttk.Scrollbar(list_outer, orient="vertical", command=self.canvas.yview)
        self.list_frame = ttk.Frame(self.canvas)
        self.list_window = self.canvas.create_window((0, 0), window=self.list_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.list_frame.bind(
            "<Configure>", lambda _event: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas.bind(
            "<Configure>", lambda event: self.canvas.itemconfigure(self.list_window, width=event.width)
        )
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.root.after(30, self.spin_ros)

    def action_button(self, parent, text, command, color):
        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=color,
            fg="white",
            activebackground=color,
            disabledforeground="#9aa2ad",
            relief="flat",
            pady=8,
            font=self.bold_font,
        )

    def apply_next_name(self) -> None:
        self.node.publish_name(self.next_name.get())
        self.next_name.delete(0, "end")

    def clear_route(self) -> None:
        if messagebox.askyesno("确认", "确定清空全部语义点吗？", parent=self.root):
            self.node.clear_pub.publish(Empty())

    def rename(self, index: int, entry: ttk.Entry) -> None:
        self.node.publish_rename(index, entry.get())

    def render_catalog(self, catalog: dict) -> None:
        waypoints = catalog.get("waypoints", [])
        pending_name = catalog.get("pending_name", "")
        active = bool(catalog.get("navigation_active", False))
        ready = bool(catalog.get("nav2_ready", False))
        self.readiness.configure(
            text="导航执行中" if active else "系统已就绪" if ready else "等待定位和 Nav2 就绪",
            style="Ready.TLabel" if ready else "Waiting.TLabel",
        )
        self.pending.configure(
            text=(
                f"下一点：{pending_name}"
                if pending_name
                else f"下一点：航点{len(waypoints) + 1}（自动编号）"
            )
        )
        self.count.configure(text=f"已选 {len(waypoints)} 个语义点")
        self.start_button.configure(state="normal" if ready and waypoints and not active else "disabled")
        self.undo_button.configure(state="normal" if waypoints and not active else "disabled")
        self.clear_button.configure(state="normal" if waypoints and not active else "disabled")

        for child in self.list_frame.winfo_children():
            child.destroy()
        for waypoint in waypoints:
            card = tk.Frame(self.list_frame, bg="#202a36", padx=8, pady=7)
            card.pack(fill="x", pady=3)
            tk.Label(
                card,
                text=f"{waypoint['index']}. {waypoint['name']}",
                bg="#202a36",
                fg="#ffd60a",
                anchor="w",
                font=self.bold_font,
            ).pack(fill="x")
            tk.Label(
                card,
                text=f"x {waypoint['x']:.2f}　y {waypoint['y']:.2f}　{waypoint['yaw_deg']:.0f}°",
                bg="#202a36",
                fg="#aeb8c5",
                anchor="w",
                font=("Noto Sans CJK SC", 9),
            ).pack(fill="x")
            rename_row = tk.Frame(card, bg="#202a36")
            rename_row.pack(fill="x", pady=(4, 0))
            entry = ttk.Entry(rename_row)
            entry.insert(0, waypoint["name"])
            entry.pack(side="left", fill="x", expand=True)
            tk.Button(
                rename_row,
                text="重命名",
                command=lambda i=waypoint["index"], e=entry: self.rename(i, e),
                bg="#566171",
                fg="white",
                relief="flat",
                font=("Noto Sans CJK SC", 9),
            ).pack(side="left", padx=(6, 0))

    def spin_ros(self) -> None:
        if not rclpy.ok():
            return
        rclpy.spin_once(self.node, timeout_sec=0.0)
        if self.node.status_changed:
            self.status.configure(text=self.node.latest_status)
            self.node.status_changed = False
        if self.node.catalog_changed and self.node.latest_catalog is not None:
            self.render_catalog(self.node.latest_catalog)
            self.node.catalog_changed = False
        self.root.after(30, self.spin_ros)

    def close(self) -> None:
        self.node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
        self.root.destroy()


def main(args=None) -> None:
    rclpy.init(args=args)
    node = SemanticWaypointPanelNode()
    root = tk.Tk()
    SemanticWaypointPanel(root, node)
    root.mainloop()


if __name__ == "__main__":
    main()
