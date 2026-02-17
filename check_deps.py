
#!/usr/bin/env python3
import sys
import os

missing = []

try:
    from PyQt6.QtWidgets import QApplication
    print("✓ PyQt6 已安装")
except ImportError:
    missing.append("PyQt6")
    print("✗ PyQt6 未安装")

try:
    import cv2
    print("✓ opencv-python 已安装")
except ImportError:
    missing.append("opencv-python")
    print("✗ opencv-python 未安装")

try:
    from PIL import Image
    print("✓ Pillow 已安装")
except ImportError:
    missing.append("Pillow")
    print("✗ Pillow 未安装")

try:
    import numpy
    print("✓ numpy 已安装")
except ImportError:
    missing.append("numpy")
    print("✗ numpy 未安装")

try:
    import jsonschema
    print("✓ jsonschema 已安装")
except ImportError:
    missing.append("jsonschema")
    print("✗ jsonschema 未安装")

try:
    from thefuzz import fuzz
    print("✓ thefuzz 已安装")
except ImportError:
    missing.append("thefuzz")
    print("✗ thefuzz 未安装")

try:
    import Levenshtein
    print("✓ python-Levenshtein 已安装")
except ImportError:
    missing.append("python-Levenshtein")
    print("✗ python-Levenshtein 未安装")

if missing:
    print(f"\n缺少 {len(missing)} 个依赖: {', '.join(missing)}")
    sys.exit(1)
else:
    print("\n✓ 所有依赖都已安装!")
    sys.exit(0)

