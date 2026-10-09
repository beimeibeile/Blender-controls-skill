"""
Blender程序化纹理生成模块
- 噪声纹理
- 渐变纹理
- 棋盘格纹理
- 木纹纹理
- 大理石纹理
- 纹理节点组管理
"""

import os
import sys
import logging
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

BLENDER_PATH = r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"


@dataclass
class TextureConfig:
    """纹理配置"""
    name: str = "Texture"
    texture_type: str = "noise"  # noise/gradient/checker/wood/marble/voronoi
    scale: float = 5.0
    detail: float = 4.0
    roughness: float = 0.5
    distortion: float = 0.0
    color1: Tuple[float, float, float] = (0.2, 0.2, 0.2)
    color2: Tuple[float, float, float] = (0.8, 0.8, 0.8)
    mapping_type: str = "UV"  # UV/GENERATED/OBJECT


# 纹理预设
TEXTURE_PRESETS = {
    "wood_oak": TextureConfig(
        name="Wood_Oak",
        texture_type="wood",
        scale=10.0,
        detail=8.0,
        color1=(0.4, 0.25, 0.1),
        color2=(0.6, 0.4, 0.2),
    ),
    "wood_walnut": TextureConfig(
        name="Wood_Walnut",
        texture_type="wood",
        scale=8.0,
        detail=10.0,
        color1=(0.2, 0.1, 0.05),
        color2=(0.4, 0.2, 0.1),
    ),
    "marble_white": TextureConfig(
        name="Marble_White",
        texture_type="marble",
        scale=3.0,
        detail=6.0,
        color1=(0.9, 0.9, 0.9),
        color2=(0.5, 0.5, 0.5),
    ),
    "marble_black": TextureConfig(
        name="Marble_Black",
        texture_type="marble",
        scale=4.0,
        detail=8.0,
        color1=(0.1, 0.1, 0.1),
        color2=(0.4, 0.4, 0.4),
    ),
    "noise_rough": TextureConfig(
        name="Noise_Rough",
        texture_type="noise",
        scale=8.0,
        detail=6.0,
        roughness=0.8,
        color1=(0.3, 0.3, 0.3),
        color2=(0.7, 0.7, 0.7),
    ),
    "checker_classic": TextureConfig(
        name="Checker_Classic",
        texture_type="checker",
        scale=2.0,
        color1=(0.1, 0.1, 0.1),
        color2=(0.9, 0.9, 0.9),
    ),
    "gradient_sunset": TextureConfig(
        name="Gradient_Sunset",
        texture_type="gradient",
        scale=1.0,
        color1=(1.0, 0.4, 0.2),
        color2=(0.8, 0.2, 0.6),
    ),
    "voronoi_cells": TextureConfig(
        name="Voronoi_Cells",
        texture_type="voronoi",
        scale=5.0,
        detail=4.0,
        color1=(0.2, 0.4, 0.8),
        color2=(0.8, 0.6, 0.2),
    ),
}


class TextureGenerator:
    """Blender程序化纹理生成器"""

    def __init__(self, blender_path: str = None):
        self.blender_path = blender_path or BLENDER_PATH
        self.presets = TEXTURE_PRESETS

    def create_noise_texture_script(self, config: TextureConfig) -> str:
        """生成噪声纹理节点脚本"""
        return f"""
# 噪声纹理
noise_node = nodes.new(type='ShaderNodeTexNoise')
noise_node.location = (-400, 0)
noise_node.inputs['Scale'].default_value = {config.scale}
noise_node.inputs['Detail'].default_value = {config.detail}
noise_node.inputs['Roughness'].default_value = {config.roughness}
noise_node.inputs['Distortion'].default_value = {config.distortion}

# 颜色渐变
ramp_node = nodes.new(type='ShaderNodeValToRGB')
ramp_node.location = (-200, 0)
ramp_node.color_ramp.elements[0].position = 0.0
ramp_node.color_ramp.elements[0].color = ({config.color1[0]}, {config.color1[1]}, {config.color1[2]}, 1.0)
ramp_node.color_ramp.elements[1].position = 1.0
ramp_node.color_ramp.elements[1].color = ({config.color2[0]}, {config.color2[1]}, {config.color2[2]}, 1.0)

links.new(noise_node.outputs['Fac'], ramp_node.inputs['Fac'])
texture_output = ramp_node.outputs['Color']
"""

    def create_checker_texture_script(self, config: TextureConfig) -> str:
        """生成棋盘格纹理节点脚本"""
        return f"""
# 棋盘格纹理
checker_node = nodes.new(type='ShaderNodeTexChecker')
checker_node.location = (-400, 0)
checker_node.inputs['Scale'].default_value = {config.scale}
checker_node.inputs['Color1'].default_value = ({config.color1[0]}, {config.color1[1]}, {config.color1[2]}, 1.0)
checker_node.inputs['Color2'].default_value = ({config.color2[0]}, {config.color2[1]}, {config.color2[2]}, 1.0)
texture_output = checker_node.outputs['Color']
"""

    def create_gradient_texture_script(self, config: TextureConfig) -> str:
        """生成渐变纹理节点脚本"""
        return f"""
# 渐变纹理
gradient_node = nodes.new(type='ShaderNodeTexGradient')
gradient_node.location = (-400, 0)

# 颜色渐变
ramp_node = nodes.new(type='ShaderNodeValToRGB')
ramp_node.location = (-200, 0)
ramp_node.color_ramp.elements[0].position = 0.0
ramp_node.color_ramp.elements[0].color = ({config.color1[0]}, {config.color1[1]}, {config.color1[2]}, 1.0)
ramp_node.color_ramp.elements[1].position = 1.0
ramp_node.color_ramp.elements[1].color = ({config.color2[0]}, {config.color2[1]}, {config.color2[2]}, 1.0)

links.new(gradient_node.outputs['Color'], ramp_node.inputs['Fac'])
texture_output = ramp_node.outputs['Color']
"""

    def create_wood_texture_script(self, config: TextureConfig) -> str:
        """生成木纹纹理节点脚本"""
        return f"""
# 木纹纹理（使用Wave纹理+Noise扰动）
wave_node = nodes.new(type='ShaderNodeTexWave')
wave_node.location = (-600, 0)
wave_node.inputs['Scale'].default_value = {config.scale}
wave_node.inputs['Distortion'].default_value = 3.0
wave_node.bands_direction = 'Y'

noise_node = nodes.new(type='ShaderNodeTexNoise')
noise_node.location = (-600, -200)
noise_node.inputs['Scale'].default_value = {config.scale * 2}
noise_node.inputs['Detail'].default_value = {config.detail}

# 混合
mix_node = nodes.new(type='ShaderNodeMixRGB')
mix_node.location = (-400, 0)
mix_node.blend_type = 'OVERLAY'
mix_node.inputs['Fac'].default_value = 0.3

links.new(wave_node.outputs['Color'], mix_node.inputs[1])
links.new(noise_node.outputs['Color'], mix_node.inputs[2])

# 颜色渐变
ramp_node = nodes.new(type='ShaderNodeValToRGB')
ramp_node.location = (-200, 0)
ramp_node.color_ramp.elements[0].position = 0.0
ramp_node.color_ramp.elements[0].color = ({config.color1[0]}, {config.color1[1]}, {config.color1[2]}, 1.0)
ramp_node.color_ramp.elements[1].position = 1.0
ramp_node.color_ramp.elements[1].color = ({config.color2[0]}, {config.color2[1]}, {config.color2[2]}, 1.0)

links.new(mix_node.outputs['Color'], ramp_node.inputs['Fac'])
texture_output = ramp_node.outputs['Color']
"""

    def create_marble_texture_script(self, config: TextureConfig) -> str:
        """生成大理石纹理节点脚本"""
        return f"""
# 大理石纹理（Noise+ColorRamp）
noise_node = nodes.new(type='ShaderNodeTexNoise')
noise_node.location = (-600, 0)
noise_node.inputs['Scale'].default_value = {config.scale}
noise_node.inputs['Detail'].default_value = {config.detail}
noise_node.inputs['Distortion'].default_value = 5.0

# 颜色渐变（大理石纹理特征）
ramp_node = nodes.new(type='ShaderNodeValToRGB')
ramp_node.location = (-400, 0)
ramp_node.color_ramp.elements[0].position = 0.0
ramp_node.color_ramp.elements[0].color = ({config.color1[0]}, {config.color1[1]}, {config.color1[2]}, 1.0)
ramp_node.color_ramp.elements[1].position = 0.3
ramp_node.color_ramp.elements[1].color = ({config.color1[0]}, {config.color1[1]}, {config.color1[2]}, 1.0)
ramp_node.color_ramp.elements.new(0.35)
ramp_node.color_ramp.elements[2].color = ({config.color2[0]}, {config.color2[1]}, {config.color2[2]}, 1.0)
ramp_node.color_ramp.elements.new(0.4)
ramp_node.color_ramp.elements[3].color = ({config.color1[0]}, {config.color1[1]}, {config.color1[2]}, 1.0)
ramp_node.color_ramp.elements[1].position = 1.0

links.new(noise_node.outputs['Fac'], ramp_node.inputs['Fac'])
texture_output = ramp_node.outputs['Color']
"""

    def create_voronoi_texture_script(self, config: TextureConfig) -> str:
        """生成Voronoi纹理节点脚本"""
        return f"""
# Voronoi纹理
voronoi_node = nodes.new(type='ShaderNodeTexVoronoi')
voronoi_node.location = (-400, 0)
voronoi_node.inputs['Scale'].default_value = {config.scale}
voronoi_node.inputs['Detail'].default_value = {config.detail}
voronoi_node.feature = 'DISTANCE_TO_EDGE'

# 颜色渐变
ramp_node = nodes.new(type='ShaderNodeValToRGB')
ramp_node.location = (-200, 0)
ramp_node.color_ramp.elements[0].position = 0.0
ramp_node.color_ramp.elements[0].color = ({config.color1[0]}, {config.color1[1]}, {config.color1[2]}, 1.0)
ramp_node.color_ramp.elements[1].position = 1.0
ramp_node.color_ramp.elements[1].color = ({config.color2[0]}, {config.color2[1]}, {config.color2[2]}, 1.0)

links.new(voronoi_node.outputs['Distance'], ramp_node.inputs['Fac'])
texture_output = ramp_node.outputs['Color']
"""

    def create_textured_material(
        self,
        output_path: str,
        texture_config: TextureConfig = None,
        preset_name: str = None,
        object_type: str = "CUBE",
    ) -> bool:
        """创建带程序化纹理的材质场景

        Args:
            output_path: 输出路径
            texture_config: 纹理配置
            preset_name: 预设名称
            object_type: 测试对象类型

        Returns:
            True成功，False失败
        """
        if preset_name and preset_name in self.presets:
            texture_config = self.presets[preset_name]
        texture_config = texture_config or TextureConfig()

        # 根据纹理类型选择生成脚本
        texture_type = texture_config.texture_type
        if texture_type == "noise":
            texture_script = self.create_noise_texture_script(texture_config)
        elif texture_type == "checker":
            texture_script = self.create_checker_texture_script(texture_config)
        elif texture_type == "gradient":
            texture_script = self.create_gradient_texture_script(texture_config)
        elif texture_type == "wood":
            texture_script = self.create_wood_texture_script(texture_config)
        elif texture_type == "marble":
            texture_script = self.create_marble_texture_script(texture_config)
        elif texture_type == "voronoi":
            texture_script = self.create_voronoi_texture_script(texture_config)
        else:
            texture_script = self.create_noise_texture_script(texture_config)

        if object_type == "SPHERE":
            create_obj = "bpy.ops.mesh.primitive_uv_sphere_add(radius=1.5, location=(0, 0, 1.5))"
        elif object_type == "CYLINDER":
            create_obj = "bpy.ops.mesh.primitive_cylinder_add(radius=1.5, depth=3, location=(0, 0, 1.5))"
        else:
            create_obj = "bpy.ops.mesh.primitive_cube_add(size=2.5, location=(0, 0, 1.25))"

        script = f"""
import bpy

# 清除场景
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# 创建材质
mat = bpy.data.materials.new(name="{texture_config.name}")
mat.use_nodes = True
nodes = mat.node_tree.nodes
links = mat.node_tree.links

# 清除默认节点
for node in nodes:
    nodes.remove(node)

# 创建纹理节点
{texture_script}

# 创建Principled BSDF
bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
bsdf.location = (200, 0)
links.new(texture_output, bsdf.inputs['Base Color'])

# 创建输出节点
output = nodes.new(type='ShaderNodeOutputMaterial')
output.location = (400, 0)
links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

# 创建测试对象
{create_obj}
obj = bpy.context.active_object
obj.name = "Textured_Object"
obj.data.materials.append(mat)

# 添加地面
bpy.ops.mesh.primitive_plane_add(size=10, location=(0, 0, 0))
ground = bpy.context.active_object
ground.name = "Ground"

# 添加相机
bpy.ops.object.camera_add(location=(4, -6, 4))
camera = bpy.context.active_object
camera.rotation_euler = (1.0, 0, 0.6)
bpy.context.scene.camera = camera

# 添加灯光
bpy.ops.object.light_add(type='AREA', location=(5, -5, 10))
light = bpy.context.active_object
light.data.energy = 1000
light.data.size = 8

# 保存
bpy.ops.wm.save_as_mainfile(filepath=r'{output_path}')
print("TEXTURE_DONE")
"""
        return self._run_blender(script, output_path)

    def create_texture_library(
        self,
        output_dir: str,
        preset_names: List[str] = None,
    ) -> Dict[str, bool]:
        """批量创建纹理材质库

        Args:
            output_dir: 输出目录
            preset_names: 预设名称列表（None表示全部）

        Returns:
            结果字典 {preset_name: success}
        """
        preset_names = preset_names or list(self.presets.keys())
        results = {}

        for name in preset_names:
            if name not in self.presets:
                results[name] = False
                continue
            output_path = os.path.join(output_dir, f"texture_{name}.blend")
            success = self.create_textured_material(output_path, preset_name=name)
            results[name] = success
            logger.info(f"纹理 {name}: {'成功' if success else '失败'}")

        return results

    def list_presets(self) -> List[str]:
        """列出所有纹理预设"""
        return list(self.presets.keys())

    def _run_blender(self, script: str, output_path: str) -> bool:
        """运行Blender脚本"""
        import subprocess
        import tempfile

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        script_path = os.path.join(tempfile.gettempdir(), "blender_texture.py")
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(script)

        try:
            result = subprocess.run(
                [self.blender_path, "--background", "--python", script_path],
                capture_output=True, text=True, timeout=120
            )
            if "TEXTURE_DONE" in result.stdout or os.path.exists(output_path):
                logger.info(f"纹理场景已生成: {output_path}")
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
    """测试纹理生成器"""
    gen = TextureGenerator()

    # 列出预设
    print(f"可用纹理预设 ({len(gen.list_presets())}种):")
    for name in gen.list_presets():
        print(f"  - {name}")

    # 测试木纹
    output = r"D:\DobaoWork_Project\Ai_Video_Editor\test_output\texture_wood.blend"
    success = gen.create_textured_material(output, preset_name="wood_oak")
    print(f"木纹纹理: {'成功' if success else '失败'}")

    # 测试大理石
    output2 = r"D:\DobaoWork_Project\Ai_Video_Editor\test_output\texture_marble.blend"
    success2 = gen.create_textured_material(output2, preset_name="marble_white")
    print(f"大理石纹理: {'成功' if success2 else '失败'}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    main()
