"""
Blender相机与运镜系统模块
- 多机位管理
- 运镜路径动画
- 景深控制
- 相机切换
- 运镜预设（推拉摇移跟升降）
"""

import os
import sys
import logging
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

BLENDER_PATH = r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"


@dataclass
class CameraConfig:
    """相机配置"""
    name: str = "Camera"
    location: Tuple[float, float, float] = (0, -10, 5)
    rotation: Tuple[float, float, float] = (1.1, 0, 0)
    focal_length: float = 50.0  # mm
    sensor_width: float = 36.0  # mm
    aperture_fstop: float = 2.8  # 景深
    focus_distance: float = 10.0
    use_dof: bool = False
    clip_start: float = 0.1
    clip_end: float = 1000.0


@dataclass
class CameraMoveConfig:
    """运镜配置"""
    move_type: str = "static"  # static/pan/tilt/dolly/track/pedestal/crane/zoom/orbit
    start_location: Tuple[float, float, float] = (0, -10, 5)
    end_location: Tuple[float, float, float] = (0, -10, 5)
    start_rotation: Tuple[float, float, float] = (1.1, 0, 0)
    end_rotation: Tuple[float, float, float] = (1.1, 0, 0)
    duration: int = 60  # 帧数
    start_frame: int = 1
    easing: str = "LINEAR"  # LINEAR/BEZIER/EASE_IN/EASE_OUT/EASE_IN_OUT


# 运镜预设
CAMERA_MOVE_PRESETS = {
    "push_in": CameraMoveConfig(
        move_type="dolly",
        start_location=(0, -15, 5),
        end_location=(0, -5, 5),
        start_rotation=(1.1, 0, 0),
        end_rotation=(1.1, 0, 0),
        duration=60,
        easing="EASE_IN_OUT",
    ),
    "pull_out": CameraMoveConfig(
        move_type="dolly",
        start_location=(0, -5, 5),
        end_location=(0, -15, 5),
        start_rotation=(1.1, 0, 0),
        end_rotation=(1.1, 0, 0),
        duration=60,
        easing="EASE_IN_OUT",
    ),
    "pan_left": CameraMoveConfig(
        move_type="pan",
        start_location=(0, -10, 5),
        end_location=(0, -10, 5),
        start_rotation=(1.1, 0, 0),
        end_rotation=(1.1, 0, 0.5),
        duration=60,
        easing="LINEAR",
    ),
    "pan_right": CameraMoveConfig(
        move_type="pan",
        start_location=(0, -10, 5),
        end_location=(0, -10, 5),
        start_rotation=(1.1, 0, 0),
        end_rotation=(1.1, 0, -0.5),
        duration=60,
        easing="LINEAR",
    ),
    "tilt_up": CameraMoveConfig(
        move_type="tilt",
        start_location=(0, -10, 5),
        end_location=(0, -10, 5),
        start_rotation=(1.3, 0, 0),
        end_rotation=(0.9, 0, 0),
        duration=60,
        easing="EASE_IN_OUT",
    ),
    "tilt_down": CameraMoveConfig(
        move_type="tilt",
        start_location=(0, -10, 5),
        end_location=(0, -10, 5),
        start_rotation=(0.9, 0, 0),
        end_rotation=(1.3, 0, 0),
        duration=60,
        easing="EASE_IN_OUT",
    ),
    "track_left": CameraMoveConfig(
        move_type="track",
        start_location=(5, -10, 5),
        end_location=(-5, -10, 5),
        start_rotation=(1.1, 0, 0),
        end_rotation=(1.1, 0, 0),
        duration=60,
        easing="LINEAR",
    ),
    "track_right": CameraMoveConfig(
        move_type="track",
        start_location=(-5, -10, 5),
        end_location=(5, -10, 5),
        start_rotation=(1.1, 0, 0),
        end_rotation=(1.1, 0, 0),
        duration=60,
        easing="LINEAR",
    ),
    "crane_up": CameraMoveConfig(
        move_type="crane",
        start_location=(0, -10, 2),
        end_location=(0, -10, 10),
        start_rotation=(1.1, 0, 0),
        end_rotation=(1.4, 0, 0),
        duration=60,
        easing="EASE_IN_OUT",
    ),
    "crane_down": CameraMoveConfig(
        move_type="crane",
        start_location=(0, -10, 10),
        end_location=(0, -10, 2),
        start_rotation=(1.4, 0, 0),
        end_rotation=(1.1, 0, 0),
        duration=60,
        easing="EASE_IN_OUT",
    ),
    "orbit": CameraMoveConfig(
        move_type="orbit",
        start_location=(10, 0, 5),
        end_location=(-10, 0, 5),
        start_rotation=(1.1, 0, 1.57),
        end_rotation=(1.1, 0, -1.57),
        duration=120,
        easing="LINEAR",
    ),
    "zoom_in": CameraMoveConfig(
        move_type="zoom",
        start_location=(0, -10, 5),
        end_location=(0, -10, 5),
        start_rotation=(1.1, 0, 0),
        end_rotation=(1.1, 0, 0),
        duration=60,
        easing="EASE_IN_OUT",
    ),
}


class CameraSystem:
    """Blender相机与运镜系统"""

    def __init__(self, blender_path: str = None):
        self.blender_path = blender_path or BLENDER_PATH
        self.presets = CAMERA_MOVE_PRESETS

    def create_camera_script(self, config: CameraConfig) -> str:
        """生成创建相机的Blender脚本"""
        return f"""
bpy.ops.object.camera_add(location={config.location})
camera = bpy.context.active_object
camera.name = "{config.name}"
camera.rotation_euler = {config.rotation}
camera.data.lens = {config.focal_length}
camera.data.sensor_width = {config.sensor_width}
camera.data.dof.use_dof = {config.use_dof}
camera.data.dof.aperture_fstop = {config.aperture_fstop}
camera.data.dof.focus_distance = {config.focus_distance}
camera.data.clip_start = {config.clip_start}
camera.data.clip_end = {config.clip_end}
bpy.context.scene.camera = camera
"""

    def create_camera_move_animation(
        self,
        output_path: str,
        move_config: CameraMoveConfig = None,
        preset_name: str = None,
        camera_config: CameraConfig = None,
    ) -> bool:
        """创建相机运镜动画

        Args:
            output_path: 输出路径
            move_config: 运镜配置（与preset_name二选一）
            preset_name: 预设名称
            camera_config: 相机配置

        Returns:
            True成功，False失败
        """
        if preset_name and preset_name in self.presets:
            move_config = self.presets[preset_name]
        move_config = move_config or CameraMoveConfig()
        camera_config = camera_config or CameraConfig()

        # 缩放动画特殊处理
        is_zoom = move_config.move_type == "zoom"

        script = f"""
import bpy

# 清除场景
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# 创建相机
{self.create_camera_script(camera_config)}
camera = bpy.context.scene.camera

# 设置动画时长
bpy.context.scene.frame_start = {move_config.start_frame}
bpy.context.scene.frame_end = {move_config.start_frame + move_config.duration}

# 起始关键帧
bpy.context.scene.frame_set({move_config.start_frame})
camera.location = {move_config.start_location}
camera.rotation_euler = {move_config.start_rotation}
camera.keyframe_insert(data_path="location", frame={move_config.start_frame})
camera.keyframe_insert(data_path="rotation_euler", frame={move_config.start_frame})
"""

        if is_zoom:
            script += f"""
camera.data.lens = 35.0
camera.data.keyframe_insert(data_path="lens", frame={move_config.start_frame})
"""

        script += f"""
# 结束关键帧
bpy.context.scene.frame_set({move_config.start_frame + move_config.duration})
camera.location = {move_config.end_location}
camera.rotation_euler = {move_config.end_rotation}
camera.keyframe_insert(data_path="location", frame={move_config.start_frame + move_config.duration})
camera.keyframe_insert(data_path="rotation_euler", frame={move_config.start_frame + move_config.duration})
"""

        if is_zoom:
            script += f"""
camera.data.lens = 85.0
camera.data.keyframe_insert(data_path="lens", frame={move_config.start_frame + move_config.duration})
"""

        script += f"""
# 设置缓动曲线
for fcurve in camera.animation_data.action.fcurves:
    for keyframe in fcurve.keyframe_points:
        keyframe.interpolation = '{move_config.easing}'
        if '{move_config.easing}' == 'EASE_IN_OUT':
            keyframe.easing = 'EASE_IN_OUT'

# 添加测试对象（立方体）
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 1))
cube = bpy.context.active_object
cube.name = "Test_Object"

# 添加灯光
bpy.ops.object.light_add(type='AREA', location=(5, -5, 10))
light = bpy.context.active_object
light.data.energy = 500

# 保存
bpy.ops.wm.save_as_mainfile(filepath=r'{output_path}')
print("CAMERA_MOVE_DONE")
"""
        return self._run_blender(script, output_path)

    def create_multi_camera_scene(
        self,
        output_path: str,
        cameras: List[CameraConfig] = None,
        switch_frames: List[int] = None,
    ) -> bool:
        """创建多机位场景

        Args:
            output_path: 输出路径
            cameras: 相机配置列表
            switch_frames: 切换帧列表

        Returns:
            True成功，False失败
        """
        cameras = cameras or [
            CameraConfig(name="Camera_Front", location=(0, -10, 5), rotation=(1.1, 0, 0)),
            CameraConfig(name="Camera_Left", location=(-10, 0, 5), rotation=(1.1, 0, 1.57)),
            CameraConfig(name="Camera_Top", location=(0, 0, 15), rotation=(0, 0, 0)),
        ]
        switch_frames = switch_frames or [1, 50, 100]

        cameras_script = ""
        for i, cam in enumerate(cameras):
            cameras_script += self.create_camera_script(cam)
            cameras_script += f"camera_{i} = bpy.data.objects['{cam.name}']\n"

        # 相机动画切换脚本
        switch_script = ""
        for i, frame in enumerate(switch_frames):
            cam_idx = i % len(cameras)
            switch_script += f"""
bpy.context.scene.frame_set({frame})
bpy.context.scene.camera = camera_{cam_idx}
bpy.context.scene.keyframe_insert(data_path="camera", frame={frame})
"""

        script = f"""
import bpy

# 清除场景
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# 创建多个相机
{cameras_script}

# 设置动画时长
bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = {switch_frames[-1] + 50 if switch_frames else 150}

# 相机切换动画
{switch_script}

# 添加测试对象
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 1))
bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(3, 0, 1))

# 添加灯光
bpy.ops.object.light_add(type='AREA', location=(0, -5, 10))
light = bpy.context.active_object
light.data.energy = 500

# 保存
bpy.ops.wm.save_as_mainfile(filepath=r'{output_path}')
print("MULTI_CAMERA_DONE")
"""
        return self._run_blender(script, output_path)

    def list_presets(self) -> List[str]:
        """列出所有运镜预设"""
        return list(self.presets.keys())

    def _run_blender(self, script: str, output_path: str) -> bool:
        """运行Blender脚本"""
        import subprocess
        import tempfile

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        script_path = os.path.join(tempfile.gettempdir(), "blender_camera.py")
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(script)

        try:
            result = subprocess.run(
                [self.blender_path, "--background", "--python", script_path],
                capture_output=True, text=True, timeout=120
            )
            if "DONE" in result.stdout or os.path.exists(output_path):
                logger.info(f"相机场景已生成: {output_path}")
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
    """测试相机系统"""
    cs = CameraSystem()

    # 列出预设
    print(f"可用运镜预设 ({len(cs.list_presets())}种):")
    for name in cs.list_presets():
        print(f"  - {name}")

    # 测试推镜
    output = r"D:\DobaoWork_Project\Ai_Video_Editor\test_output\camera_push_in.blend"
    success = cs.create_camera_move_animation(output, preset_name="push_in")
    print(f"推镜动画: {'成功' if success else '失败'}")

    # 测试多机位
    output2 = r"D:\DobaoWork_Project\Ai_Video_Editor\test_output\multi_camera.blend"
    success2 = cs.create_multi_camera_scene(output2)
    print(f"多机位场景: {'成功' if success2 else '失败'}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    main()
