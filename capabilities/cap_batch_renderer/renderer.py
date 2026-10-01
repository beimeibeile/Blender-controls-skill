"""
批量渲染器
批量渲染、队列管理、进度监控、结果归档
"""
import os
import time
from typing import Dict, List, Optional, Callable


class BatchRenderer:
    """批量渲染器"""

    def __init__(self, output_dir: str = None, api=None):
        self.output_dir = output_dir or os.environ.get("DEFAULT_OUTPUT_DIR", "./output")
        os.makedirs(self.output_dir, exist_ok=True)
        self.api = api
        self._queue = []
        self._results = {"success": [], "failed": [], "pending": []}

    def _get_api(self):
        if self.api is None:
            from cap_api_wrapper import BlenderAPI
            self.api = BlenderAPI()
        return self.api

    def render_batch(self, blend_files: List[str], output_dir: str = None,
                     quality_check: bool = False,
                     on_progress: Callable = None) -> Dict:
        """
        批量渲染

        Args:
            blend_files: .blend文件路径列表
            output_dir: 输出目录
            quality_check: 是否启用质量检查
            on_progress: 进度回调函数

        Returns:
            渲染结果字典
        """
        out_dir = output_dir or self.output_dir
        os.makedirs(out_dir, exist_ok=True)

        api = self._get_api()
        results = {"success": [], "failed": [], "total": len(blend_files)}

        for i, blend_file in enumerate(blend_files):
            try:
                result = api.render(blend_file, output_dir=out_dir)
                if result.get("success"):
                    results["success"].append({"index": i, "file": blend_file})
                else:
                    results["failed"].append({"index": i, "file": blend_file, "error": result.get("stderr", "")})
            except Exception as e:
                results["failed"].append({"index": i, "file": blend_file, "error": str(e)})

            if on_progress:
                on_progress(i + 1, len(blend_files), results)

        return results

    def render_scenes(self, scene_names: List[str], output_dir: str = None,
                      params: Dict = None, on_progress: Callable = None) -> Dict:
        """
        批量渲染场景模板

        Args:
            scene_names: 场景模板名称列表
            output_dir: 输出根目录
            params: 统一覆盖参数
            on_progress: 进度回调函数 (current, total, results)

        Returns:
            渲染结果字典
        """
        from cap_scene_manager import SceneManager
        sm = SceneManager()

        out_dir = output_dir or self.output_dir
        results = {"success": [], "failed": [], "total": len(scene_names), "output_dir": out_dir}

        for i, scene_name in enumerate(scene_names):
            try:
                scene_out = os.path.join(out_dir, scene_name)
                result = sm.run(scene_name, params=params, output_dir=scene_out)
                if result and result.get("status") == "success":
                    results["success"].append({
                        "index": i,
                        "scene": scene_name,
                        "output_dir": scene_out,
                        "frames": result.get("frames", 0),
                    })
                else:
                    results["failed"].append({
                        "index": i,
                        "scene": scene_name,
                        "error": result.get("error", "render_failed") if result else "not_found",
                    })
            except Exception as e:
                results["failed"].append({"index": i, "scene": scene_name, "error": str(e)})

            if on_progress:
                on_progress(i + 1, len(scene_names), results)

        return results

    def render_with_quality_check(self, blend_files: List[str], output_dir: str = None,
                                   quality_threshold: float = 0.7,
                                   max_retries: int = 2,
                                   on_progress: Callable = None) -> Dict:
        """
        带质量检查的批量渲染（不合格自动重渲染）

        Args:
            blend_files: .blend文件列表
            output_dir: 输出目录
            quality_threshold: 质量阈值
            max_retries: 最大重试次数
            on_progress: 进度回调

        Returns:
            渲染+质检结果
        """
        from cap_quality_control import QualityController
        qc = QualityController(quality_threshold=quality_threshold)

        out_dir = output_dir or self.output_dir
        api = self._get_api()
        results = {"success": [], "failed": [], "retried": [], "total": len(blend_files)}

        for i, blend_file in enumerate(blend_files):
            file_out = os.path.join(out_dir, os.path.splitext(os.path.basename(blend_file))[0])
            attempt = 0
            passed = False

            while attempt <= max_retries and not passed:
                render_result = api.render(blend_file, output_dir=file_out)
                if not render_result.get("success"):
                    attempt += 1
                    continue

                # 质量检查
                output_files = [os.path.join(file_out, f) for f in os.listdir(file_out)
                                if f.endswith(('.png', '.jpg', '.mp4'))] if os.path.exists(file_out) else []
                if output_files:
                    qc_result = qc.check_render(output_files[0])
                    passed = qc_result.get("passed", False)

                if not passed and attempt < max_retries:
                    results["retried"].append({"file": blend_file, "attempt": attempt + 1})
                attempt += 1

            if passed:
                results["success"].append({"index": i, "file": blend_file, "attempts": attempt})
            else:
                results["failed"].append({"index": i, "file": blend_file, "attempts": attempt})

            if on_progress:
                on_progress(i + 1, len(blend_files), results)

        return results

    def get_queue_status(self) -> Dict:
        """获取队列状态"""
        return {
            "queue_size": len(self._queue),
            "results": self._results,
        }


if __name__ == "__main__":
    br = BatchRenderer()
    print(f"输出目录: {br.output_dir}")
    print(f"API可用: {'✅' if br._get_api().is_available() else '❌'}")
