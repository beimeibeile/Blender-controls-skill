"""
质量控制器
渲染结果质量检测、自动筛选、不合格重渲染
"""
import os
import json
import subprocess
from typing import Dict, List, Optional

FFMPEG_PATH = os.environ.get("FFMPEG_PATH", r"D:\Ai\ffmpeg-master-latest-win64-gpl\bin\ffmpeg.exe")
FFPROBE_PATH = os.environ.get("FFPROBE_PATH", r"D:\Ai\ffmpeg-master-latest-win64-gpl\bin\ffprobe.exe")


class QualityController:
    """质量控制器"""

    def __init__(self, quality_threshold: float = 0.7,
                 min_resolution: tuple = (256, 256),
                 min_file_size_kb: int = 1,
                 min_duration_sec: float = 0.5):
        self.quality_threshold = quality_threshold
        self.min_resolution = min_resolution
        self.min_file_size_kb = min_file_size_kb
        self.min_duration_sec = min_duration_sec
        self.checks = {
            "resolution": self._check_resolution,
            "file_size": self._check_file_size,
            "video_metadata": self._check_video_metadata,
            "black_frame": self._check_black_frame,
        }

    def check_render(self, output_path: str) -> Dict:
        """检查渲染结果质量"""
        if not os.path.exists(output_path):
            return {"status": "failed", "error": "file_not_found"}

        results = {"file": output_path, "checks": {}, "passed": True, "score": 0.0}
        check_scores = []

        for check_name, check_func in self.checks.items():
            try:
                check_result = check_func(output_path)
                results["checks"][check_name] = check_result
                if not check_result.get("passed", True):
                    results["passed"] = False
                check_scores.append(check_result.get("score", 1.0 if check_result.get("passed") else 0.0))
            except Exception as e:
                results["checks"][check_name] = {"passed": False, "error": str(e)}
                results["passed"] = False
                check_scores.append(0.0)

        results["score"] = round(sum(check_scores) / len(check_scores), 3) if check_scores else 0.0
        return results

    def check_batch(self, output_paths: List[str]) -> Dict:
        """批量检查渲染结果"""
        results = {"total": len(output_paths), "passed": [], "failed": [], "avg_score": 0.0}
        scores = []
        for path in output_paths:
            result = self.check_render(path)
            scores.append(result.get("score", 0))
            if result["passed"]:
                results["passed"].append(result)
            else:
                results["failed"].append(result)
        results["avg_score"] = round(sum(scores) / len(scores), 3) if scores else 0.0
        return results

    def _check_resolution(self, output_path: str) -> Dict:
        """检查分辨率"""
        try:
            from PIL import Image
            if output_path.lower().endswith((".png", ".jpg", ".jpeg")):
                with Image.open(output_path) as img:
                    width, height = img.size
                passed = width >= self.min_resolution[0] and height >= self.min_resolution[1]
                score = min(1.0, (width * height) / (1920 * 1080))
                return {"passed": passed, "width": width, "height": height, "score": score}
            return {"passed": True, "warning": "video file, use video_metadata", "score": 1.0}
        except ImportError:
            return {"passed": True, "warning": "Pillow not installed", "score": 1.0}
        except Exception as e:
            return {"passed": False, "error": str(e), "score": 0.0}

    def _check_file_size(self, output_path: str) -> Dict:
        """检查文件大小"""
        try:
            size_kb = os.path.getsize(output_path) / 1024
            passed = size_kb >= self.min_file_size_kb
            score = min(1.0, size_kb / 1024)
            return {"passed": passed, "size_kb": round(size_kb, 2), "score": score}
        except Exception as e:
            return {"passed": False, "error": str(e), "score": 0.0}

    def _check_video_metadata(self, output_path: str) -> Dict:
        """检查视频元数据（时长/分辨率/帧率/码率）"""
        if not output_path.lower().endswith((".mp4", ".mov", ".avi", ".mkv")):
            return {"passed": True, "warning": "not a video file", "score": 1.0}

        if not os.path.exists(FFPROBE_PATH):
            return {"passed": True, "warning": "ffprobe not available", "score": 1.0}

        try:
            result = subprocess.run(
                [FFPROBE_PATH, "-v", "quiet", "-print_format", "json",
                 "-show_format", "-show_streams", output_path],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode != 0:
                return {"passed": False, "error": "ffprobe failed", "score": 0.0}

            data = json.loads(result.stdout)
            format_info = data.get("format", {})
            video_stream = next((s for s in data.get("streams", []) if s.get("codec_type") == "video"), {})

            duration = float(format_info.get("duration", 0))
            width = int(video_stream.get("width", 0))
            height = int(video_stream.get("height", 0))
            bit_rate = int(format_info.get("bit_rate", 0)) / 1000
            fps_str = video_stream.get("r_frame_rate", "30/1")
            if "/" in fps_str:
                num, den = fps_str.split("/")
                fps = float(num) / float(den) if float(den) > 0 else 30
            else:
                fps = float(fps_str)

            passed = (duration >= self.min_duration_sec and
                      width >= self.min_resolution[0] and
                      height >= self.min_resolution[1])

            duration_score = min(1.0, duration / 5.0)
            resolution_score = min(1.0, (width * height) / (1920 * 1080))
            bitrate_score = min(1.0, bit_rate / 5000)
            score = round((duration_score + resolution_score + bitrate_score) / 3, 3)

            return {
                "passed": passed,
                "duration_sec": round(duration, 2),
                "width": width,
                "height": height,
                "fps": round(fps, 1),
                "bitrate_kbps": round(bit_rate, 1),
                "score": score,
            }
        except Exception as e:
            return {"passed": False, "error": str(e), "score": 0.0}

    def _check_black_frame(self, output_path: str) -> Dict:
        """检测全黑帧（渲染失败常见问题）"""
        if not output_path.lower().endswith((".png", ".jpg", ".jpeg")):
            return {"passed": True, "warning": "not an image", "score": 1.0}

        try:
            from PIL import Image
            import numpy as np
            with Image.open(output_path) as img:
                arr = np.array(img.convert("L"))
            mean_brightness = arr.mean()
            passed = mean_brightness > 5
            score = min(1.0, mean_brightness / 128)
            return {
                "passed": passed,
                "mean_brightness": round(float(mean_brightness), 2),
                "score": score,
            }
        except ImportError:
            return {"passed": True, "warning": "numpy not installed", "score": 1.0}
        except Exception as e:
            return {"passed": False, "error": str(e), "score": 0.0}

    def auto_rerender(self, failed_results: List[Dict], renderer=None,
                      max_retries: int = 2) -> Dict:
        """自动重渲染不合格的结果"""
        if renderer is None:
            from cap_batch_renderer import BatchRenderer
            renderer = BatchRenderer()

        rerendered = []
        still_failed = []

        for result in failed_results:
            file_path = result.get("file", "")
            if not os.path.exists(file_path):
                still_failed.append(result)
                continue

            blend_file = os.path.splitext(file_path)[0] + ".blend"
            if not os.path.exists(blend_file):
                blend_file = os.path.join(os.path.dirname(file_path), "..",
                                          os.path.basename(os.path.dirname(file_path)) + ".blend")

            if os.path.exists(blend_file):
                try:
                    output_dir = os.path.dirname(file_path)
                    render_result = renderer._get_api().render(blend_file, output_dir=output_dir)
                    if render_result.get("success"):
                        rerendered.append({"file": file_path, "blend": blend_file})
                    else:
                        still_failed.append(result)
                except Exception as e:
                    result["rerender_error"] = str(e)
                    still_failed.append(result)
            else:
                still_failed.append(result)

        return {
            "rerendered": len(rerendered),
            "still_failed": len(still_failed),
            "rerendered_files": rerendered,
            "still_failed_files": still_failed,
        }

    def generate_report(self, batch_result: Dict, output_path: str = None) -> str:
        """生成质量检查HTML报告"""
        html = f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>渲染质量报告</title>
<style>
body {{ font-family: sans-serif; background: #0d1117; color: #c9d1d9; padding: 20px; }}
.pass {{ color: #3fb950; }} .fail {{ color: #f85149; }}
.card {{ background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 16px; margin: 8px 0; }}
</style></head><body>
<h1>渲染质量检查报告</h1>
<p>总计: {batch_result['total']} | 通过: <span class="pass">{len(batch_result['passed'])}</span> | 失败: <span class="fail">{len(batch_result['failed'])}</span> | 平均分: {batch_result.get('avg_score', 0)}</p>
"""
        for r in batch_result.get("failed", []):
            html += f'<div class="card"><h3 class="fail">❌ {os.path.basename(r.get("file","?"))}</h3>'
            for check_name, check_result in r.get("checks", {}).items():
                if not check_result.get("passed", True):
                    html += f'<p>{check_name}: {check_result}</p>'
            html += '</div>'
        html += "</body></html>"

        if output_path is None:
            output_path = os.path.join(os.path.expanduser("~"), "quality_report.html")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)
        return output_path


if __name__ == "__main__":
    qc = QualityController()
    print(f"质量阈值: {qc.quality_threshold}")
    print(f"可用检查项: {list(qc.checks.keys())}")
    print(f"ffprobe: {'可用' if os.path.exists(FFPROBE_PATH) else '不可用'}")
