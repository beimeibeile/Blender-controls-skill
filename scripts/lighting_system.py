"""
Blender灯光系统模块
- 三点布光预设
- 区域光/点光/聚光灯/平行光
- HDRI环境光照
- 灯光动画
- 灯光强度/颜色/阴影控制
"""

import os
import sys
import logging
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

BLENDER_PATH = r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"


@dataclass
class LightConfig:
    """灯光配置"""
    name: str = "Light"
    light_type: str = "AREA"  # POINT/SUN/SPOT/AREA
    location: Tuple[float, float, float] = (5, -5, 10)
    rotation: Tuple[float, float, float] = (0, 0, 0)
    energy: float = 1000.0
    color: Tuple[float, float, float] = (1.0, 1.0, 1.0)
    size: float = 5.0  # 区域光大小/聚光灯大小
    spot_size: float = 0.785  # 聚光灯角度（弧度）
    spot_blend: float = 0.15
    use_shadow: bool = True
    shadow_soft_size: float = 0.25
    contact_shadow: bool = False


# 三点布光预设
THREE_POINT_LIGHTING = {
    "key": LightConfig(
        name="Key_Light",
        light_type="AREA",
        location=(5, -5, 10),
        rotation=(0.5, 0, 0.5),
        energy=1000,
        color=(1.0, 0.95, 0.9),
        size=5,
    ),
    "fill": LightConfig(
        name="Fill_Light",
        light_type="AREA",
        location=(-5, -5, 5),
        rotation=(0.5, 0, -0.5),
        energy=400,
        color=(0.9, 0.95, 1.0),
        size=4,
    ),
    "rim": LightConfig(
        name="Rim_Light",
        light_type="AREA",
        location=(0, 5, 8),
        rotation=(2.5, 0, 0),
        energy=800,
        color=(1.0, 1.0, 1.0),
        size=3,
    ),
}

# 氛围灯光预设
MOOD_LIGHTING = {
    "warm": LightConfig(
        name="Warm_Light",
        light_type="AREA",
        location=(0, -5, 8),
        rotation=(0.5, 0, 0),
        energy=800,
        color=(1.0, 0.8, 0.5),
        size=8,
    ),
    "cool": LightConfig(
        name="Cool_Light",
        light_type="AREA",
        location=(0, -5, 8),
        rotation=(0.5, 0, 0),
        energy=800,
        color=(0.5, 0.7, 1.0),
        size=8,
    ),
    "dramatic": LightConfig(
        name="Dramatic_Light",
        light_type="SPOT",
        location=(3, -5, 10),
        rotation=(0.8, 0, 0.3),
        energy=2000,
        color=(1.0, 0.95, 0.8),
        spot_size=0.5,
        spot_blend=0.1,
    ),
    "soft": LightConfig(
        name="Soft_Light",
        light_type="AREA",
        location=(0, -8, 6),
        rotation=(0.6, 0, 0),
        energy=500,
        color=(1.0, 1.0, 1.0),
        size=10,
        shadow_soft_size=1.0,
    ),
    "neon": LightConfig(
        name="Neon_Light",
        light_type="POINT",
        location=(0, 0, 3),
        energy=3000,
        color=(0.2, 0.8, 1.0),
    ),
}


class LightingSystem:
    """Blender灯光系统"""

    def __init__(self, blender_path: str = None):
        self.blender_path = blender_path or BLENDER_PATH

    def create_light_script(self, config: LightConfig) -> str:
        """生成创建灯光的Blender脚本"""
        shadow_str = "True" if config.use_shadow else "False"
        contact_str = "True" if config.contact_shadow else "False"

        script = f"""
bpy.ops.object.light_add(type='{config.light_type}', location={config.location})
light = bpy.context.active_object
light.name = "{config.name}"
light.rotation_euler = {config.rotation}
light.data.energy = {config.energy}
light.data.color = ({config.color[0]}, {config.color[1]}, {config.color[2]})
light.data.use_shadow = {shadow_str}
"""

        if config.light_type == "AREA":
            script += f"""
light.data.size = {config.size}
light.data.shadow_soft_size = {config.shadow_soft_size}
"""
        elif config.light_type == "SPOT":
            script += f"""
light.data.spot_size = {config.spot_size}
light.data.spot_blend = {config.spot_blend}
light.data.shadow_soft_size = {config.shadow_soft_size}
"""
        elif config.light_type == "POINT":
            script += f"""
light.data.shadow_soft_size = {config.shadow_soft_size}
"""

        return script

    def create_three_point_lighting(
        self,
        output_path: str,
        target_location: Tuple[float, float, float] = (0, 0, 1),
        intensity_scale: float = 1.0,
    ) -> bool:
        """创建三点布光场景

        Args:
            output_path: 输出路径
            target_location: 目标对象位置
            intensity_scale: 强度缩放

        Returns:
            True成功，False失败
        """
        lights_script = ""
        for key, config in THREE_POINT_LIGHTING.items():
            # 调整位置以面向目标
            config.energy *= intensity_scale
            lights_script += self.create_light_script(config)

        script = f"""
import bpy

# 清除场景
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# 创建三点布光
{lights_script}

# 添加目标对象
bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location={target_location})
target = bpy.context.active_object
target.name = "Target"

# 添加相机
bpy.ops.object.camera_add(location=(0, -8, 4))
camera = bpy.context.active_object
camera.rotation_euler = (1.0, 0, 0)
bpy.context.scene.camera = camera

# 添加地面
bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, 0))
ground = bpy.context.active_object
ground.name = "Ground"

# 保存
bpy.ops.wm.save_as_mainfile(filepath=r'{output_path}')
print("THREE_POINT_DONE")
"""
        return self._run_blender(script, output_path)

    def create_mood_lighting(
        self,
        output_path: str,
        mood: str = "warm",
        add_object: bool = True,
    ) -> bool:
        """创建氛围灯光场景

        Args:
            output_path: 输出路径
            mood: 氛围类型（warm/cool/dramatic/soft/neon）
            add_object: 是否添加测试对象

        Returns:
            True成功，False失败
        """
        config = MOOD_LIGHTING.get(mood, MOOD_LIGHTING["soft"])
        light_script = self.create_light_script(config)

        object_script = ""
        if add_object:
            object_script = """
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 1))
obj = bpy.context.active_object
obj.name = "Test_Object"
"""

        script = f"""
import bpy

# 清除场景
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# 创建氛围灯光
{light_script}

# 添加测试对象
{object_script}

# 添加相机
bpy.ops.object.camera_add(location=(0, -8, 4))
camera = bpy.context.active_object
camera.rotation_euler = (1.0, 0, 0)
bpy.context.scene.camera = camera

# 保存
bpy.ops.wm.save_as_mainfile(filepath=r'{output_path}')
print("MOOD_LIGHTING_DONE")
"""
        return self._run_blender(script, output_path)

    def create_hdri_lighting(
        self,
        output_path: str,
        hdri_path: str = None,
        background_strength: float = 1.0,
    ) -> bool:
        """创建HDRI环境光照场景

        Args:
            output_path: 输出路径
            hdri_path: HDRI文件路径（None则使用程序化天空）
            background_strength: 背景强度

        Returns:
            True成功，False失败
        """
        if hdri_path and os.path.exists(hdri_path):
            env_script = f"""
# 设置HDRI环境贴图
world = bpy.context.scene.world
world.use_nodes = True
env_node = world.node_tree.nodes.new(type='ShaderNodeTexEnvironment')
env_node.image = bpy.data.images.load(r'{hdri_path}')
bg_node = world.node_tree.nodes['Background']
bg_node.inputs['Strength'].default_value = {background_strength}
world.node_tree.links.new(env_node.outputs['Color'], bg_node.inputs['Color'])
"""
        else:
            env_script = f"""
# 使用程序化天空
world = bpy.context.scene.world
world.use_nodes = True
sky_node = world.node_tree.nodes.new(type='ShaderNodeTexSky')
bg_node = world.node_tree.nodes['Background']
bg_node.inputs['Strength'].default_value = {background_strength}
world.node_tree.links.new(sky_node.outputs['Color'], bg_node.inputs['Color'])
"""

        script = f"""
import bpy

# 清除场景
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# 设置环境光照
{env_script}

# 添加测试对象
bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(0, 0, 1))
sphere = bpy.context.active_object
sphere.name = "Test_Sphere"

# 添加相机
bpy.ops.object.camera_add(location=(0, -5, 3))
camera = bpy.context.active_object
camera.rotation_euler = (1.0, 0, 0)
bpy.context.scene.camera = camera

# 添加地面
bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, 0))

# 保存
bpy.ops.wm.save_as_mainfile(filepath=r'{output_path}')
print("HDRI_LIGHTING_DONE")
"""
        return self._run_blender(script, output_path)

    def create_light_animation(
        self,
        output_path: str,
        light_config: LightConfig = None,
        animation_type: str = "intensity",  # intensity/color/move
        duration: int = 60,
    ) -> bool:
        """创建灯光动画

        Args:
            output_path: 输出路径
            light_config: 灯光配置
            animation_type: 动画类型
            duration: 持续帧数

        Returns:
            True成功，False失败
        """
        light_config = light_config or LightConfig()
        light_script = self.create_light_script(light_config)

        if animation_type == "intensity":
            anim_script = f"""
# 灯光强度动画（呼吸效果）
bpy.context.scene.frame_set(1)
light.data.energy = {light_config.energy}
light.keyframe_insert(data_path="data.energy", frame=1)

bpy.context.scene.frame_set({duration // 2})
light.data.energy = {light_config.energy * 2}
light.keyframe_insert(data_path="data.energy", frame={duration // 2})

bpy.context.scene.frame_set({duration})
light.data.energy = {light_config.energy}
light.keyframe_insert(data_path="data.energy", frame={duration})
"""
        elif animation_type == "color":
            anim_script = f"""
# 灯光颜色动画（暖→冷→暖）
bpy.context.scene.frame_set(1)
light.data.color = (1.0, 0.8, 0.5)
light.keyframe_insert(data_path="data.color", frame=1)

bpy.context.scene.frame_set({duration // 2})
light.data.color = (0.5, 0.7, 1.0)
light.keyframe_insert(data_path="data.color", frame={duration // 2})

bpy.context.scene.frame_set({duration})
light.data.color = (1.0, 0.8, 0.5)
light.keyframe_insert(data_path="data.color", frame={duration})
"""
        else:  # move
            anim_script = f"""
# 灯光位移动画
bpy.context.scene.frame_set(1)
light.location = (-5, -5, 10)
light.keyframe_insert(data_path="location", frame=1)

bpy.context.scene.frame_set({duration})
light.location = (5, -5, 10)
light.keyframe_insert(data_path="location", frame={duration})
"""

        script = f"""
import bpy

# 清除场景
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# 创建灯光
{light_script}

# 设置动画时长
bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = {duration}

# 灯光动画
{anim_script}

# 添加测试对象
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 1))

# 添加相机
bpy.ops.object.camera_add(location=(0, -8, 4))
camera = bpy.context.active_object
camera.rotation_euler = (1.0, 0, 0)
bpy.context.scene.camera = camera

# 保存
bpy.ops.wm.save_as_mainfile(filepath=r'{output_path}')
print("LIGHT_ANIMATION_DONE")
"""
        return self._run_blender(script, output_path)

    def list_mood_presets(self) -> List[str]:
        """列出所有氛围灯光预设"""
        return list(MOOD_LIGHTING.keys())

    def _run_blender(self, script: str, output_path: str) -> bool:
        """运行Blender脚本"""
        import subprocess
        import tempfile

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        script_path = os.path.join(tempfile.gettempdir(), "blender_lighting.py")
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(script)

        try:
            result = subprocess.run(
                [self.blender_path, "--background", "--python", script_path],
                capture_output=True, text=True, timeout=120
            )
            if "DONE" in result.stdout or os.path.exists(output_path):
                logger.info(f"灯光场景已生成: {output_path}")
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
    """测试灯光系统"""
    ls = LightingSystem()

    # 列出预设
    print(f"可用氛围灯光 ({len(ls.list_mood_presets())}种):")
    for name in ls.list_mood_presets():
        print(f"  - {name}")

    # 测试三点布光
    output = r"D:\DobaoWork_Project\Ai_Video_Editor\test_output\three_point_lighting.blend"
    success = ls.create_three_point_lighting(output)
    print(f"三点布光: {'成功' if success else '失败'}")

    # 测试氛围灯光
    output2 = r"D:\DobaoWork_Project\Ai_Video_Editor\test_output\warm_lighting.blend"
    success2 = ls.create_mood_lighting(output2, mood="warm")
    print(f"暖光氛围: {'成功' if success2 else '失败'}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    main()
