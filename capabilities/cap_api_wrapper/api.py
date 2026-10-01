"""
Blender API 统一封装
屏蔽Blender版本差异（4.x/5.x），提供统一接口
"""
import os
import sys
import json
import subprocess
import tempfile
from typing import Dict, List, Optional, Any


class BlenderAPI:
    """Blender API 统一封装"""

    def __init__(self, blender_path: str = None):
        self.blender_path = blender_path or os.environ.get(
            "BLENDER_PATH",
            r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
        )
        self.version = None

    def get_version(self) -> Optional[str]:
        """获取Blender版本"""
        try:
            result = subprocess.run(
                [self.blender_path, "--version"],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                # 解析版本号
                for line in result.stdout.split("\n"):
                    if "Blender" in line:
                        parts = line.split()
                        for part in parts:
                            if "." in part and part[0].isdigit():
                                self.version = part
                                return part
        except Exception as e:
            print(f"❌ 获取Blender版本失败: {e}")
        return None

    def is_available(self) -> bool:
        """检查Blender是否可用"""
        return os.path.exists(self.blender_path)

    def run_script(self, script_content: str, blend_file: str = None,
                   background: bool = True, timeout: int = 300) -> Dict:
        """
        运行Blender Python脚本

        Args:
            script_content: Python脚本内容
            blend_file: .blend文件路径（可选）
            background: 是否后台运行
            timeout: 超时时间（秒）

        Returns:
            运行结果字典
        """
        # 写入临时脚本
        script_path = os.path.join(tempfile.gettempdir(), f"blender_script_{os.getpid()}.py")
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(script_content)

        try:
            cmd = [self.blender_path]
            if background:
                cmd.append("-b")
            if blend_file and os.path.exists(blend_file):
                cmd.append(blend_file)
            cmd.extend(["-P", script_path])

            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=timeout
            )

            return {
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "success": result.returncode == 0,
            }
        except subprocess.TimeoutExpired:
            return {"returncode": -1, "stdout": "", "stderr": "timeout", "success": False}
        except Exception as e:
            return {"returncode": -1, "stdout": "", "stderr": str(e), "success": False}
        finally:
            if os.path.exists(script_path):
                os.remove(script_path)

    def render(self, blend_file: str, output_dir: str = None,
               frame_start: int = 1, frame_end: int = 1,
               engine: str = "BLENDER_EEVEE") -> Dict:
        """
        渲染Blender文件

        Args:
            blend_file: .blend文件路径
            output_dir: 输出目录
            frame_start: 起始帧
            frame_end: 结束帧
            engine: 渲染引擎（BLENDER_EEVEE / CYCLES）

        Returns:
            渲染结果字典
        """
        if not os.path.exists(blend_file):
            return {"success": False, "error": "blend_file not found"}

        if output_dir is None:
            output_dir = os.path.dirname(blend_file)
        os.makedirs(output_dir, exist_ok=True)

        script = f"""
import bpy
import os

# 设置渲染引擎
bpy.context.scene.render.engine = '{engine}'

# 设置输出路径
bpy.context.scene.render.filepath = r'{output_dir}/'

# 设置帧范围
bpy.context.scene.frame_start = {frame_start}
bpy.context.scene.frame_end = {frame_end}

# 渲染
bpy.ops.render.render(animation=True)
print('RENDER_COMPLETE')
"""
        return self.run_script(script, blend_file=blend_file, background=True)

    def get_scene_info(self, blend_file: str) -> Optional[Dict]:
        """获取Blender文件的场景信息"""
        script = """
import bpy
import json

info = {
    "objects": len(bpy.data.objects),
    "meshes": len(bpy.data.meshes),
    "materials": len(bpy.data.materials),
    "textures": len(bpy.data.textures),
    "scenes": len(bpy.data.scenes),
    "frame_start": bpy.context.scene.frame_start,
    "frame_end": bpy.context.scene.frame_end,
    "resolution_x": bpy.context.scene.render.resolution_x,
    "resolution_y": bpy.context.scene.render.resolution_y,
    "fps": bpy.context.scene.render.fps,
    "engine": bpy.context.scene.render.engine,
}
print("SCENE_INFO:" + json.dumps(info))
"""
        result = self.run_script(script, blend_file=blend_file)
        if result["success"]:
            for line in result["stdout"].split("\n"):
                if line.startswith("SCENE_INFO:"):
                    return json.loads(line.replace("SCENE_INFO:", ""))
        return None


if __name__ == "__main__":
    api = BlenderAPI()
    print(f"Blender路径: {api.blender_path}")
    print(f"Blender可用: {'✅' if api.is_available() else '❌'}")
    print(f"Blender版本: {api.get_version()}")
