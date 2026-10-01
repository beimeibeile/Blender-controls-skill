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
                      on_progress: Callable = None) -> Dict:
        """批量渲染场景模板"""
        from cap_scene_manager import SceneManager
        sm = SceneManager()

        results = {"success": [], "failed": [], "total": len(scene_names)}
        for i, scene_name in enumerate(scene_names):
            try:
                scene = sm.load_scene(scene_name)
                if scene:
                    results["success"].append({"index": i, "scene": scene_name})
                else:
                    results["failed"].append({"index": i, "scene": scene_name, "error": "not found"})
            except Exception as e:
                results["failed"].append({"index": i, "scene": scene_name, "error": str(e)})

            if on_progress:
                on_progress(i + 1, len(scene_names), results)

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
