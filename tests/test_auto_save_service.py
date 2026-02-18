"""
单元测试 - 自动保存服务
"""
import pytest
import tempfile
import os
import json
import time
from unittest.mock import Mock, MagicMock

from core.auto_save_service import AutoSaveService, AutoSaveConfig


class TestAutoSaveService:
    """测试自动保存服务"""

    @pytest.fixture
    def temp_dir(self):
        """创建临时目录"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture
    def mock_config(self):
        """创建模拟配置对象"""
        config = Mock()
        config.to_dict.return_value = {'test': 'data'}
        return config

    def test_auto_save_config_default(self):
        """测试默认配置"""
        config = AutoSaveConfig()
        assert config.enabled is True
        assert config.interval_seconds == 300
        assert config.max_backups == 5

    def test_auto_save_config_custom(self):
        """测试自定义配置"""
        config = AutoSaveConfig(
            enabled=False,
            interval_seconds=600,
            max_backups=10
        )
        assert config.enabled is False
        assert config.interval_seconds == 600
        assert config.max_backups == 10

    def test_auto_save_service_initialization(self, temp_dir):
        """测试服务初始化"""
        config = AutoSaveConfig(enabled=False)
        service = AutoSaveService(config)
        assert service.config.enabled is False
        assert service._timer is None

    def test_auto_save_disabled(self, temp_dir, mock_config):
        """测试禁用自动保存"""
        config = AutoSaveConfig(enabled=False)
        service = AutoSaveService(config)

        service.start(mock_config, "test.json", temp_dir)

        # 禁用状态下不应该启动定时器
        assert service._timer is None

    def test_auto_save_enabled(self, temp_dir, mock_config):
        """测试启用自动保存"""
        config = AutoSaveConfig(
            enabled=True,
            interval_seconds=1  # 1秒间隔用于测试
        )
        service = AutoSaveService(config)

        service.start(mock_config, "test.json", temp_dir)

        # 启用状态下应该启动定时器
        assert service._timer is not None
        assert service._timer.isActive()

        service.stop()

    def test_auto_save_stop(self, temp_dir, mock_config):
        """测试停止自动保存"""
        config = AutoSaveConfig(
            enabled=True,
            interval_seconds=1
        )
        service = AutoSaveService(config)

        service.start(mock_config, "test.json", temp_dir)
        service.stop()

        # 停止后定时器应该不活跃
        assert not service._timer.isActive()

    def test_auto_save_update_config(self, temp_dir):
        """测试更新配置"""
        config = AutoSaveConfig(enabled=False)
        service = AutoSaveService(config)

        # 更新配置
        new_config = AutoSaveConfig(
            enabled=True,
            interval_seconds=600
        )
        service.update_config(new_config)

        assert service.config.enabled is True
        assert service.config.interval_seconds == 600

    def test_auto_save_clear_backups(self, temp_dir, mock_config):
        """测试清理备份"""
        config = AutoSaveConfig(enabled=False)
        service = AutoSaveService(config)

        # 创建一些备份文件
        autosave_dir = os.path.join(temp_dir, ".autosave")
        os.makedirs(autosave_dir, exist_ok=True)

        for i in range(3):
            backup_file = os.path.join(autosave_dir, f"backup_{i}.json")
            with open(backup_file, 'w') as f:
                json.dump({'backup': i}, f)

        # 清理备份
        service.clear_backups(temp_dir)

        # 检查备份是否被删除
        assert not os.path.exists(autosave_dir) or len(os.listdir(autosave_dir)) == 0