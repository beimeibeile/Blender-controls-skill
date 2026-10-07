"""示例1: 最小可用 - 检查Blender状态并列出可用特效"""
import os, sys
SKILL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if SKILL_ROOT not in sys.path:
    sys.path.insert(0, SKILL_ROOT)
from blender_controls import create_controls

def main():
    bc = create_controls()
    status = bc.get_status()
    print(f"Blender可用: {status['available']}")
    print(f"Blender路径: {status['blender_path']}")
    print(f"\n可用特效:")
    for cat, items in status['effects'].items():
        print(f"  {cat}: {items}")

if __name__ == "__main__":
    main()
