"""
基础设置面板 - 简化版配置界面
"""
import os
from typing import Optional

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QGroupBox, QFormLayout, QLineEdit,
    QPushButton, QHBoxLayout, QLabel, QFileDialog, QComboBox
)
from PyQt6.QtCore import pyqtSignal

from config.epconfig import EPConfig, ScreenType
from config.constants import RESOLUTION_SPECS


class BasicConfigPanel(QWidget):
    """基础设置面板"""

    config_changed = pyqtSignal()  # 配置变更信号
    video_file_selected = pyqtSignal(str)  # 视频文件选择信号
    validate_requested = pyqtSignal()  # 验证配置请求信号
    export_requested = pyqtSignal()  # 导出素材请求信号

    def __init__(self, parent=None):
        super().__init__(parent)

        self._config: Optional[EPConfig] = None
        self._base_dir: str = ""

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)

        # 基本信息
        group_basic = QGroupBox("基本信息")
        basic_layout = QFormLayout(group_basic)

        self.edit_name = QLineEdit()
        self.edit_name.setPlaceholderText("素材名称")
        basic_layout.addRow("名称:", self.edit_name)

        self.combo_screen = QComboBox()
        for screen in RESOLUTION_SPECS:
            desc = RESOLUTION_SPECS[screen].get("description", screen)
            self.combo_screen.addItem(desc, screen)
        basic_layout.addRow("分辨率:", self.combo_screen)

        layout.addWidget(group_basic)

        # 视频设置
        group_video = QGroupBox("视频设置")
        video_layout = QVBoxLayout(group_video)

        # 循环视频
        loop_layout = QFormLayout()
        self.edit_loop_file = QLineEdit()
        self.edit_loop_file.setPlaceholderText("选择循环视频")
        loop_layout.addRow("循环视频:", self.edit_loop_file)

        btn_browse_loop = QPushButton("浏览...")
        btn_browse_loop.clicked.connect(lambda: self._browse_file("视频", ["视频文件 (*.mp4 *.avi *.mov"]))
        loop_layout.addRow("", btn_browse_loop)

        video_layout.addLayout(loop_layout)
        layout.addWidget(group_video)

        # 一键模板
        group_template = QGroupBox("一键模板")
        template_layout = QVBoxLayout(group_template)

        template_desc = QLabel("选择一个模板，快速创建素材")
        template_layout.addWidget(template_desc)

        self.combo_template = QComboBox()
        self.combo_template.addItems(["默认模板", "明日方舟模板", "自定义模板"])
        template_layout.addWidget(self.combo_template)

        layout.addWidget(group_template)

        # 操作按钮
        group_actions = QGroupBox("操作")
        actions_layout = QVBoxLayout(group_actions)

        self.btn_validate = QPushButton("验证配置")
        actions_layout.addWidget(self.btn_validate)

        self.btn_export = QPushButton("导出素材")
        actions_layout.addWidget(self.btn_export)

        layout.addWidget(group_actions)

        layout.addStretch()

    def _connect_signals(self):
        """连接信号"""
        self.edit_name.textChanged.connect(self._on_config_changed)
        self.combo_screen.currentIndexChanged.connect(self._on_config_changed)
        self.edit_loop_file.textChanged.connect(self._on_config_changed)
        self.combo_template.currentIndexChanged.connect(self._on_template_changed)

        self.btn_validate.clicked.connect(self.validate_requested.emit)
        self.btn_export.clicked.connect(self.export_requested.emit)

    def set_config(self, config: EPConfig, base_dir: str = ""):
        """设置配置"""
        self._config = config
        self._base_dir = base_dir

        if config:
            self.edit_name.setText(config.name)
            
            # 分辨率
            index = self.combo_screen.findData(config.screen.value)
            if index >= 0:
                self.combo_screen.setCurrentIndex(index)

            # 循环视频
            self.edit_loop_file.setText(config.loop.file)

    def get_config(self) -> Optional[EPConfig]:
        """获取配置"""
        return self._config

    def update_config_from_ui(self):
        """从UI更新配置"""
        if self._config is None:
            return

        # 基本信息
        self._config.name = self.edit_name.text()

        # 分辨率
        screen_value = self.combo_screen.currentData()
        self._config.screen = ScreenType.from_string(screen_value)

        # 循环视频
        self._config.loop.file = self.edit_loop_file.text()
        self._config.loop.is_image = False

        # 根据模板设置其他参数
        template = self.combo_template.currentText()
        if template == "明日方舟模板":
            # 设置明日方舟模板的默认值
            self._config.overlay.type = "arknights"
            if not self._config.overlay.arknights_options:
                from config.epconfig import ArknightsOverlayOptions
                self._config.overlay.arknights_options = ArknightsOverlayOptions(
                    operator_name="OPERATOR",
                    operator_code="ARKNIGHTS - UNK0",
                    barcode_text="OPERATOR - ARKNIGHTS",
                    aux_text="Operator of Rhodes Island",
                    staff_text="STAFF"
                )
        elif template == "自定义模板":
            # 可以在这里添加自定义模板的逻辑
            pass

    def _on_config_changed(self):
        """配置变更处理"""
        self.update_config_from_ui()
        self.config_changed.emit()

    def _on_template_changed(self):
        """模板变更处理"""
        self._on_config_changed()

    def _browse_file(self, title: str, filters: list):
        """浏览文件"""
        path, _ = QFileDialog.getOpenFileName(
            self, f"选择{title}", self._base_dir,
            ";;".join(filters)
        )
        if path:
            self.edit_loop_file.setText(path)
            self.video_file_selected.emit(path)
