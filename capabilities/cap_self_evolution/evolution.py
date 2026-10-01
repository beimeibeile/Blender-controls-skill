"""
自我进化模块
从渲染结果中学习优化参数、积累最佳实践
"""
import os
import json
from typing import Dict, List, Optional
from datetime import datetime


class SelfEvolution:
    """自我进化模块"""

    def __init__(self, knowledge_dir: str = None):
        self.knowledge_dir = knowledge_dir or os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "knowledge"
        )
        os.makedirs(self.knowledge_dir, exist_ok=True)
        self.best_practices_file = os.path.join(self.knowledge_dir, "best_practices.json")
        self.learning_log_file = os.path.join(self.knowledge_dir, "learning_log.json")

    def record_result(self, scene: str, params: Dict, result: Dict, quality_score: float) -> bool:
        """记录渲染结果用于学习"""
        try:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "scene": scene,
                "params": params,
                "quality_score": quality_score,
                "result_summary": {
                    "success": result.get("success", False),
                    "render_time": result.get("render_time", 0),
                }
            }

            log = self._load_json(self.learning_log_file, [])
            log.append(log_entry)
            if len(log) > 1000:
                log = log[-1000:]
            self._save_json(self.learning_log_file, log)

            if quality_score >= 0.8:
                self._update_best_practice(scene, params, quality_score)

            return True
        except Exception as e:
            print(f"❌ 记录学习结果失败: {e}")
            return False

    def get_best_params(self, scene: str) -> Optional[Dict]:
        """获取某场景的最佳参数"""
        practices = self._load_json(self.best_practices_file, {})
        return practices.get(scene, {}).get("best_params")

    def suggest_optimization(self, scene: str, current_params: Dict) -> Dict:
        """基于历史数据建议参数优化"""
        best = self.get_best_params(scene)
        if not best:
            return {"suggestion": "no_history", "message": "暂无历史数据"}

        suggestions = []
        for key, best_value in best.items():
            if key in current_params and current_params[key] != best_value:
                suggestions.append({
                    "param": key,
                    "current": current_params[key],
                    "suggested": best_value,
                    "reason": "历史最佳实践",
                })

        return {
            "scene": scene,
            "best_quality_score": best.get("_quality_score", 0),
            "suggestions": suggestions,
        }

    def get_learning_stats(self) -> Dict:
        """获取学习统计"""
        log = self._load_json(self.learning_log_file, [])
        practices = self._load_json(self.best_practices_file, {})

        total = len(log)
        high_quality = sum(1 for entry in log if entry.get("quality_score", 0) >= 0.8)
        avg_quality = sum(entry.get("quality_score", 0) for entry in log) / total if total > 0 else 0

        return {
            "total_records": total,
            "high_quality_count": high_quality,
            "average_quality_score": round(avg_quality, 3),
            "best_practices_count": len(practices),
            "scenes_learned": list(practices.keys()),
        }

    def _update_best_practice(self, scene: str, params: Dict, quality_score: float):
        """更新最佳实践"""
        practices = self._load_json(self.best_practices_file, {})
        current_best = practices.get(scene, {})
        if quality_score > current_best.get("_quality_score", 0):
            practices[scene] = {
                "best_params": params,
                "_quality_score": quality_score,
                "_updated_at": datetime.now().isoformat(),
            }
            self._save_json(self.best_practices_file, practices)

    def record_quality_result(self, scene: str, params: Dict, quality_result: Dict) -> bool:
        """
        从质量检查结果中学习

        Args:
            scene: 场景名称
            params: 渲染参数
            quality_result: QualityController.check_render()的结果

        Returns:
            是否记录成功
        """
        score = quality_result.get("score", 0.5)
        render_time = quality_result.get("render_time", 0)

        result_summary = {
            "success": quality_result.get("passed", False),
            "score": score,
            "checks": list(quality_result.get("checks", {}).keys()),
            "failed_checks": [k for k, v in quality_result.get("checks", {}).items()
                              if not v.get("passed", True)],
        }

        return self.record_result(scene, params, result_summary, score)

    def get_optimization_report(self) -> Dict:
        """生成全局优化建议报告"""
        stats = self.get_learning_stats()
        practices = self._load_json(self.best_practices_file, {})
        log = self._load_json(self.learning_log_file, [])

        report = {
            "summary": stats,
            "top_scenes": [],
            "weak_scenes": [],
            "recommendations": [],
        }

        # 找出表现最好和最差的场景
        scene_scores = {}
        for entry in log:
            scene = entry.get("scene", "unknown")
            if scene not in scene_scores:
                scene_scores[scene] = []
            scene_scores[scene].append(entry.get("quality_score", 0))

        for scene, scores in scene_scores.items():
            avg = sum(scores) / len(scores) if scores else 0
            if avg >= 0.8:
                report["top_scenes"].append({"scene": scene, "avg_score": round(avg, 3), "runs": len(scores)})
            elif avg < 0.5:
                report["weak_scenes"].append({"scene": scene, "avg_score": round(avg, 3), "runs": len(scores)})

        # 生成建议
        if stats["total_records"] < 10:
            report["recommendations"].append("数据量不足，建议多运行几次场景以积累学习数据")
        if report["weak_scenes"]:
            report["recommendations"].append(f"以下场景表现较差，建议优化参数: {[s['scene'] for s in report['weak_scenes']]}")
        if stats["high_quality_count"] > 0 and stats["total_records"] > 0:
            rate = stats["high_quality_count"] / stats["total_records"]
            if rate < 0.5:
                report["recommendations"].append(f"高质量产出率仅{rate:.0%}，建议降低渲染复杂度或提升硬件")

        return report

    def export_knowledge(self, output_path: str) -> str:
        """导出知识库为JSON"""
        data = {
            "best_practices": self._load_json(self.best_practices_file, {}),
            "learning_log": self._load_json(self.learning_log_file, []),
            "stats": self.get_learning_stats(),
            "exported_at": datetime.now().isoformat(),
        }
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return output_path

    def _load_json(self, path: str, default):
        if not os.path.exists(path):
            return default
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return default

    def _save_json(self, path: str, data):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    se = SelfEvolution()
    print(f"知识库目录: {se.knowledge_dir}")
    print(f"学习统计: {json.dumps(se.get_learning_stats(), indent=2, ensure_ascii=False)}")
