"""
单元测试 - 崩溃恢复服务
"""
import pytest
import tempfile
import os
import json
import time
from unittest.mock import Mock

from core.crash_recovery_service import CrashRecoveryService, RecoveryInfo


class TestCrashRecoveryService:
    """测试崩溃恢复服务"""

    @pytest.fixture
    def temp_dir(self):
        """创建临时目录"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture
    def recovery_service(self, temp_dir):
        """创建恢复服务实例"""
        service = CrashRecoveryService()
        service.initialize(temp_dir)
        yield service

    def test_recovery_info_creation(self):
        """测试恢复信息创建"""
        info = RecoveryInfo(
            backup_path="/path/to/backup.json",
            timestamp=time.time(),
            project_path="/path/to/project.json",
            is_temp=False
        )

        assert info.backup_path == "/path/to/backup.json"
        assert info.project_path == "/path/to/project.json"
        assert info.is_temp is False

    def test_service_initialization(self, temp_dir):
        """测试服务初始化"""
        service = CrashRecoveryService()
        service.initialize(temp_dir)

        recovery_dir = os.path.join(temp_dir, ".recovery")
        assert os.path.exists(recovery_dir)
        assert service._recovery_dir == recovery_dir

    def test_save_recovery_info(self, recovery_service, temp_dir):
        """测试保存恢复信息"""
        recovery_info = RecoveryInfo(
            backup_path="/path/to/backup.json",
            timestamp=time.time(),
            project_path="/path/to/project.json",
            is_temp=False
        )

        recovery_service.save_recovery_info(recovery_info)

        # 检查恢复信息文件是否创建
        recovery_dir = os.path.join(temp_dir, ".recovery")
        files = os.listdir(recovery_dir)
        assert len(files) > 0

    def test_check_crash_recovery_empty(self, recovery_service):
        """测试检查崩溃恢复（无恢复项目）"""
        recovery_list = recovery_service.check_crash_recovery()

        assert len(recovery_list) == 0
        assert isinstance(recovery_list, list)

    def test_check_crash_recovery_with_data(self, recovery_service, temp_dir):
        """测试检查崩溃恢复（有恢复项目）"""
        # 创建恢复信息
        recovery_info = RecoveryInfo(
            backup_path="/path/to/backup.json",
            timestamp=time.time(),
            project_path="/path/to/project.json",
            is_temp=False
        )

        recovery_service.save_recovery_info(recovery_info)

        # 检查崩溃恢复
        recovery_list = recovery_service.check_crash_recovery()

        assert len(recovery_list) > 0
        assert isinstance(recovery_list[0], RecoveryInfo)

    def test_clear_recovery_info(self, recovery_service, temp_dir):
        """测试清除恢复信息"""
        # 创建恢复信息
        recovery_info = RecoveryInfo(
            backup_path="/path/to/backup.json",
            timestamp=time.time(),
            project_path="/path/to/project.json",
            is_temp=False
        )

        recovery_service.save_recovery_info(recovery_info)

        # 清除恢复信息
        recovery_service.clear_recovery_info(recovery_info)

        # 检查恢复信息是否被删除
        recovery_list = recovery_service.check_crash_recovery()
        assert len(recovery_list) == 0

    def test_clear_all_recovery(self, recovery_service, temp_dir):
        """测试清除所有恢复信息"""
        # 创建多个恢复信息
        for i in range(3):
            recovery_info = RecoveryInfo(
                backup_path=f"/path/to/backup_{i}.json",
                timestamp=time.time(),
                project_path=f"/path/to/project_{i}.json",
                is_temp=False
            )
            recovery_service.save_recovery_info(recovery_info)

        # 清除所有恢复信息
        recovery_service.clear_all_recovery()

        # 检查所有恢复信息是否被删除
        recovery_list = recovery_service.check_crash_recovery()
        assert len(recovery_list) == 0

    def test_cleanup_old_recoveries(self, recovery_service, temp_dir):
        """测试清理旧的恢复信息"""
        # 创建旧的恢复信息（超过24小时）
        old_timestamp = time.time() - (25 * 3600)  # 25小时前
        old_info = RecoveryInfo(
            backup_path="/path/to/old_backup.json",
            timestamp=old_timestamp,
            project_path="/path/to/old_project.json",
            is_temp=False
        )
        recovery_service.save_recovery_info(old_info)

        # 创建新的恢复信息
        new_info = RecoveryInfo(
            backup_path="/path/to/new_backup.json",
            timestamp=time.time(),
            project_path="/path/to/new_project.json",
            is_temp=False
        )
        recovery_service.save_recovery_info(new_info)

        # 清理旧的恢复信息
        recovery_service.cleanup_old_recoveries(max_age_hours=24)

        # 检查旧的恢复信息是否被删除
        recovery_list = recovery_service.check_crash_recovery()
        assert len(recovery_list) == 1
        assert recovery_list[0].backup_path == "/path/to/new_backup.json"

    def test_get_recovery_summary(self, recovery_service, temp_dir):
        """测试获取恢复摘要"""
        # 创建恢复信息
        recovery_info = RecoveryInfo(
            backup_path="/path/to/backup.json",
            timestamp=time.time(),
            project_path="/path/to/project.json",
            is_temp=False
        )

        recovery_service.save_recovery_info(recovery_info)

        # 获取恢复摘要
        summary = recovery_service.get_recovery_summary()

        assert 'total_count' in summary
        assert 'temp_count' in summary
        assert 'permanent_count' in summary
        assert summary['total_count'] > 0