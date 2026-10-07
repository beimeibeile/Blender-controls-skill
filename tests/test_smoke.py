"""冒烟测试: blender-controls-skill核心模块可导入、可初始化（不依赖Blender实际运行）"""
import os, sys
SKILL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if SKILL_ROOT not in sys.path:
    sys.path.insert(0, SKILL_ROOT)

passed = 0; failed = 0
def check(name, func):
    global passed, failed
    try:
        func(); print(f"  PASS: {name}"); passed += 1
    except Exception as e:
        print(f"  FAIL: {name} -> {type(e).__name__}: {e}"); failed += 1

print("=== Module Imports ===")
check('blender_controls', lambda: __import__('blender_controls'))
check('cap_api_wrapper', lambda: __import__('capabilities.cap_api_wrapper.blender_runner', fromlist=['BlenderRunner']))
check('cap_scene_manager', lambda: __import__('capabilities.cap_scene_manager.manager', fromlist=['SceneManager']))
check('cap_effects_library', lambda: __import__('capabilities.cap_effects_library.library', fromlist=['EffectsLibrary']))
check('cap_batch_renderer', lambda: __import__('capabilities.cap_batch_renderer.renderer', fromlist=['BatchRenderer']))
check('cap_quality_control', lambda: __import__('capabilities.cap_quality_control.controller', fromlist=['QualityController']))
check('cap_self_evolution', lambda: __import__('capabilities.cap_self_evolution.evolution', fromlist=['SelfEvolution']))

print()
print("=== Offline Init ===")
from blender_controls import BlenderControls, create_controls
check('create_controls', lambda: create_controls())
check('list_effects', lambda: create_controls().list_effects())
check('get_status', lambda: create_controls().get_status())

print()
print(f"=== 结果: {passed} passed, {failed} failed ===")
sys.exit(1 if failed > 0 else 0)
