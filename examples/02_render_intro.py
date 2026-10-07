"""示例2: 典型场景 - 渲染3D片头"""
import os, sys
SKILL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if SKILL_ROOT not in sys.path:
    sys.path.insert(0, SKILL_ROOT)
from blender_controls import create_controls

def main():
    bc = create_controls()
    if not bc.is_available():
        print("Blender不可用，请先安装Blender")
        return
    # 渲染电影感片头
    output = bc.render_intro(
        style="cinematic",
        text="AI VIDEO",
        duration=3.0,
        width=1080, height=1920,
    )
    print(f"片头输出: {output}")

if __name__ == "__main__":
    main()
