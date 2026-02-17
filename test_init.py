#!/usr/bin/env python3
"""
测试程序初始化，不启动GUI
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath('.'))

try:
    print("开始测试程序初始化...")
    
    # 检查依赖
    print("1. 检查依赖...")
    from main import check_dependencies
    check_dependencies()
    print("依赖检查通过!")
    
    # 测试模块导入
    print("2. 测试模块导入...")
    
    # 测试配置模块
    from config.constants import APP_VERSION
    print(f"  - 配置模块: 版本 {APP_VERSION}")
    
    # 测试核心模块
    from core.validator import ConfigValidator
    print("  - 核心模块: 验证器导入成功")
    
    # 测试GUI模块
    from gui.main_window import MainWindow
    print("  - GUI模块: 主窗口导入成功")
    
    # 测试工具模块
    from utils.logger import setup_logger
    print("  - 工具模块: 日志系统导入成功")
    
    # 测试日志系统
    print("3. 测试日志系统...")
    logger = setup_logger()
    logger.info("日志系统初始化成功")
    print("日志系统测试成功!")
    
    print("\n✅ 程序初始化测试全部通过!")
    print("程序应该可以正常运行")
    
    sys.exit(0)
    
except Exception as e:
    print(f"\n❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
