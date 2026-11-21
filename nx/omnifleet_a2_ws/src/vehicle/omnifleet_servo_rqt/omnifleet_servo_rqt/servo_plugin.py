from time import monotonic
from python_qt_binding.QtCore import QTimer, Qt
from python_qt_binding.QtWidgets import (
    QFormLayout, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QSpinBox, QTextEdit, QVBoxLayout, QWidget, QComboBox, QSlider,
    QListWidget, QListWidgetItem,
)
from rqt_gui_py.plugin import Plugin
import rclpy
from omnifleet_interfaces.srv import ServoCommand


OPS = {
    'ping': 1, 'state': 2, 'position': 3, 'mode': 4, 'speed': 5,
    'torque': 6, 'read_limits': 7, 'set_limits': 8, 'calibrate': 9,
    'set_id': 10,
    'set_baud': 12,
}


class ServoPlugin(Plugin):
    def __init__(self, context):
        super().__init__(context)
        self.setObjectName('FTServoPanel')
        if not rclpy.ok():
            rclpy.init(args=None)
        self._node = rclpy.create_node('omnifleet_servo_rqt')
        self._client = self._node.create_client(ServoCommand, '/t2/servo_command')
        self._future = None
        self._scanning = False
        self._batch = []
        self._drafts = {}
        self._widget = QWidget()
        self._build_ui()
        context.add_widget(self._widget)
        self._timer = QTimer(self._widget)
        self._timer.timeout.connect(self._spin_once)
        self._timer.start(50)

    def _spin_once(self):
        if not rclpy.ok():
            return
        rclpy.spin_once(self._node, timeout_sec=0.0)
        if self._future is not None and (self._future.done() or monotonic() > self._deadline):
            future = self._future
            self._future = None
            try:
                if not future.done():
                    future.cancel()
                    raise TimeoutError('等待服务回复超时，请检查底盘连接')
                result = future.result()
                if self._scanning:
                    self._scan_result(result)
                else:
                    self._log('ID %d %s ' % (self._pending_id, self._pending_action) + ('成功: ' if result.success else '失败: ') + result.message +
                              '  [%d, %d, %d]' % (result.value0, result.value1, result.value2))
                    if result.success and self._pending_action == 'read_limits' and self._id.value() == self._pending_id:
                        self._lower.setValue(result.value0)
                        self._upper.setValue(result.value1)
                    if self._batch:
                        if result.success:
                            self._next_batch()
                        else:
                            self._batch.clear()
                            self._log('批量操作中止，剩余舵机未发送')
            except Exception as error:
                self._log('服务异常: %s' % error)
                self._finish_scan('查找中断')
                self._batch.clear()

    def _build_ui(self):
        root = QVBoxLayout(self._widget)
        form = QFormLayout()
        self._id = QSpinBox(); self._id.setRange(0, 253); self._id.setValue(1)
        self._scan_button = QPushButton('自动查找舵机')
        self._scan_button.clicked.connect(self._toggle_scan)
        id_row = QHBoxLayout(); id_row.addWidget(self._id); id_row.addWidget(self._scan_button)
        form.addRow('舵机 ID', id_row)
        self._scan_status = QLabel('按所选波特率扫描全部 ID 0..253；多个舵机必须使用不同 ID')
        form.addRow(self._scan_status)
        self._servos = QListWidget()
        self._servos.setMaximumHeight(100)
        self._servos.currentItemChanged.connect(lambda item, previous: self._id.setValue(item.data(Qt.UserRole)) if item else None)
        form.addRow('舵机列表（点击切换，勾选批量）', self._servos)
        add_button = QPushButton('添加当前 ID（未验证）')
        add_button.clicked.connect(lambda: self._add_servo(self._id.value(), False))
        form.addRow(add_button)
        self._baud = QComboBox()
        for label, code in [('115200', 0), ('1000000', 1), ('500000', 2), ('250000', 3), ('57600', 4), ('38400', 5)]:
            self._baud.addItem(label, code)
        self._baud.setCurrentIndex(1)
        baud_button = QPushButton('应用波特率')
        baud_button.clicked.connect(lambda: self._action('set_baud'))
        baud_row = QHBoxLayout(); baud_row.addWidget(self._baud); baud_row.addWidget(baud_button)
        form.addRow('USART3 波特率', baud_row)
        self._pos = QSpinBox(); self._pos.setRange(-32768, 32767); self._pos.setValue(2048)
        self._pos_slider = QSlider(Qt.Horizontal)
        self._pos_slider.setRange(0, 4095); self._pos_slider.setValue(self._pos.value())
        self._pos_slider.valueChanged.connect(self._pos.setValue)
        self._pos.valueChanged.connect(self._sync_position_slider)
        position_row = QHBoxLayout(); position_row.addWidget(self._pos_slider); position_row.addWidget(self._pos)
        self._speed = QSpinBox(); self._speed.setRange(0, 3400); self._speed.setValue(500)
        self._acc = QSpinBox(); self._acc.setRange(0, 255); self._acc.setValue(50)
        form.addRow('目标位置', position_row)
        form.addRow(QLabel('拖动仅修改目标值，点击“发送位置”执行；默认滑动范围 0..4095'))
        form.addRow('速度', self._speed); form.addRow('加速度', self._acc)
        root.addLayout(form)

        actions = QGroupBox('状态与动作')
        grid = QGridLayout(actions)
        for col, (label, op) in enumerate([('Ping', 'ping'), ('读取状态', 'state'), ('扭矩开', 'torque_on'), ('扭矩关', 'torque_off'), ('中位校准/清多圈', 'calibrate')]):
            button = QPushButton(label); button.clicked.connect(lambda _=False, name=op: self._action(name)); grid.addWidget(button, col // 3, col % 3)
        pos_button = QPushButton('发送位置'); pos_button.clicked.connect(lambda: self._action('position')); grid.addWidget(pos_button, 2, 0)
        speed_button = QPushButton('发送速度'); speed_button.clicked.connect(lambda: self._action('speed')); grid.addWidget(speed_button, 2, 1)
        root.addWidget(actions)
        batch_row = QHBoxLayout()
        for label, action in [('向勾选舵机发送当前目标位置', 'position'), ('勾选舵机扭矩开', 'torque_on'), ('勾选舵机扭矩关', 'torque_off')]:
            button = QPushButton(label)
            button.clicked.connect(lambda _=False, name=action: self._start_batch(name))
            batch_row.addWidget(button)
        stop_batch = QPushButton('停止后续发送')
        stop_batch.clicked.connect(self._stop_batch)
        batch_row.addWidget(stop_batch)
        root.addLayout(batch_row)
        root.addWidget(QLabel('普通按钮仅操作当前 ID；批量按顺序发送，非同步运动。停止发送不会停止已执行的运动。'))

        limits = QGroupBox('上下限位（0..4095，写入前自动关闭扭矩并锁定 EEPROM）')
        lf = QFormLayout(limits)
        self._lower = QSpinBox(); self._lower.setRange(0, 4095); self._lower.setValue(0)
        self._upper = QSpinBox(); self._upper.setRange(0, 4095); self._upper.setValue(4095)
        lf.addRow('下限位', self._lower); lf.addRow('上限位', self._upper)
        lb = QHBoxLayout(); readb = QPushButton('读取上下限位'); readb.clicked.connect(lambda: self._action('read_limits')); writeb = QPushButton('写入上下限位'); writeb.clicked.connect(lambda: self._action('set_limits')); lb.addWidget(readb); lb.addWidget(writeb); lf.addRow(lb)
        root.addWidget(limits)

        mode = QHBoxLayout(); mode.addWidget(QLabel('模式 0位置 1速度 2PWM 3步进'))
        self._mode = QSpinBox(); self._mode.setRange(0, 3); mode.addWidget(self._mode)
        mb = QPushButton('写入模式'); mb.clicked.connect(lambda: self._action('mode')); mode.addWidget(mb)
        root.addLayout(mode)
        root.addWidget(QLabel('提示：先确认机械结构安全，再开启扭矩或发送位置；上下限位写入会改变舵机 EEPROM。'))
        self._output = QTextEdit(); self._output.setReadOnly(True); root.addWidget(self._output)
        self._active_id = self._id.value()
        self._id.valueChanged.connect(self._switch_servo)

    def _switch_servo(self, servo_id):
        fields = (self._pos, self._speed, self._acc, self._lower, self._upper, self._mode)
        self._drafts[self._active_id] = tuple(field.value() for field in fields)
        for field, value in zip(fields, self._drafts.get(servo_id, (2048, 500, 50, 0, 4095, 0))):
            field.setValue(value)
        self._active_id = servo_id

    def _add_servo(self, servo_id, online=True):
        for index in range(self._servos.count()):
            item = self._servos.item(index)
            if item.data(Qt.UserRole) == servo_id:
                break
        else:
            item = QListWidgetItem()
            item.setData(Qt.UserRole, servo_id)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)
            self._servos.addItem(item)
        item.setText('ID %d — %s' % (servo_id, '本次 Ping 成功' if online else '未验证'))

    def _start_batch(self, action):
        if self._scanning or self._future is not None or self._batch:
            self._log('请等待当前操作完成'); return
        if not self._client.service_is_ready():
            self._log('服务 /t2/servo_command 不可用'); return
        ids = [self._servos.item(i).data(Qt.UserRole) for i in range(self._servos.count())
               if self._servos.item(i).checkState() == Qt.Checked]
        if not ids:
            self._log('请先勾选要控制的舵机'); return
        args = (self._pos.value(), self._speed.value(), self._acc.value()) if action == 'position' else (int(action == 'torque_on'), 0, 0)
        self._batch = [(action if action == 'position' else 'torque', servo_id, args) for servo_id in ids]
        self._log('批量发送至 ID %s，参数 %s' % (ids, args))
        self._next_batch()

    def _next_batch(self):
        action, servo_id, args = self._batch.pop(0)
        self._send(action, servo_id, *args)

    def _stop_batch(self):
        self._batch.clear()
        self._log('已停止后续发送；已发送命令仍会执行')

    def _log(self, text):
        self._output.append(text)

    def _sync_position_slider(self, value):
        # Keep signed/multi-turn numeric input available outside the single-turn range.
        self._pos_slider.blockSignals(True)
        self._pos_slider.setRange(min(0, value), max(4095, value))
        self._pos_slider.setValue(value)
        self._pos_slider.blockSignals(False)

    def _send(self, action, servo_id, arg0=0, arg1=0, arg2=0):
        request = ServoCommand.Request()
        request.operation = OPS[action]; request.id = servo_id
        request.arg0 = arg0 & 0xffff; request.arg1 = arg1 & 0xffff; request.arg2 = arg2 & 0xffff
        self._pending_action = action
        self._pending_id = servo_id
        self._deadline = monotonic() + 5.0
        self._future = self._client.call_async(request)

    def _toggle_scan(self):
        if self._scanning:
            self._finish_scan('已停止查找')
            return
        if self._future is not None:
            self._log('请等待当前命令完成'); return
        if not self._client.service_is_ready():
            self._log('服务 /t2/servo_command 不可用'); return
        self._scanning = True
        self._scan_id = 0
        self._found_ids = []
        for i in range(self._servos.count()):
            self._add_servo(self._servos.item(i).data(Qt.UserRole), False)
        self._scan_button.setText('停止查找')
        self._id.setEnabled(False); self._baud.setEnabled(False); self._servos.setEnabled(False)
        self._scan_status.setText('正在应用 USART3 波特率 ' + self._baud.currentText())
        self._send('set_baud', self._id.value(), int(self._baud.currentData()))

    def _finish_scan(self, status):
        if not self._scanning:
            return
        self._scanning = False
        self._scan_button.setText('自动查找舵机')
        self._id.setEnabled(True); self._baud.setEnabled(True); self._servos.setEnabled(True)
        if self._found_ids:
            self._id.setValue(self._found_ids[0])
        status += '；发现 ID：' + (', '.join(map(str, self._found_ids)) or '无')
        self._scan_status.setText(status)
        self._log(status)

    def _scan_result(self, result):
        if self._pending_action == 'set_baud':
            if not result.success:
                self._finish_scan('波特率设置失败：' + result.message); return
        elif result.success:
            self._found_ids.append(self._scan_id)
            self._add_servo(self._scan_id)
            self._log('发现舵机 ID %d' % self._scan_id)
        if self._pending_action == 'ping':
            self._scan_id += 1
        if self._scan_id > 253:
            self._finish_scan('扫描完成'); return
        self._scan_status.setText('正在查找 ID %d / 253' % self._scan_id)
        self._send('ping', self._scan_id)

    def _action(self, action):
        if self._scanning or self._future is not None:
            self._log('请先停止查找并等待当前命令完成'); return
        servo_id = self._id.value()
        op = OPS.get(action)
        arg0 = arg1 = arg2 = 0
        if action == 'torque_on': op, arg0 = OPS['torque'], 1
        elif action == 'torque_off': op, arg0 = OPS['torque'], 0
        elif action == 'position': op, arg0, arg1, arg2 = OPS['position'], self._pos.value(), self._speed.value(), self._acc.value()
        elif action == 'speed': op, arg0, arg1 = OPS['speed'], self._pos.value(), self._acc.value()
        elif action == 'mode': op, arg0 = OPS['mode'], self._mode.value()
        elif action == 'set_baud': op, arg0 = OPS['set_baud'], int(self._baud.currentData())
        elif action == 'set_limits':
            if self._lower.value() >= self._upper.value(): self._log('拒绝写入：下限位必须小于上限位'); return
            op, arg0, arg1 = OPS['set_limits'], self._lower.value(), self._upper.value()
        elif action == 'read_limits': op = OPS['read_limits']
        if op is None: return
        if not self._client.wait_for_service(timeout_sec=0.2): self._log('服务 /t2/servo_command 不可用'); return
        self._send('torque' if action in ('torque_on', 'torque_off') else action, servo_id, arg0, arg1, arg2)

    def shutdown_plugin(self):
        self._timer.stop(); self._node.destroy_node()

    def save_settings(self, plugin_settings, instance_settings):
        instance_settings.set_value('servo_id', self._id.value())
        instance_settings.set_value('baud_index', self._baud.currentIndex())

    def restore_settings(self, plugin_settings, instance_settings):
        self._id.setValue(int(instance_settings.value('servo_id', 1)))
        self._baud.setCurrentIndex(int(instance_settings.value('baud_index', 1)))
