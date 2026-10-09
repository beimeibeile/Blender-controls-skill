"""
Blender 3D对象库模块
- 预设几何体
- 参数化对象生成
- 对象变换工具
- 对象组合预设
- 模型导入导出
"""

import os
import sys
import logging
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

BLENDER_PATH = r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"


@dataclass
class ObjectConfig:
    """对象配置"""
    name: str = "Object"
    object_type: str = "CUBE"  # CUBE/SPHERE/CYLINDER/CONE/PLANE/TORUS/ICOSPHERE/MONKEY
    location: Tuple[float, float, float] = (0, 0, 0)
    rotation: Tuple[float, float, float] = (0, 0, 0)
    scale: Tuple[float, float, float] = (1, 1, 1)
    size: float = 2.0
    radius: float = 1.0
    depth: float = 2.0
    vertices: int = 32
    material: str = None


# 对象组合预设
OBJECT_COMPOSITIONS = {
    "product_display": [
        {"type": "CYLINDER", "location": (0, 0, 0.5), "scale": (2, 2, 0.5), "name": "Base"},
        {"type": "SPHERE", "location": (0, 0, 2), "scale": (1, 1, 1), "name": "Product"},
    ],
    "tower": [
        {"type": "CUBE", "location": (0, 0, 1), "scale": (1.5, 1.5, 1), "name": "Bottom"},
        {"type": "CUBE", "location": (0, 0, 3), "scale": (1.2, 1.2, 1), "name": "Middle"},
        {"type": "CUBE", "location": (0, 0, 5), "scale": (0.9, 0.9, 1), "name": "Top"},
    ],
    "pyramid": [
        {"type": "CUBE", "location": (0, 0, 0.5), "scale": (3, 3, 1), "name": "Layer1"},
        {"type": "CUBE", "location": (0, 0, 1.5), "scale": (2, 2, 1), "name": "Layer2"},
        {"type": "CUBE", "location": (0, 0, 2.5), "scale": (1, 1, 1), "name": "Layer3"},
    ],
    "solar_system": [
        {"type": "SPHERE", "location": (0, 0, 0), "scale": (2, 2, 2), "name": "Sun"},
        {"type": "SPHERE", "location": (5, 0, 0), "scale": (0.5, 0.5, 0.5), "name": "Planet1"},
        {"type": "SPHERE", "location": (-8, 0, 0), "scale": (0.8, 0.8, 0.8), "name": "Planet2"},
        {"type": "SPHERE", "location": (0, 10, 0), "scale": (0.6, 0.6, 0.6), "name": "Planet3"},
    ],
    "living_room": [
        {"type": "CUBE", "location": (0, -2, 0.5), "scale": (3, 1, 1), "name": "Sofa"},
        {"type": "CUBE", "location": (0, 1, 0.3), "scale": (2, 1.5, 0.6), "name": "Table"},
        {"type": "CUBE", "location": (-2, -2, 1), "scale": (0.8, 0.8, 2), "name": "Lamp"},
        {"type": "CUBE", "location": (2, -2, 0.4), "scale": (0.6, 0.6, 0.8), "name": "Plant"},
    ],
    "city_block": [
        {"type": "CUBE", "location": (-3, -3, 5), "scale": (2, 2, 5), "name": "Building1"},
        {"type": "CUBE", "location": (3, -3, 8), "scale": (2, 2, 8), "name": "Building2"},
        {"type": "CUBE", "location": (-3, 3, 3), "scale": (2, 2, 3), "name": "Building3"},
        {"type": "CUBE", "location": (3, 3, 6), "scale": (2, 2, 6), "name": "Building4"},
        {"type": "CUBE", "location": (0, 0, 0.1), "scale": (10, 10, 0.2), "name": "Ground"},
    ],
}


class ObjectLibrary:
    """Blender 3D对象库"""

    def __init__(self, blender_path: str = None):
        self.blender_path = blender_path or BLENDER_PATH
        self.compositions = OBJECT_COMPOSITIONS

    def create_object_script(self, config: ObjectConfig) -> str:
        """生成创建对象的Blender脚本"""
        if config.object_type == "CUBE":
            create = f"bpy.ops.mesh.primitive_cube_add(size={config.size}, location={config.location})"
        elif config.object_type == "SPHERE":
            create = f"bpy.ops.mesh.primitive_uv_sphere_add(radius={config.radius}, segments={config.vertices}, location={config.location})"
        elif config.object_type == "CYLINDER":
            create = f"bpy.ops.mesh.primitive_cylinder_add(radius={config.radius}, depth={config.depth}, vertices={config.vertices}, location={config.location})"
        elif config.object_type == "CONE":
            create = f"bpy.ops.mesh.primitive_cone_add(radius1={config.radius}, depth={config.depth}, vertices={config.vertices}, location={config.location})"
        elif config.object_type == "PLANE":
            create = f"bpy.ops.mesh.primitive_plane_add(size={config.size}, location={config.location})"
        elif config.object_type == "TORUS":
            create = f"bpy.ops.mesh.primitive_torus_add(major_radius={config.radius}, minor_radius={config.radius*0.3}, location={config.location})"
        elif config.object_type == "ICOSPHERE":
            create = f"bpy.ops.mesh.primitive_ico_sphere_add(radius={config.radius}, subdivisions=3, location={config.location})"
        elif config.object_type == "MONKEY":
            create = f"bpy.ops.mesh.primitive_monkey_add(size={config.size}, location={config.location})"
        else:
            create = f"bpy.ops.mesh.primitive_cube_add(size={config.size}, location={config.location})"

        return f"""
{create}
obj = bpy.context.active_object
obj.name = "{config.name}"
obj.rotation_euler = {config.rotation}
obj.scale = {config.scale}
"""

    def create_composition(
        self,
        output_path: str,
        composition_name: str = "product_display",
        add_camera: bool = True,
        add_lighting: bool = True,
    ) -> bool:
        """创建对象组合场景

        Args:
            output_path: 输出路径
            composition_name: 组合名称
            add_camera: 是否添加相机
            add_lighting: 是否添加灯光

        Returns:
            True成功，False失败
        """
        composition = self.compositions.get(composition_name)
        if not composition:
            logger.error(f"未知组合: {composition_name}")
            return False

        objects_script = ""
        for i, obj_data in enumerate(composition):
            config = ObjectConfig(
                name=obj_data.get("name", f"Object_{i}"),
                object_type=obj_data.get("type", "CUBE"),
                location=obj_data.get("location", (0, 0, 0)),
                scale=obj_data.get("scale", (1, 1, 1)),
            )
            objects_script += self.create_object_script(config)

        extras = ""
        if add_camera:
            extras += """
bpy.ops.object.camera_add(location=(8, -8, 6))
camera = bpy.context.active_object
camera.rotation_euler = (1.0, 0, 0.8)
bpy.context.scene.camera = camera
"""
        if add_lighting:
            extras += """
bpy.ops.object.light_add(type='AREA', location=(5, -5, 10))
light = bpy.context.active_object
light.data.energy = 800
light.data.size = 8
"""

        script = f"""
import bpy

# 清除场景
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# 创建对象组合
{objects_script}

# 添加相机和灯光
{extras}

# 保存
bpy.ops.wm.save_as_mainfile(filepath=r'{output_path}')
print("COMPOSITION_DONE")
"""
        return self._run_blender(script, output_path)

    def create_parametric_geometry(
        self,
        output_path: str,
        geometry_type: str = "spiral",
        count: int = 20,
        radius: float = 5.0,
        height: float = 10.0,
    ) -> bool:
        """创建参数化几何场景

        Args:
            output_path: 输出路径
            geometry_type: 几何类型（spiral/grid/wave/random）
            count: 对象数量
            radius: 半径
            height: 高度

        Returns:
            True成功，False失败
        """
        if geometry_type == "spiral":
            gen_script = f"""
import math
for i in range({count}):
    angle = i * 0.5
    r = {radius} * (1 - i / {count})
    x = r * math.cos(angle)
    y = r * math.sin(angle)
    z = {height} * i / {count}
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.3, location=(x, y, z))
    obj = bpy.context.active_object
    obj.name = f"Spiral_{{i}}"
"""
        elif geometry_type == "grid":
            grid_size = int(count ** 0.5)
            gen_script = f"""
for i in range({grid_size}):
    for j in range({grid_size}):
        x = (i - {grid_size}/2) * 2
        y = (j - {grid_size}/2) * 2
        z = 0.5
        bpy.ops.mesh.primitive_cube_add(size=1.5, location=(x, y, z))
        obj = bpy.context.active_object
        obj.name = f"Grid_{{i}}_{{j}}"
"""
        elif geometry_type == "wave":
            gen_script = f"""
import math
for i in range({count}):
    x = (i - {count}/2) * 0.8
    y = 0
    z = math.sin(i * 0.3) * 2 + 3
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.4, location=(x, y, z))
    obj = bpy.context.active_object
    obj.name = f"Wave_{{i}}"
"""
        else:  # random
            gen_script = f"""
import random
random.seed(42)
for i in range({count}):
    x = random.uniform(-{radius}, {radius})
    y = random.uniform(-{radius}, {radius})
    z = random.uniform(0, {height})
    size = random.uniform(0.3, 1.0)
    bpy.ops.mesh.primitive_cube_add(size=size, location=(x, y, z))
    obj = bpy.context.active_object
    obj.name = f"Random_{{i}}"
"""

        script = f"""
import bpy

# 清除场景
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# 生成参数化几何
{gen_script}

# 添加相机
bpy.ops.object.camera_add(location=(10, -10, 8))
camera = bpy.context.active_object
camera.rotation_euler = (1.0, 0, 0.8)
bpy.context.scene.camera = camera

# 添加灯光
bpy.ops.object.light_add(type='AREA', location=(5, -5, 10))
light = bpy.context.active_object
light.data.energy = 1000

# 保存
bpy.ops.wm.save_as_mainfile(filepath=r'{output_path}')
print("PARAMETRIC_DONE")
"""
        return self._run_blender(script, output_path)

    def list_compositions(self) -> List[str]:
        """列出所有对象组合预设"""
        return list(self.compositions.keys())

    def _run_blender(self, script: str, output_path: str) -> bool:
        """运行Blender脚本"""
        import subprocess
        import tempfile

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        script_path = os.path.join(tempfile.gettempdir(), "blender_objects.py")
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(script)

        try:
            result = subprocess.run(
                [self.blender_path, "--background", "--python", script_path],
                capture_output=True, text=True, timeout=120
            )
            if "DONE" in result.stdout or os.path.exists(output_path):
                logger.info(f"对象场景已生成: {output_path}")
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
    """测试对象库"""
    lib = ObjectLibrary()

    # 列出预设
    print(f"可用对象组合 ({len(lib.list_compositions())}种):")
    for name in lib.list_compositions():
        print(f"  - {name}")

    # 测试产品展示
    output = r"D:\DobaoWork_Project\Ai_Video_Editor\test_output\product_display.blend"
    success = lib.create_composition(output, "product_display")
    print(f"产品展示: {'成功' if success else '失败'}")

    # 测试螺旋几何
    output2 = r"D:\DobaoWork_Project\Ai_Video_Editor\test_output\spiral_geometry.blend"
    success2 = lib.create_parametric_geometry(output2, "spiral", count=30)
    print(f"螺旋几何: {'成功' if success2 else '失败'}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    main()
