"""
Blender场景预设库模块
- 预设场景模板
- 快速场景搭建
- 场景元素组合
- 环境设置
"""

import os
import sys
import logging
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

BLENDER_PATH = r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"


@dataclass
class ScenePreset:
    """场景预设配置"""
    name: str
    description: str
    category: str  # product/nature/architecture/abstract/studio
    elements: List[Dict[str, Any]] = field(default_factory=list)
    lighting: str = "three_point"
    camera_position: Tuple[float, float, float] = (5, -8, 5)
    camera_rotation: Tuple[float, float, float] = (1.0, 0, 0.6)
    background_color: Tuple[float, float, float] = (0.1, 0.1, 0.1)
    world_strength: float = 1.0


# 场景预设库
SCENE_PRESETS = {
    "product_studio": ScenePreset(
        name="Product Studio",
        description="产品展示工作室场景",
        category="studio",
        elements=[
            {"type": "CYLINDER", "location": (0, 0, 0.5), "scale": (2, 2, 0.5), "name": "Pedestal"},
            {"type": "SPHERE", "location": (0, 0, 2), "scale": (1, 1, 1), "name": "Product"},
        ],
        lighting="three_point",
        camera_position=(4, -6, 4),
        camera_rotation=(1.0, 0, 0.6),
        background_color=(0.95, 0.95, 0.95),
    ),
    "dark_studio": ScenePreset(
        name="Dark Studio",
        description="暗色工作室场景（戏剧化灯光）",
        category="studio",
        elements=[
            {"type": "CUBE", "location": (0, 0, 1), "scale": (1.5, 1.5, 2), "name": "Subject"},
        ],
        lighting="dramatic",
        camera_position=(3, -5, 3),
        camera_rotation=(1.0, 0, 0.5),
        background_color=(0.05, 0.05, 0.05),
    ),
    "nature_forest": ScenePreset(
        name="Nature Forest",
        description="自然森林场景",
        category="nature",
        elements=[
            {"type": "CYLINDER", "location": (-2, 0, 2), "scale": (0.3, 0.3, 4), "name": "Tree1_Trunk"},
            {"type": "ICOSPHERE", "location": (-2, 0, 5), "scale": (1.5, 1.5, 1.5), "name": "Tree1_Leaves"},
            {"type": "CYLINDER", "location": (2, 1, 1.5), "scale": (0.25, 0.25, 3), "name": "Tree2_Trunk"},
            {"type": "ICOSPHERE", "location": (2, 1, 4), "scale": (1.2, 1.2, 1.2), "name": "Tree2_Leaves"},
            {"type": "PLANE", "location": (0, 0, 0), "scale": (10, 10, 1), "name": "Ground"},
        ],
        lighting="soft",
        camera_position=(0, -10, 5),
        camera_rotation=(1.1, 0, 0),
        background_color=(0.6, 0.8, 1.0),
    ),
    "abstract_geometric": ScenePreset(
        name="Abstract Geometric",
        description="抽象几何场景",
        category="abstract",
        elements=[
            {"type": "ICOSPHERE", "location": (-2, 0, 2), "scale": (1, 1, 1), "name": "Icosphere"},
            {"type": "TORUS", "location": (2, 0, 2), "scale": (1, 1, 1), "name": "Torus"},
            {"type": "CONE", "location": (0, 2, 2), "scale": (1, 1, 1.5), "name": "Cone"},
            {"type": "CUBE", "location": (0, -2, 1), "scale": (1.5, 1.5, 1.5), "name": "Cube"},
        ],
        lighting="neon",
        camera_position=(5, -8, 5),
        camera_rotation=(1.0, 0, 0.6),
        background_color=(0.1, 0.05, 0.2),
    ),
    "architecture_modern": ScenePreset(
        name="Modern Architecture",
        description="现代建筑场景",
        category="architecture",
        elements=[
            {"type": "CUBE", "location": (0, 0, 3), "scale": (4, 3, 3), "name": "Building"},
            {"type": "CUBE", "location": (0, 0, 0.1), "scale": (8, 8, 0.2), "name": "Ground"},
            {"type": "CUBE", "location": (-3, 0, 1), "scale": (0.5, 2, 2), "name": "Window1"},
            {"type": "CUBE", "location": (3, 0, 1), "scale": (0.5, 2, 2), "name": "Window2"},
        ],
        lighting="soft",
        camera_position=(8, -8, 6),
        camera_rotation=(1.1, 0, 0.8),
        background_color=(0.8, 0.85, 0.9),
    ),
    "neon_cyberpunk": ScenePreset(
        name="Neon Cyberpunk",
        description="赛博朋克霓虹场景",
        category="abstract",
        elements=[
            {"type": "CUBE", "location": (-3, 0, 2), "scale": (1, 1, 4), "name": "Building1"},
            {"type": "CUBE", "location": (0, 0, 3), "scale": (1.5, 1.5, 6), "name": "Building2"},
            {"type": "CUBE", "location": (3, 0, 1.5), "scale": (1, 1, 3), "name": "Building3"},
            {"type": "PLANE", "location": (0, 0, 0), "scale": (10, 10, 1), "name": "Ground"},
        ],
        lighting="neon",
        camera_position=(5, -8, 4),
        camera_rotation=(1.0, 0, 0.6),
        background_color=(0.05, 0.02, 0.1),
    ),
    "minimal_white": ScenePreset(
        name="Minimal White",
        description="极简白色场景",
        category="studio",
        elements=[
            {"type": "SPHERE", "location": (0, 0, 1), "scale": (1, 1, 1), "name": "Subject"},
            {"type": "PLANE", "location": (0, 0, 0), "scale": (20, 20, 1), "name": "Ground"},
        ],
        lighting="soft",
        camera_position=(3, -5, 3),
        camera_rotation=(1.0, 0, 0.6),
        background_color=(1.0, 1.0, 1.0),
    ),
    "ocean_sunset": ScenePreset(
        name="Ocean Sunset",
        description="海洋日落场景",
        category="nature",
        elements=[
            {"type": "PLANE", "location": (0, 0, 0), "scale": (20, 20, 1), "name": "Ocean"},
            {"type": "SPHERE", "location": (0, 8, 5), "scale": (2, 2, 2), "name": "Sun"},
        ],
        lighting="warm",
        camera_position=(0, -10, 3),
        camera_rotation=(1.2, 0, 0),
        background_color=(1.0, 0.6, 0.3),
    ),
}


class ScenePresets:
    """Blender场景预设库"""

    def __init__(self, blender_path: str = None):
        self.blender_path = blender_path or BLENDER_PATH
        self.presets = SCENE_PRESETS

    def create_scene(
        self,
        output_path: str,
        preset_name: str = "product_studio",
        custom_elements: List[Dict[str, Any]] = None,
    ) -> bool:
        """创建预设场景

        Args:
            output_path: 输出路径
            preset_name: 预设名称
            custom_elements: 自定义元素（覆盖预设）

        Returns:
            True成功，False失败
        """
        preset = self.presets.get(preset_name)
        if not preset:
            logger.error(f"未知场景预设: {preset_name}")
            return False

        elements = custom_elements or preset.elements

        # 生成元素创建脚本
        elements_script = ""
        for i, elem in enumerate(elements):
            elem_type = elem.get("type", "CUBE")
            location = elem.get("location", (0, 0, 0))
            scale = elem.get("scale", (1, 1, 1))
            name = elem.get("name", f"Element_{i}")

            if elem_type == "CUBE":
                create = f"bpy.ops.mesh.primitive_cube_add(size=2, location={location})"
            elif elem_type == "SPHERE":
                create = f"bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location={location})"
            elif elem_type == "CYLINDER":
                create = f"bpy.ops.mesh.primitive_cylinder_add(radius=1, depth=2, location={location})"
            elif elem_type == "CONE":
                create = f"bpy.ops.mesh.primitive_cone_add(radius1=1, depth=2, location={location})"
            elif elem_type == "PLANE":
                create = f"bpy.ops.mesh.primitive_plane_add(size=2, location={location})"
            elif elem_type == "TORUS":
                create = f"bpy.ops.mesh.primitive_torus_add(major_radius=1, minor_radius=0.3, location={location})"
            elif elem_type == "ICOSPHERE":
                create = f"bpy.ops.mesh.primitive_ico_sphere_add(radius=1, subdivisions=3, location={location})"
            else:
                create = f"bpy.ops.mesh.primitive_cube_add(size=2, location={location})"

            elements_script += f"""
{create}
elem_{i} = bpy.context.active_object
elem_{i}.name = "{name}"
elem_{i}.scale = {scale}
"""

        # 灯光设置
        if preset.lighting == "three_point":
            lighting_script = """
bpy.ops.object.light_add(type='AREA', location=(5, -5, 10))
key = bpy.context.active_object
key.data.energy = 1000
key.data.size = 5

bpy.ops.object.light_add(type='AREA', location=(-5, -5, 5))
fill = bpy.context.active_object
fill.data.energy = 400
fill.data.size = 4

bpy.ops.object.light_add(type='AREA', location=(0, 5, 8))
rim = bpy.context.active_object
rim.data.energy = 800
rim.data.size = 3
"""
        elif preset.lighting == "dramatic":
            lighting_script = """
bpy.ops.object.light_add(type='SPOT', location=(3, -5, 10))
spot = bpy.context.active_object
spot.data.energy = 2000
spot.data.spot_size = 0.5
"""
        elif preset.lighting == "neon":
            lighting_script = """
bpy.ops.object.light_add(type='POINT', location=(-3, 0, 3))
neon1 = bpy.context.active_object
neon1.data.energy = 3000
neon1.data.color = (0.2, 0.8, 1.0)

bpy.ops.object.light_add(type='POINT', location=(3, 0, 3))
neon2 = bpy.context.active_object
neon2.data.energy = 3000
neon2.data.color = (1.0, 0.2, 0.8)
"""
        elif preset.lighting == "warm":
            lighting_script = """
bpy.ops.object.light_add(type='SUN', location=(0, -10, 10))
sun = bpy.context.active_object
sun.data.energy = 2.0
sun.data.color = (1.0, 0.8, 0.5)
"""
        else:  # soft
            lighting_script = """
bpy.ops.object.light_add(type='AREA', location=(0, -8, 8))
soft = bpy.context.active_object
soft.data.energy = 800
soft.data.size = 10
"""

        script = f"""
import bpy

# 清除场景
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# 设置背景
bpy.context.scene.world.use_nodes = True
bg = bpy.context.scene.world.node_tree.nodes['Background']
bg.inputs['Color'].default_value = {preset.background_color}
bg.inputs['Strength'].default_value = {preset.world_strength}

# 创建场景元素
{elements_script}

# 设置灯光
{lighting_script}

# 添加相机
bpy.ops.object.camera_add(location={preset.camera_position})
camera = bpy.context.active_object
camera.rotation_euler = {preset.camera_rotation}
bpy.context.scene.camera = camera

# 保存
bpy.ops.wm.save_as_mainfile(filepath=r'{output_path}')
print("SCENE_PRESET_DONE")
"""
        return self._run_blender(script, output_path)

    def list_presets(self) -> List[str]:
        """列出所有场景预设"""
        return list(self.presets.keys())

    def get_preset_info(self, preset_name: str) -> Optional[Dict[str, Any]]:
        """获取预设信息"""
        preset = self.presets.get(preset_name)
        if preset:
            return {
                "name": preset.name,
                "description": preset.description,
                "category": preset.category,
                "element_count": len(preset.elements),
                "lighting": preset.lighting,
            }
        return None

    def _run_blender(self, script: str, output_path: str) -> bool:
        """运行Blender脚本"""
        import subprocess
        import tempfile

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        script_path = os.path.join(tempfile.gettempdir(), "blender_scene.py")
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(script)

        try:
            result = subprocess.run(
                [self.blender_path, "--background", "--python", script_path],
                capture_output=True, text=True, timeout=120
            )
            if "DONE" in result.stdout or os.path.exists(output_path):
                logger.info(f"场景已生成: {output_path}")
                return True
            else:
                logger.error(f"Blender执行失败: {result.stderr[-500:]}")
                return False
        except subprocess.TimeoutExpired:
            logger.error("Blender执行超时")
            return False
        except Exception as e:
            logger.error(f"Blender执行异常: {e}")
            return False
        finally:
            if os.path.exists(script_path):
                os.remove(script_path)


def main():
    """测试场景预设库"""
    presets = ScenePresets()

    # 列出预设
    print(f"可用场景预设 ({len(presets.list_presets())}种):")
    for name in presets.list_presets():
        info = presets.get_preset_info(name)
        print(f"  - {name}: {info['description']} ({info['category']})")

    # 测试产品工作室
    output = r"D:\DobaoWork_Project\Ai_Video_Editor\test_output\product_studio.blend"
    success = presets.create_scene(output, "product_studio")
    print(f"产品工作室: {'成功' if success else '失败'}")

    # 测试抽象几何
    output2 = r"D:\DobaoWork_Project\Ai_Video_Editor\test_output\abstract_geometric.blend"
    success2 = presets.create_scene(output2, "abstract_geometric")
    print(f"抽象几何: {'成功' if success2 else '失败'}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    main()
