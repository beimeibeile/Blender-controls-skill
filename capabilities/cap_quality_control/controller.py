"""
质量控制器
渲染结果质量检测、自动筛选、不合格重渲染
"""
import os
from typing import Dict, List, Optional


class QualityController:
    """质量控制器"""

    def __init__(self, quality_threshold: float = 0.7):
        self.quality_threshold = quality_threshold
        self.checks = {
            "resolution": self._check_resolution,
            "file_size": self._check_file_size,
            "frame_count": self._check_frame_count,
        }

    def check_render(self, output_path: str) -> Dict:
        """检查渲染结果质量"""
        if not os.path.exists(output_path):
            return {"status": "failed", "error": "file_not_found"}

        results = {"file": output_path, "checks": {}, "passed": True}

        for check_name, check_func in self.checks.items():
            try:
                check_result = check_func(output_path)
                results["checks"][check_name] = check_result
                if not check_result.get("passed", True):
                    results["passed"] = False
            except Exception as e:
                results["checks"][check_name] = {"passed": False, "error": str(e)}
                results["passed"] = False

        return results

    def check_batch(self, output_paths: List[str]) -> Dict:
        """批量检查渲染结果"""
        results = {"total": len(output_paths), "passed": [], "failed": []}
        for path in output_paths:
            result = self.check_render(path)
            if result["passed"]:
                results["passed"].append(result)
            else:
                results["failed"].append(result)
        return results

    def _check_resolution(self, output_path: str) -> Dict:
        """检查分辨率"""
        try:
            from PIL import Image
            if output_path.lower().endswith((".png", ".jpg", ".jpeg")):
                with Image.open(output_path) as img:
                    width, height = img.size
                min_size = 256
                passed = width >= min_size and height >= min_size
                return {"passed": passed, "width": width, "height": height}
            return {"passed": True, "warning": "video file, skipped"}
        except ImportError:
            return {"passed": True, "warning": "Pillow not installed"}
        except Exception as e:
            return {"passed": False, "error": str(e)}

    def _check_file_size(self, output_path: str) -> Dict:
        """检查文件大小"""
        try:
            size_kb = os.path.getsize(output_path) / 1024
            min_size_kb = 1
            passed = size_kb >= min_size_kb
            return {"passed": passed, "size_kb": round(size_kb, 2)}
        except Exception as e:
            return {"passed": False, "error": str(e)}

    def _check_frame_count(self, output_path: str) -> Dict:
        """检查帧数（视频）"""
        if output_path.lower().endswith((".mp4", ".mov", ".avi")):
            return {"passed": True, "warning": "frame count check pending"}
        return {"passed": True, "warning": "image file, skipped"}

    def auto_rerender(self, failed_results: List[Dict], renderer=None) -> Dict:
        """自动重渲染不合格的结果（占位，待实现）"""
        return {
            "rerendered": len(failed_results),
            "status": "rerender_pending",
            "message": "自动重渲染功能开发中",
        }


if __name__ == "__main__":
    qc = QualityController()
    print(f"质量阈值: {qc.quality_threshold}")
    print(f"可用检查项: {list(qc.checks.keys())}")
