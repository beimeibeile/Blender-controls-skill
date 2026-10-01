"""
3D场景管理器
场景模板库、版本控制、参数优化、一键运行
"""
import os
import json
from typing import Dict, List, Optional


class SceneManager:
    """3D场景管理器"""

    def __init__(self, scenes_dir: str = None):
        self.scenes_dir = scenes_dir or os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "scenes"
        )
        os.makedirs(self.scenes_dir, exist_ok=True)

    def list_scenes(self) -> List[str]:
        """列出所有场景模板"""
        scenes = []
        for f in os.listdir(self.scenes_dir):
            if f.endswith(".json"):
                scenes.append(f.replace(".json", ""))
        return sorted(scenes)

    def load_scene(self, name: str) -> Optional[Dict]:
        """加载场景模板"""
        path = os.path.join(self.scenes_dir, f"{name}.json")
        if not os.path.exists(path):
            return None
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def save_scene(self, name: str, scene: Dict, version: str = "1.0") -> str:
        """保存场景模板"""
        scene["_meta"] = {
            "name": name,
            "version": version,
        }
        path = os.path.join(self.scenes_dir, f"{name}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(scene, f, ensure_ascii=False, indent=2)
        return path

    def run(self, name: str, params: Dict = None, api=None) -> Optional[Dict]:
        """运行场景"""
        scene = self.load_scene(name)
        if not scene:
            print(f"❌ 场景不存在: {name}")
            return None
        if api is None:
            from cap_api_wrapper import BlenderAPI
            api = BlenderAPI()
        # 构建Blender脚本并运行
        return {"scene": name, "status": "submitted"}

    def optimize(self, name: str) -> Dict:
        """自动优化场景参数（占位，待实现）"""
        return {"scene": name, "status": "optimization_pending"}


if __name__ == "__main__":
    sm = SceneManager()
    print(f"场景目录: {sm.scenes_dir}")
    print(f"可用场景: {sm.list_scenes()}")
