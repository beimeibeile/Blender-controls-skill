"""
Blender动画工具模块
- 关键帧动画
- 缓动曲线预设
- 约束动画
- 路径动画
- 形变动画
- 动画批量处理
"""

import os
import sys
import logging
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

BLENDER_PATH = r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"


@dataclass
class KeyframeConfig:
    """关键帧配置"""
    property: str = "location"  # location/rotation_euler/scale
    frame: int = 1
    value: Tuple[float, ...] = (0, 0, 0)
    interpolation: str = "BEZIER"  # CONSTANT/LINEAR/BEZIER
    easing: str = "EASE_IN_OUT"  # EASE_IN/EASE_OUT/EASE_IN_OUT/ EASE_IN_OUT


@dataclass
class AnimationConfig:
    """动画配置"""
    name: str = "Animation"
    object_name: str = "Object"
    animation_type: str = "bounce"  # bounce/spin/float/orbit/shake/pulse
    duration: int = 60
    start_frame: int = 1
    amplitude: float = 1.0
    speed: float = 1.0


# 缓动曲线预设
EASING_PRESETS = {
    "linear": {"interpolation": "LINEAR", "easing": "EASE_IN_OUT"},
    "ease_in": {"interpolation": "BEZIER", "easing": "EASE_IN"},
    "ease_out": {"interpolation": "BEZIER", "easing": "EASE_OUT"},
    "ease_in_out": {"interpolation": "BEZIER", "easing": "EASE_IN_OUT"},
    "bounce": {"interpolation": "BEZIER", "easing": "EASE_OUT"},
    "elastic": {"interpolation": "BEZIER", "easing": "EASE_OUT"},
}


class AnimationTools:
    """Blender动画工具"""

    def __init__(self, blender_path: str = None):
        self.blender_path = blender_path or BLENDER_PATH

    def create_bounce_animation(
        self,
        output_path: str,
        object_type: str = "SPHERE",
        bounce_height: float = 3.0,
        duration: int = 60,
        bounce_count: int = 3,
    ) -> bool:
        """创建弹跳动画

        Args:
            output_path: 输出路径
            object_type: 对象类型
            bounce_height: 弹跳高度
            duration: 持续帧数
            bounce_count: 弹跳次数

        Returns:
            True成功，False失败
        """
        script = f"""
import bpy
import math

# 清除场景
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# 创建对象
bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(0, 0, {bounce_height}))
obj = bpy.context.active_object
obj.name = "Bouncing_Ball"

# 添加地面
bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, 0))
ground = bpy.context.active_object
ground.name = "Ground"

# 设置动画
bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = {duration}

# 弹跳关键帧
bounces = {bounce_count}
frames_per_bounce = {duration} // bounces

for i in range(bounces):
    start = i * frames_per_bounce + 1
    mid = start + frames_per_bounce // 2
    end = start + frames_per_bounce

    # 起始高点
    bpy.context.scene.frame_set(start)
    obj.location.z = {bounce_height}
    obj.keyframe_insert(data_path="location", frame=start)

    # 最低点
    bpy.context.scene.frame_set(mid)
    obj.location.z = 1.0
    obj.keyframe_insert(data_path="location", frame=mid)

    # 回到高点
    bpy.context.scene.frame_set(end)
    obj.location.z = {bounce_height}
    obj.keyframe_insert(data_path="location", frame=end)

# 设置缓动曲线
for fcurve in obj.animation_data.action.fcurves:
    for keyframe in fcurve.keyframe_points:
        keyframe.interpolation = 'BEZIER'
        keyframe.easing = 'EASE_IN_OUT'

# 添加相机
bpy.ops.object.camera_add(location=(5, -8, 4))
camera = bpy.context.active_object
camera.rotation_euler = (1.0, 0, 0.6)
bpy.context.scene.camera = camera

# 添加灯光
bpy.ops.object.light_add(type='AREA', location=(5, -5, 10))
light = bpy.context.active_object
light.data.energy = 800

# 保存
bpy.ops.wm.save_as_mainfile(filepath=r'{output_path}')
print("BOUNCE_DONE")
"""
        return self._run_blender(script, output_path)

    def create_spin_animation(
        self,
        output_path: str,
        object_type: str = "CUBE",
        rotation_axis: str = "Z",
        rotations: float = 2.0,
        duration: int = 60,
    ) -> bool:
        """创建旋转动画

        Args:
            output_path: 输出路径
            object_type: 对象类型
            rotation_axis: 旋转轴（X/Y/Z）
            rotations: 旋转圈数
            duration: 持续帧数

        Returns:
            True成功，False失败
        """
        axis_index = {"X": 0, "Y": 1, "Z": 2}[rotation_axis]
        end_rotation = rotations * 6.28318  # 2π

        script = f"""
import bpy

# 清除场景
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# 创建对象
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 1))
obj = bpy.context.active_object
obj.name = "Spinning_Object"

# 设置动画
bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = {duration}

# 起始关键帧
bpy.context.scene.frame_set(1)
obj.rotation_euler[{axis_index}] = 0
obj.keyframe_insert(data_path="rotation_euler", frame=1)

# 结束关键帧
bpy.context.scene.frame_set({duration})
obj.rotation_euler[{axis_index}] = {end_rotation}
obj.keyframe_insert(data_path="rotation_euler", frame={duration})

# 设置线性插值
for fcurve in obj.animation_data.action.fcurves:
    for keyframe in fcurve.keyframe_points:
        keyframe.interpolation = 'LINEAR'

# 添加相机
bpy.ops.object.camera_add(location=(5, -5, 4))
camera = bpy.context.active_object
camera.rotation_euler = (1.0, 0, 0.8)
bpy.context.scene.camera = camera

# 添加灯光
bpy.ops.object.light_add(type='AREA', location=(5, -5, 10))
light = bpy.context.active_object
light.data.energy = 800

# 保存
bpy.ops.wm.save_as_mainfile(filepath=r'{output_path}')
print("SPIN_DONE")
"""
        return self._run_blender(script, output_path)

    def create_float_animation(
        self,
        output_path: str,
        object_type: str = "SPHERE",
        float_height: float = 1.0,
        float_speed: float = 1.0,
        duration: int = 120,
    ) -> bool:
        """创建浮动动画（正弦波）

        Args:
            output_path: 输出路径
            object_type: 对象类型
            float_height: 浮动高度
            float_speed: 浮动速度
            duration: 持续帧数

        Returns:
            True成功，False失败
        """
        script = f"""
import bpy
import math

# 清除场景
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# 创建对象
bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(0, 0, 3))
obj = bpy.context.active_object
obj.name = "Floating_Object"

# 设置动画
bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = {duration}

# 使用驱动实现正弦浮动
# 添加多个关键帧模拟正弦波
num_keyframes = 10
for i in range(num_keyframes + 1):
    frame = 1 + i * ({duration} // num_keyframes)
    t = i / num_keyframes * 2 * math.pi * {float_speed}
    z = 3 + math.sin(t) * {float_height}

    bpy.context.scene.frame_set(frame)
    obj.location.z = z
    obj.keyframe_insert(data_path="location", frame=frame)

# 设置平滑插值
for fcurve in obj.animation_data.action.fcurves:
    for keyframe in fcurve.keyframe_points:
        keyframe.interpolation = 'BEZIER'
        keyframe.easing = 'EASE_IN_OUT'

# 添加相机
bpy.ops.object.camera_add(location=(5, -8, 4))
camera = bpy.context.active_object
camera.rotation_euler = (1.0, 0, 0.6)
bpy.context.scene.camera = camera

# 添加灯光
bpy.ops.object.light_add(type='AREA', location=(5, -5, 10))
light = bpy.context.active_object
light.data.energy = 800

# 保存
bpy.ops.wm.save_as_mainfile(filepath=r'{output_path}')
print("FLOAT_DONE")
"""
        return self._run_blender(script, output_path)

    def create_path_animation(
        self,
        output_path: str,
        object_type: str = "CUBE",
        path_points: List[Tuple[float, float, float]] = None,
        duration: int = 120,
    ) -> bool:
        """创建路径动画

        Args:
            output_path: 输出路径
            object_type: 对象类型
            path_points: 路径点列表
            duration: 持续帧数

        Returns:
            True成功，False失败
        """
        path_points = path_points or [
            (-5, -5, 1), (5, -5, 1), (5, 5, 1), (-5, 5, 1), (-5, -5, 1)
        ]

        # 生成路径点脚本
        points_script = "["
        for p in path_points:
            points_script += f"({p[0]}, {p[1]}, {p[2]}), "
        points_script += "]"

        script = f"""
import bpy

# 清除场景
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# 创建路径曲线
curve = bpy.data.curves.new(name='Path', type='CURVE')
curve.dimensions = '3D'
spline = curve.splines.new(type='NURBS')
spline.use_cyclic_u = True

points = {points_script}
spline.points.add(len(points) - 1)
for i, (x, y, z) in enumerate(points):
    spline.points[i].co = (x, y, z, 1)

path_obj = bpy.data.objects.new('Path', curve)
bpy.context.collection.objects.link(path_obj)

# 创建跟随对象
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 1))
obj = bpy.context.active_object
obj.name = "Path_Follower"

# 添加跟随路径约束
constraint = obj.constraints.new(type='FOLLOW_PATH')
constraint.target = path_obj
constraint.use_curve_follow = True
constraint.forward_axis = 'FORWARD_X'
constraint.up_axis = 'UP_Z'

# 设置动画
bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = {duration}

# 路径动画关键帧
bpy.context.scene.frame_set(1)
constraint.offset_factor = 0
constraint.keyframe_insert(data_path="offset_factor", frame=1)

bpy.context.scene.frame_set({duration})
constraint.offset_factor = 1
constraint.keyframe_insert(data_path="offset_factor", frame={duration})

# 设置线性插值
for fcurve in obj.animation_data.action.fcurves:
    for keyframe in fcurve.keyframe_points:
        keyframe.interpolation = 'LINEAR'

# 添加相机
bpy.ops.object.camera_add(location=(0, -10, 8))
camera = bpy.context.active_object
camera.rotation_euler = (1.1, 0, 0)
bpy.context.scene.camera = camera

# 添加灯光
bpy.ops.object.light_add(type='AREA', location=(5, -5, 10))
light = bpy.context.active_object
light.data.energy = 800

# 保存
bpy.ops.wm.save_as_mainfile(filepath=r'{output_path}')
print("PATH_DONE")
"""
        return self._run_blender(script, output_path)

    def create_shake_animation(
        self,
        output_path: str,
        object_type: str = "CUBE",
        shake_intensity: float = 0.3,
        duration: int = 30,
    ) -> bool:
        """创建震动动画

        Args:
            output_path: 输出路径
            object_type: 对象类型
            shake_intensity: 震动强度
            duration: 持续帧数

        Returns:
            True成功，False失败
        """
        script = f"""
import bpy
import random

# 清除场景
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# 创建对象
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 1))
obj = bpy.context.active_object
obj.name = "Shaking_Object"

# 设置动画
bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = {duration}

# 震动关键帧（每帧随机偏移）
random.seed(42)
for frame in range(1, {duration} + 1):
    bpy.context.scene.frame_set(frame)
    obj.location.x = random.uniform(-{shake_intensity}, {shake_intensity})
    obj.location.y = random.uniform(-{shake_intensity}, {shake_intensity})
    obj.rotation_euler.z = random.uniform(-0.1, 0.1)
    obj.keyframe_insert(data_path="location", frame=frame)
    obj.keyframe_insert(data_path="rotation_euler", frame=frame)

# 添加相机
bpy.ops.object.camera_add(location=(5, -8, 4))
camera = bpy.context.active_object
camera.rotation_euler = (1.0, 0, 0.6)
bpy.context.scene.camera = camera

# 添加灯光
bpy.ops.object.light_add(type='AREA', location=(5, -5, 10))
light = bpy.context.active_object
light.data.energy = 800

# 保存
bpy.ops.wm.save_as_mainfile(filepath=r'{output_path}')
print("SHAKE_DONE")
"""
        return self._run_blender(script, output_path)

    def _run_blender(self, script: str, output_path: str) -> bool:
        """运行Blender脚本"""
        import subprocess
        import tempfile

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        script_path = os.path.join(tempfile.gettempdir(), "blender_animation.py")
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(script)

        try:
            result = subprocess.run(
                [self.blender_path, "--background", "--python", script_path],
                capture_output=True, text=True, timeout=120
            )
            if "DONE" in result.stdout or os.path.exists(output_path):
                logger.info(f"动画场景已生成: {output_path}")
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
    """测试动画工具"""
    tools = AnimationTools()

    # 测试弹跳
    output = r"D:\DobaoWork_Project\Ai_Video_Editor\test_output\bounce_anim.blend"
    success = tools.create_bounce_animation(output, bounce_height=3, bounce_count=3)
    print(f"弹跳动画: {'成功' if success else '失败'}")

    # 测试旋转
    output2 = r"D:\DobaoWork_Project\Ai_Video_Editor\test_output\spin_anim.blend"
    success2 = tools.create_spin_animation(output2, rotations=2)
    print(f"旋转动画: {'成功' if success2 else '失败'}")

    # 测试路径
    output3 = r"D:\DobaoWork_Project\Ai_Video_Editor\test_output\path_anim.blend"
    success3 = tools.create_path_animation(output3)
    print(f"路径动画: {'成功' if success3 else '失败'}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    main()
