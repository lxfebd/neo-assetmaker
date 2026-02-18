"""
基础设置面板 - 简化版配置界面
"""
import os
from typing import Optional

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QGroupBox, QFormLayout, QLineEdit,
    QPushButton, QHBoxLayout, QLabel, QFileDialog, QComboBox, QCompleter
)
from PyQt6.QtCore import pyqtSignal, Qt

from config.epconfig import EPConfig, ScreenType
from config.constants import RESOLUTION_SPECS, OPERATOR_CLASS_PRESETS
from config.operator_db import get_operator_db


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
        self._operator_db = get_operator_db()
        self._is_updating_from_db = False  # 防止循环更新

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
        btn_browse_loop.clicked.connect(lambda: self._browse_file("视频", ["视频文件 (*.mp4 *.avi *.mov)" ]))
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

        # 明日方舟干员信息（仅在明日方舟模板时显示）
        self.group_arknights = QGroupBox("明日方舟干员信息")
        arknights_layout = QFormLayout(self.group_arknights)
        
        # 干员名称输入框（带自动完成）
        self.edit_ark_name = QLineEdit()
        self.edit_ark_name.setPlaceholderText("例如：新约能天使")
        self.edit_ark_name.setToolTip("干员名称，显示在UI顶部\n支持模糊搜索，输入部分名称即可")
        
        # 设置自动完成
        completer = QCompleter()
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self.edit_ark_name.setCompleter(completer)
        
        arknights_layout.addRow("干员名称:", self.edit_ark_name)
        
        # 职业下拉框
        self.combo_ark_class = QComboBox()
        self.combo_ark_class.addItem("无", "")
        for class_name, class_value in OPERATOR_CLASS_PRESETS.items():
            self.combo_ark_class.addItem(class_name, class_value)
        self.combo_ark_class.setToolTip("选择干员职业\n输入干员名称后自动匹配")
        arknights_layout.addRow("职业:", self.combo_ark_class)
        
        # 默认隐藏明日方舟干员信息
        self.group_arknights.setVisible(False)
        
        template_layout.addWidget(self.group_arknights)
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
        
        # 明日方舟干员信息信号
        self.edit_ark_name.textChanged.connect(self._on_operator_name_changed)
        self.combo_ark_class.currentIndexChanged.connect(self._on_config_changed)

        self.btn_validate.clicked.connect(self.validate_requested.emit)
        self.btn_export.clicked.connect(self.export_requested.emit)

    def _on_operator_name_changed(self, text: str):
        """干员名称变更处理"""
        if self._is_updating_from_db:
            return
        
        if not text:
            self.combo_ark_class.setCurrentIndex(0)  # 选择"无"
            self._on_config_changed()
            return
        
        # 搜索干员
        results = self._operator_db.search(text, limit=1)
        if results:
            operator_name, similarity = results[0]
            if similarity > 0.5:  # 相似度阈值
                # 获取干员职业
                profession = self._operator_db.get_operator_profession(operator_name)
                if profession:
                    # 自动选择职业
                    index = self.combo_ark_class.findData(profession)
                    if index >= 0:
                        self.combo_ark_class.setCurrentIndex(index)
        
        self._on_config_changed()

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
            
            # 明日方舟干员信息
            if config.overlay.arknights_options:
                self.edit_ark_name.setText(config.overlay.arknights_options.operator_name)
                # 设置职业图标
                class_icon = config.overlay.arknights_options.operator_class_icon or ""
                index = self.combo_ark_class.findData(class_icon)
                if index >= 0:
                    self.combo_ark_class.setCurrentIndex(index)
                else:
                    self.combo_ark_class.setCurrentIndex(0)  # 选择"无"
            
            # 更新自动完成列表
            self._update_completer()

    def _update_completer(self):
        """更新自动完成列表"""
        completer = self.edit_ark_name.completer()
        if completer:
            model = completer.model()
            if model:
                model.setStringList(self._operator_db.get_all_operators())

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
        try:
            if template == "明日方舟模板":
                # 设置明日方舟模板的默认值
                from config.epconfig import OverlayType
                self._config.overlay.type = OverlayType.ARKNIGHTS
                if not self._config.overlay.arknights_options:
                    from config.epconfig import ArknightsOverlayOptions
                    self._config.overlay.arknights_options = ArknightsOverlayOptions(
                        operator_name="OPERATOR",
                        operator_code="ARKNIGHTS - UNK0",
                        barcode_text="OPERATOR - ARKNIGHTS",
                        aux_text="Operator of Rhodes Island",
                        staff_text="STAFF"
                    )
                
                # 更新干员名称和职业图标
                if self._config.overlay.arknights_options:
                    self._config.overlay.arknights_options.operator_name = self.edit_ark_name.text()
                    # 获取职业图标
                    class_value = self.combo_ark_class.currentData()
                    if class_value:
                        # 使用内置职业图标
                        self._config.overlay.arknights_options.operator_class_icon = f"class_icons/{class_value}.png"
                    else:
                        # 清除职业图标
                        self._config.overlay.arknights_options.operator_class_icon = ""
            elif template == "自定义模板":
                # 可以在这里添加自定义模板的逻辑
                pass
        except Exception as e:
            print(f"设置模板时出错: {e}")
            import traceback
            traceback.print_exc()

    def _on_config_changed(self):
        """配置变更处理"""
        self.update_config_from_ui()
        self.config_changed.emit()

    def _on_template_changed(self):
        """模板变更处理"""
        template = self.combo_template.currentText()
        # 显示或隐藏明日方舟干员信息
        self.group_arknights.setVisible(template == "明日方舟模板")
        
        # 如果显示明日方舟干员信息，更新自动完成列表
        if template == "明日方舟模板":
            self._update_completer()
        
        self._on_config_changed()

    def _browse_file(self, title: str, filters: list):
        """浏览文件"""
        # 确保基础目录存在
        import os
        import pathlib
        
        # 如果基础目录为空或者不存在，使用桌面目录
        if not self._base_dir or not os.path.exists(self._base_dir):
            # 获取用户桌面目录
            desktop_dir = str(pathlib.Path.home() / "Desktop")
            initial_dir = desktop_dir
        else:
            initial_dir = self._base_dir
        
        path, _ = QFileDialog.getOpenFileName(
            self, f"选择{title}", initial_dir,
            ";;".join(filters)
        )
        if path:
            self.edit_loop_file.setText(path)
            # 更新配置
            if self._config:
                self._config.loop.file = path
                # 检查文件类型
                ext = os.path.splitext(path)[1].lower()
                image_extensions = [".jpg", ".jpeg", ".png", ".bmp", ".gif"]
                self._config.loop.is_image = ext in image_extensions
            # 发送信号
            self.video_file_selected.emit(path)
