"""
Blender材质与纹理管理模块
- PBR材质创建与管理
- 程序化纹理生成
- 材质库预设
- 纹理坐标映射
- 节点组管理
"""

import os
import sys
import logging
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

BLENDER_PATH = r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"


@dataclass
class PBRMaterialConfig:
    """PBR材质配置"""
    name: str = "Material"
    base_color: Tuple[float, float, float] = (0.8, 0.8, 0.8)
    metallic: float = 0.0
    roughness: float = 0.5
    specular: float = 0.5
    emission_color: Tuple[float, float, float] = (0, 0, 0)
    emission_strength: float = 0.0
    alpha: float = 1.0
    use_alpha: bool = False
    normal_strength: float = 1.0
    displacement_strength: float = 0.0


# 预设材质库
MATERIAL_PRESETS = {
    "gold": PBRMaterialConfig(
        name="Gold", base_color=(1.0, 0.84, 0.0),
        metallic=1.0, roughness=0.2, specular=1.0
    ),
    "silver": PBRMaterialConfig(
        name="Silver", base_color=(0.95, 0.95, 0.97),
        metallic=1.0, roughness=0.1, specular=1.0
    ),
    "copper": PBRMaterialConfig(
        name="Copper", base_color=(0.95, 0.6, 0.35),
        metallic=1.0, roughness=0.3, specular=1.0
    ),
    "glass": PBRMaterialConfig(
        name="Glass", base_color=(1.0, 1.0, 1.0),
        metallic=0.0, roughness=0.0, specular=1.0,
        alpha=0.3, use_alpha=True
    ),
    "plastic_black": PBRMaterialConfig(
        name="Plastic_Black", base_color=(0.05, 0.05, 0.05),
        metallic=0.0, roughness=0.4, specular=0.5
    ),
    "plastic_white": PBRMaterialConfig(
        name="Plastic_White", base_color=(0.95, 0.95, 0.95),
        metallic=0.0, roughness=0.3, specular=0.5
    ),
    "rubber": PBRMaterialConfig(
        name="Rubber", base_color=(0.1, 0.1, 0.1),
        metallic=0.0, roughness=0.9, specular=0.0
    ),
    "wood": PBRMaterialConfig(
        name="Wood", base_color=(0.6, 0.4, 0.2),
        metallic=0.0, roughness=0.7, specular=0.3
    ),
    "concrete": PBRMaterialConfig(
        name="Concrete", base_color=(0.5, 0.5, 0.5),
        metallic=0.0, roughness=0.8, specular=0.2
    ),
    "neon_blue": PBRMaterialConfig(
        name="Neon_Blue", base_color=(0.0, 0.5, 1.0),
        metallic=0.0, roughness=0.2,
        emission_color=(0.0, 0.5, 1.0), emission_strength=5.0
    ),
    "neon_pink": PBRMaterialConfig(
        name="Neon_Pink", base_color=(1.0, 0.2, 0.6),
        metallic=0.0, roughness=0.2,
        emission_color=(1.0, 0.2, 0.6), emission_strength=5.0
    ),
    "neon_green": PBRMaterialConfig(
        name="Neon_Green", base_color=(0.2, 1.0, 0.4),
        metallic=0.0, roughness=0.2,
        emission_color=(0.2, 1.0, 0.4), emission_strength=5.0
    ),
    "chrome": PBRMaterialConfig(
        name="Chrome", base_color=(0.9, 0.9, 0.95),
        metallic=1.0, roughness=0.05, specular=1.0
    ),
    "brushed_metal": PBRMaterialConfig(
        name="Brushed_Metal", base_color=(0.7, 0.7, 0.72),
        metallic=1.0, roughness=0.4, specular=0.8
    ),
    "ceramic": PBRMaterialConfig(
        name="Ceramic", base_color=(0.95, 0.95, 0.92),
        metallic=0.0, roughness=0.15, specular=0.6
    ),
}


class MaterialManager:
    """Blender材质管理器"""

    def __init__(self, blender_path: str = None):
        self.blender_path = blender_path or BLENDER_PATH
        self.presets = MATERIAL_PRESETS

    def create_pbr_material_script(self, config: PBRMaterialConfig) -> str:
        """生成创建PBR材质的Blender脚本"""
        return f"""
mat = bpy.data.materials.new(name="{config.name}")
mat.use_nodes = True
nodes = mat.node_tree.nodes
links = mat.node_tree.links

# 清除默认节点
for node in nodes:
    nodes.remove(node)

# 创建Principled BSDF节点
bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
bsdf.location = (0, 0)
bsdf.inputs['Base Color'].default_value = ({config.base_color[0]}, {config.base_color[1]}, {config.base_color[2]}, 1.0)
bsdf.inputs['Metallic'].default_value = {config.metallic}
bsdf.inputs['Roughness'].default_value = {config.roughness}
bsdf.inputs['Specular'].default_value = {config.specular}
bsdf.inputs['Emission'].default_value = ({config.emission_color[0]}, {config.emission_color[1]}, {config.emission_color[2]}, 1.0)
bsdf.inputs['Emission Strength'].default_value = {config.emission_strength}
bsdf.inputs['Alpha'].default_value = {config.alpha}

# 创建输出节点
output = nodes.new(type='ShaderNodeOutputMaterial')
output.location = (400, 0)
links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

# 设置透明
mat.blend_method = 'BLEND' if {config.use_alpha} else 'OPAQUE'
mat.show_transparent_back = True
"""

    def create_material_library_scene(
        self,
        output_path: str,
        material_names: List[str] = None,
    ) -> bool:
        """创建材质库展示场景

        Args:
            output_path: 输出路径
            material_names: 要展示的材质名称列表（None表示全部）

        Returns:
            True成功，False失败
        """
        material_names = material_names or list(self.presets.keys())

        # 生成材质创建脚本
        materials_script = ""
        for name in material_names:
            if name in self.presets:
                config = self.presets[name]
                materials_script += self.create_pbr_material_script(config)
                materials_script += f"\ncreated_materials.append(bpy.data.materials['{config.name}'])\n"

        # 生成展示球体脚本
        spheres_script = ""
        for i, name in enumerate(material_names):
            if name in self.presets:
                config = self.presets[name]
                x = (i % 5) * 3 - 6
                y = (i // 5) * 3
                spheres_script += f"""
bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=({x}, {y}, 1))
sphere = bpy.context.active_object
sphere.name = "Sphere_{config.name}"
if '{config.name}' in bpy.data.materials:
    sphere.data.materials.append(bpy.data.materials['{config.name}'])
"""

        script = f"""
import bpy

# 清除场景
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

created_materials = []

# 创建材质
{materials_script}

# 创建展示球体
{spheres_script}

# 添加地面
bpy.ops.mesh.primitive_plane_add(size=30, location=(0, 0, 0))
ground = bpy.context.active_object
ground.name = "Ground"

# 添加灯光
bpy.ops.object.light_add(type='AREA', location=(0, 0, 10))
light = bpy.context.active_object
light.name = "Main_Light"
light.data.energy = 1000
light.data.size = 10

# 添加相机
bpy.ops.object.camera_add(location=(0, -10, 5))
camera = bpy.context.active_object
camera.name = "Camera"
camera.rotation_euler = (1.1, 0, 0)
bpy.context.scene.camera = camera

# 保存
bpy.ops.wm.save_as_mainfile(filepath=r'{output_path}')
print("MATERIAL_LIBRARY_DONE")
"""
        return self._run_blender(script, output_path)

    def apply_material_to_object(
        self,
        output_path: str,
        object_type: str = "CUBE",
        material_name: str = "gold",
        material_config: PBRMaterialConfig = None,
    ) -> bool:
        """创建对象并应用材质

        Args:
            output_path: 输出路径
            object_type: 对象类型（CUBE/SPHERE/CYLINDER/PLANE）
            material_name: 预设材质名称
            material_config: 自定义材质配置（覆盖预设）

        Returns:
            True成功，False失败
        """
        config = material_config or self.presets.get(material_name, PBRMaterialConfig())
        material_script = self.create_pbr_material_script(config)

        if object_type == "CUBE":
            create_obj = "bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 1))"
        elif object_type == "SPHERE":
            create_obj = "bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(0, 0, 1))"
        elif object_type == "CYLINDER":
            create_obj = "bpy.ops.mesh.primitive_cylinder_add(radius=1, depth=2, location=(0, 0, 1))"
        else:
            create_obj = "bpy.ops.mesh.primitive_plane_add(size=4, location=(0, 0, 0))"

        script = f"""
import bpy

# 清除场景
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# 创建材质
{material_script}

# 创建对象
{create_obj}
obj = bpy.context.active_object
obj.name = "{object_type}_{config.name}"

# 应用材质
if '{config.name}' in bpy.data.materials:
    obj.data.materials.append(bpy.data.materials['{config.name}'])

# 添加灯光
bpy.ops.object.light_add(type='AREA', location=(5, -5, 10))
light = bpy.context.active_object
light.data.energy = 500

# 添加相机
bpy.ops.object.camera_add(location=(5, -5, 3))
camera = bpy.context.active_object
camera.rotation_euler = (1.1, 0, 0.8)
bpy.context.scene.camera = camera

# 保存
bpy.ops.wm.save_as_mainfile(filepath=r'{output_path}')
print("APPLY_MATERIAL_DONE")
"""
        return self._run_blender(script, output_path)

    def list_presets(self) -> List[str]:
        """列出所有预设材质"""
        return list(self.presets.keys())

    def _run_blender(self, script: str, output_path: str) -> bool:
        """运行Blender脚本"""
        import subprocess
        import tempfile

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        script_path = os.path.join(tempfile.gettempdir(), "blender_materials.py")
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(script)

        try:
            result = subprocess.run(
                [self.blender_path, "--background", "--python", script_path],
                capture_output=True, text=True, timeout=120
            )
            if "DONE" in result.stdout or os.path.exists(output_path):
                logger.info(f"材质场景已生成: {output_path}")
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
    """测试材质管理器"""
    mm = MaterialManager()

    # 列出预设
    print(f"可用材质预设 ({len(mm.list_presets())}种):")
    for name in mm.list_presets():
        print(f"  - {name}")

    # 创建材质库场景
    output = r"D:\DobaoWork_Project\Ai_Video_Editor\test_output\material_library.blend"
    success = mm.create_material_library_scene(output)
    print(f"材质库场景: {'成功' if success else '失败'}")

    # 测试单个材质
    output2 = r"D:\DobaoWork_Project\Ai_Video_Editor\test_output\gold_sphere.blend"
    success2 = mm.apply_material_to_object(output2, "SPHERE", "gold")
    print(f"金色球体: {'成功' if success2 else '失败'}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    main()
