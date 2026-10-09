"""
Blender批量渲染优化模块
- 渲染队列管理
- 渲染进度跟踪
- 失败重试机制
- 渲染设置预设
- 多格式输出
"""

import os
import sys
import logging
import subprocess
import json
import time
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)

BLENDER_PATH = r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"


class RenderEngine(Enum):
    """渲染引擎"""
    BLENDER_EEVEE = "BLENDER_EEVEE"
    CYCLES = "CYCLES"
    WORKBENCH = "BLENDER_WORKBENCH"


class RenderFormat(Enum):
    """渲染格式"""
    PNG = "PNG"
    JPEG = "JPEG"
    OPEN_EXR = "OPEN_EXR"
    TIFF = "TIFF"
    WEBP = "WEBP"
    FFMPEG = "FFMPEG"


@dataclass
class RenderConfig:
    """渲染配置"""
    engine: RenderEngine = RenderEngine.BLENDER_EEVEE
    resolution_x: int = 1920
    resolution_y: int = 1080
    resolution_percentage: int = 100
    frame_start: int = 1
    frame_end: int = 250
    frame_step: int = 1
    fps: int = 24
    file_format: RenderFormat = RenderFormat.PNG
    color_mode: str = "RGBA"  # BW/RGB/RGBA
    color_depth: str = "8"  # 8/16/32
    compression: int = 15  # 0-100 (PNG)
    quality: int = 90  # 0-100 (JPEG)
    samples: int = 128  # Cycles采样数
    use_denoising: bool = True
    use_transparent: bool = False
    output_path: str = ""
    output_name: str = "render"


@dataclass
class RenderJob:
    """渲染任务"""
    job_id: str = ""
    blend_file: str = ""
    config: RenderConfig = field(default_factory=RenderConfig)
    status: str = "pending"  # pending/running/completed/failed
    progress: float = 0.0
    start_time: float = 0.0
    end_time: float = 0.0
    error_message: str = ""
    output_files: List[str] = field(default_factory=list)
    retry_count: int = 0
    max_retries: int = 3


# 渲染预设
RENDER_PRESETS = {
    "preview": RenderConfig(
        engine=RenderEngine.BLENDER_EEVEE,
        resolution_x=1280, resolution_y=720,
        resolution_percentage=50,
        samples=16,
        use_denoising=False,
        file_format=RenderFormat.JPEG,
        quality=70,
    ),
    "standard": RenderConfig(
        engine=RenderEngine.BLENDER_EEVEE,
        resolution_x=1920, resolution_y=1080,
        resolution_percentage=100,
        samples=64,
        use_denoising=True,
        file_format=RenderFormat.PNG,
        compression=15,
    ),
    "high_quality": RenderConfig(
        engine=RenderEngine.CYCLES,
        resolution_x=1920, resolution_y=1080,
        resolution_percentage=100,
        samples=256,
        use_denoising=True,
        file_format=RenderFormat.PNG,
        compression=10,
    ),
    "cinematic": RenderConfig(
        engine=RenderEngine.CYCLES,
        resolution_x=3840, resolution_y=2160,
        resolution_percentage=100,
        samples=512,
        use_denoising=True,
        file_format=RenderFormat.OPEN_EXR,
        color_depth="32",
    ),
    "transparent": RenderConfig(
        engine=RenderEngine.BLENDER_EEVEE,
        resolution_x=1920, resolution_y=1080,
        resolution_percentage=100,
        samples=64,
        use_transparent=True,
        file_format=RenderFormat.PNG,
        color_mode="RGBA",
        compression=15,
    ),
    "video_mp4": RenderConfig(
        engine=RenderEngine.BLENDER_EEVEE,
        resolution_x=1920, resolution_y=1080,
        resolution_percentage=100,
        samples=64,
        file_format=RenderFormat.FFMPEG,
        fps=30,
    ),
}


class BatchRenderer:
    """Blender批量渲染器"""

    def __init__(self, blender_path: str = None):
        self.blender_path = blender_path or BLENDER_PATH
        self.jobs: List[RenderJob] = []
        self.presets = RENDER_PRESETS

    def add_job(
        self,
        blend_file: str,
        output_dir: str,
        output_name: str = "render",
        preset: str = "standard",
        config: RenderConfig = None,
    ) -> str:
        """添加渲染任务

        Args:
            blend_file: .blend文件路径
            output_dir: 输出目录
            output_name: 输出文件名
            preset: 预设名称
            config: 自定义配置（覆盖预设）

        Returns:
            任务ID
        """
        import uuid
        job_id = uuid.uuid4().hex[:8]

        render_config = config or self.presets.get(preset, RenderConfig())
        render_config.output_path = output_dir
        render_config.output_name = output_name

        job = RenderJob(
            job_id=job_id,
            blend_file=blend_file,
            config=render_config,
        )
        self.jobs.append(job)
        logger.info(f"添加渲染任务: {job_id} ({blend_file})")
        return job_id

    def create_render_script(self, config: RenderConfig, output_path: str) -> str:
        """生成渲染脚本"""
        transparent_str = "True" if config.use_transparent else "False"
        denoising_str = "True" if config.use_denoising else "False"

        return f"""
import bpy
import os

# 设置渲染引擎
bpy.context.scene.render.engine = '{config.engine.value}'

# 设置分辨率
bpy.context.scene.render.resolution_x = {config.resolution_x}
bpy.context.scene.render.resolution_y = {config.resolution_y}
bpy.context.scene.render.resolution_percentage = {config.resolution_percentage}

# 设置帧范围
bpy.context.scene.frame_start = {config.frame_start}
bpy.context.scene.frame_end = {config.frame_end}
bpy.context.scene.frame_step = {config.frame_step}
bpy.context.scene.render.fps = {config.fps}

# 设置输出格式
bpy.context.scene.render.image_settings.file_format = '{config.file_format.value}'
bpy.context.scene.render.image_settings.color_mode = '{config.color_mode}'
bpy.context.scene.render.image_settings.color_depth = '{config.color_depth}'
bpy.context.scene.render.image_settings.compression = {config.compression}
bpy.context.scene.render.image_settings.quality = {config.quality}

# 设置透明背景
bpy.context.scene.render.film_transparent = {transparent_str}

# 设置Cycles参数
if bpy.context.scene.render.engine == 'CYCLES':
    bpy.context.scene.cycles.samples = {config.samples}
    bpy.context.scene.cycles.use_denoising = {denoising_str}
    bpy.context.scene.cycles.device = 'GPU'

# 设置输出路径
os.makedirs(r'{output_path}', exist_ok=True)
bpy.context.scene.render.filepath = os.path.join(r'{output_path}', '{config.output_name}_')

# 执行渲染
bpy.ops.render.render(animation=True)

print("RENDER_COMPLETE")
"""

    def run_job(self, job: RenderJob) -> bool:
        """运行单个渲染任务"""
        job.status = "running"
        job.start_time = time.time()
        job.progress = 0.0

        output_dir = job.config.output_path
        script = self.create_render_script(job.config, output_dir)

        import tempfile
        script_path = os.path.join(tempfile.gettempdir(), f"blender_render_{job.job_id}.py")
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(script)

        try:
            result = subprocess.run(
                [
                    self.blender_path, "--background",
                    job.blend_file,
                    "--python", script_path,
                ],
                capture_output=True, text=True, timeout=3600
            )

            if "RENDER_COMPLETE" in result.stdout:
                job.status = "completed"
                job.progress = 1.0
                job.end_time = time.time()
                # 收集输出文件
                if os.path.exists(output_dir):
                    job.output_files = [
                        os.path.join(output_dir, f)
                        for f in os.listdir(output_dir)
                        if f.startswith(job.config.output_name)
                    ]
                logger.info(f"渲染完成: {job.job_id} ({len(job.output_files)}个文件)")
                return True
            else:
                job.status = "failed"
                job.error_message = result.stderr[-500:]
                logger.error(f"渲染失败: {job.job_id} - {job.error_message}")
                return False

        except subprocess.TimeoutExpired:
            job.status = "failed"
            job.error_message = "渲染超时"
            logger.error(f"渲染超时: {job.job_id}")
            return False
        except Exception as e:
            job.status = "failed"
            job.error_message = str(e)
            logger.error(f"渲染异常: {job.job_id} - {e}")
            return False
        finally:
            if os.path.exists(script_path):
                os.remove(script_path)

    def run_all(self, retry_failed: bool = True) -> Dict[str, Any]:
        """运行所有渲染任务

        Args:
            retry_failed: 是否重试失败任务

        Returns:
            渲染结果统计
        """
        results = {
            "total": len(self.jobs),
            "completed": 0,
            "failed": 0,
            "total_time": 0.0,
            "jobs": [],
        }

        for job in self.jobs:
            if job.status == "completed":
                results["completed"] += 1
                continue

            success = self.run_job(job)

            if not success and retry_failed and job.retry_count < job.max_retries:
                job.retry_count += 1
                logger.info(f"重试渲染 ({job.retry_count}/{job.max_retries}): {job.job_id}")
                success = self.run_job(job)

            if success:
                results["completed"] += 1
            else:
                results["failed"] += 1

            results["jobs"].append({
                "job_id": job.job_id,
                "status": job.status,
                "duration": job.end_time - job.start_time if job.end_time else 0,
                "output_files": len(job.output_files),
                "error": job.error_message,
            })

        results["total_time"] = sum(
            j.end_time - j.start_time for j in self.jobs if j.end_time
        )

        logger.info(f"批量渲染完成: {results['completed']}/{results['total']}成功, "
                    f"{results['failed']}失败, 总耗时{results['total_time']:.1f}秒")
        return results

    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """获取任务状态"""
        for job in self.jobs:
            if job.job_id == job_id:
                return {
                    "job_id": job.job_id,
                    "status": job.status,
                    "progress": job.progress,
                    "blend_file": job.blend_file,
                    "output_files": job.output_files,
                    "error": job.error_message,
                    "retry_count": job.retry_count,
                }
        return None

    def list_presets(self) -> List[str]:
        """列出所有渲染预设"""
        return list(self.presets.keys())

    def save_queue(self, file_path: str):
        """保存渲染队列"""
        data = {
            "jobs": [
                {
                    "job_id": j.job_id,
                    "blend_file": j.blend_file,
                    "status": j.status,
                    "config": asdict(j.config),
                }
                for j in self.jobs
            ]
        }
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_queue(self, file_path: str):
        """加载渲染队列"""
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for job_data in data.get("jobs", []):
            config = RenderConfig(**job_data["config"])
            job = RenderJob(
                job_id=job_data["job_id"],
                blend_file=job_data["blend_file"],
                config=config,
                status=job_data["status"],
            )
            self.jobs.append(job)


def main():
    """测试批量渲染器"""
    renderer = BatchRenderer()

    # 列出预设
    print(f"可用渲染预设 ({len(renderer.list_presets())}种):")
    for name in renderer.list_presets():
        print(f"  - {name}")

    # 添加测试任务
    test_blend = r"D:\DobaoWork_Project\Ai_Video_Editor\test_output\test_scene.blend"
    if os.path.exists(test_blend):
        job_id = renderer.add_job(
            test_blend,
            r"D:\DobaoWork_Project\Ai_Video_Editor\test_output\renders",
            output_name="test",
            preset="preview",
        )
        print(f"添加任务: {job_id}")

        # 运行
        results = renderer.run_all()
        print(f"渲染结果: {results['completed']}/{results['total']}成功")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    main()
