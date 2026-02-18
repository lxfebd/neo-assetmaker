"""
单元测试 - 错误处理器
"""
import pytest
from unittest.mock import Mock, patch

from core.error_handler import ErrorHandler, ErrorInfo, handle_error, show_error


class TestErrorHandler:
    """测试错误处理器"""

    @pytest.fixture
    def error_handler(self):
        """创建错误处理器实例"""
        return ErrorHandler()

    def test_error_info_creation(self):
        """测试错误信息创建"""
        error = Exception("Test error")
        error_info = ErrorInfo(
            original_error=error,
            user_message="用户友好的错误消息",
            error_type="Exception",
            severity="error",
            suggestions=["建议1", "建议2"],
            technical_details="技术详情"
        )

        assert error_info.original_error == error
        assert error_info.user_message == "用户友好的错误消息"
        assert error_info.error_type == "Exception"
        assert error_info.severity == "error"
        assert len(error_info.suggestions) == 2
        assert error_info.technical_details == "技术详情"

    def test_error_handler_initialization(self, error_handler):
        """测试错误处理器初始化"""
        assert error_handler is not None
        assert hasattr(error_handler, '_error_patterns')
        assert hasattr(error_handler, 'error_occurred')

    def test_handle_file_not_found_error(self, error_handler):
        """测试处理文件未找到错误"""
        error = FileNotFoundError("文件不存在")

        error_info = error_handler.handle_error(error, "打开文件")

        assert error_info.error_type == "FileNotFoundError"
        assert error_info.severity == "error"
        assert "文件未找到" in error_info.user_message
        assert len(error_info.suggestions) > 0

    def test_handle_permission_error(self, error_handler):
        """测试处理权限错误"""
        error = PermissionError("权限不足")

        error_info = error_handler.handle_error(error, "写入文件")

        assert error_info.error_type == "PermissionError"
        assert error_info.severity == "error"
        assert "权限不足" in error_info.user_message
        assert len(error_info.suggestions) > 0

    def test_handle_connection_error(self, error_handler):
        """测试处理连接错误"""
        error = ConnectionError("连接失败")

        error_info = error_handler.handle_error(error, "网络请求")

        assert error_info.error_type == "ConnectionError"
        assert error_info.severity == "error"
        assert "网络连接失败" in error_info.user_message
        assert len(error_info.suggestions) > 0

    def test_handle_memory_error(self, error_handler):
        """测试处理内存错误"""
        error = MemoryError("内存不足")

        error_info = error_handler.handle_error(error, "处理大文件")

        assert error_info.error_type == "MemoryError"
        assert error_info.severity == "critical"
        assert "内存不足" in error_info.user_message
        assert len(error_info.suggestions) > 0

    def test_handle_unknown_error(self, error_handler):
        """测试处理未知错误"""
        class CustomError(Exception):
            pass

        error = CustomError("自定义错误")

        error_info = error_handler.handle_error(error, "自定义操作")

        assert error_info.error_type == "CustomError"
        assert error_info.severity == "info"  # 未知错误默认为info
        assert len(error_info.suggestions) > 0

    def test_determine_severity(self, error_handler):
        """测试确定错误严重程度"""
        critical_errors = ["MemoryError", "SystemError"]
        error_errors = ["FileNotFoundError", "PermissionError", "OSError"]
        warning_errors = ["ValueError", "KeyError", "AttributeError"]

        for error_type in critical_errors:
            severity = error_handler._determine_severity(error_type)
            assert severity == "critical"

        for error_type in error_errors:
            severity = error_handler._determine_severity(error_type)
            assert severity == "error"

        for error_type in warning_errors:
            severity = error_handler._determine_severity(error_type)
            assert severity == "warning"

    def test_translate_exception(self, error_handler):
        """测试翻译异常"""
        error = FileNotFoundError("文件不存在")

        user_message = error_handler.translate_exception(error, "打开文件")

        assert "文件未找到" in user_message

    @patch('core.error_handler.QMessageBox')
    def test_show_error_dialog(self, mock_qmessagebox, error_handler):
        """测试显示错误对话框"""
        error = FileNotFoundError("文件不存在")
        error_info = error_handler.handle_error(error, "打开文件")

        error_handler.show_error_dialog(error_info)

        # 检查是否调用了QMessageBox
        assert mock_qmessagebox.called

    def test_handle_error_convenience_function(self):
        """测试便捷函数"""
        error = FileNotFoundError("文件不存在")

        error_info = handle_error(error, "打开文件")

        assert error_info is not None
        assert isinstance(error_info, ErrorInfo)

    @patch('core.error_handler.show_error')
    @patch('core.error_handler.handle_error')
    def test_show_error_convenience_function(self, mock_handle, mock_show):
        """测试显示错误便捷函数"""
        error = FileNotFoundError("文件不存在")

        show_error(error, "打开文件", parent=None)

        # 检查是否调用了handle_error和show_error_dialog
        assert mock_handle.called
        assert mock_show.called