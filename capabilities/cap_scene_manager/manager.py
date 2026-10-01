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

    def run(self, name: str, params: Dict = None, api=None, output_dir: str = None) -> Optional[Dict]:
        """
        运行场景模板

        Args:
            name: 场景模板名称
            params: 覆盖参数（分辨率/帧数/引擎等）
            api: BlenderAPI实例（None则自动创建）
            output_dir: 输出目录

        Returns:
            渲染结果字典
        """
        scene = self.load_scene(name)
        if not scene:
            print(f"❌ 场景不存在: {name}")
            return None

        if api is None:
            from cap_api_wrapper import BlenderAPI
            api = BlenderAPI()

        # 合并参数
        render_cfg = scene.get("render", {})
        if params:
            render_cfg.update(params)

        width = render_cfg.get("width", 1920)
        height = render_cfg.get("height", 1080)
        fps = render_cfg.get("fps", 30)
        frame_start = render_cfg.get("frame_start", 1)
        frame_end = render_cfg.get("frame_end", fps * 3)
        engine = render_cfg.get("engine", "BLENDER_EEVEE")

        if output_dir is None:
            output_dir = os.path.join(self.scenes_dir, "..", "output", name)
        os.makedirs(output_dir, exist_ok=True)

        # 构建场景设置脚本
        setup_script = f"""
import bpy

# 清空默认场景
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# 渲染设置
scene = bpy.context.scene
scene.render.engine = '{engine}'
scene.render.resolution_x = {width}
scene.render.resolution_y = {height}
scene.render.fps = {fps}
scene.frame_start = {frame_start}
scene.frame_end = {frame_end}
scene.render.filepath = r'{output_dir}/'

# 应用场景对象
"""

        # 添加场景中的对象
        objects = scene.get("objects", [])
        for obj in objects:
            obj_type = obj.get("type", "cube")
            location = obj.get("location", [0, 0, 0])
            scale = obj.get("scale", [1, 1, 1])
            setup_script += f"""
bpy.ops.mesh.primitive_{obj_type}_add(location={location})
obj = bpy.context.active_object
obj.scale = {scale}
"""

        # 添加相机和灯光
        setup_script += """
# 相机
bpy.ops.object.camera_add(location=(0, -10, 5))
bpy.context.scene.camera = bpy.context.active_object

# 灯光
bpy.ops.object.light_add(type='SUN', location=(5, -5, 10))

# 保存blend文件
"""
        blend_path = os.path.join(output_dir, f"{name}.blend")
        setup_script += f"bpy.ops.wm.save_as_mainfile(filepath=r'{blend_path}')\n"

        # 运行设置脚本
        print(f"  构建场景: {name} ({width}x{height}, {frame_end-frame_start+1}帧)")
        setup_result = api.run_script(setup_script, background=True)
        if not setup_result["success"]:
            print(f"  ❌ 场景构建失败: {setup_result['stderr'][:200]}")
            return {"scene": name, "status": "setup_failed", "error": setup_result["stderr"]}

        # 渲染
        print(f"  开始渲染...")
        render_result = api.render(blend_path, output_dir=output_dir,
                                   frame_start=frame_start, frame_end=frame_end, engine=engine)

        status = "success" if render_result["success"] else "render_failed"
        print(f"  渲染{'✅ 完成' if render_result['success'] else '❌ 失败'}")

        return {
            "scene": name,
            "status": status,
            "blend_path": blend_path,
            "output_dir": output_dir,
            "frames": frame_end - frame_start + 1,
            "render_result": render_result,
        }

    def optimize(self, name: str, api=None) -> Dict:
        """
        自动优化场景参数
        基于场景复杂度推荐渲染引擎和采样数

        Args:
            name: 场景名称
            api: BlenderAPI实例

        Returns:
            优化建议字典
        """
        scene = self.load_scene(name)
        if not scene:
            return {"scene": name, "status": "not_found"}

        obj_count = len(scene.get("objects", []))
        has_transparent = any(o.get("transparent") for o in scene.get("objects", []))
        has_particles = scene.get("particles", {}).get("count", 0) > 0

        # 简单优化规则
        if obj_count > 20 or has_particles:
            recommended_engine = "BLENDER_EEVEE"
            recommended_samples = 64
        elif has_transparent:
            recommended_engine = "CYCLES"
            recommended_samples = 128
        else:
            recommended_engine = "BLENDER_EEVEE"
            recommended_samples = 32

        optimization = {
            "scene": name,
            "object_count": obj_count,
            "has_transparent": has_transparent,
            "has_particles": has_particles,
            "recommended_engine": recommended_engine,
            "recommended_samples": recommended_samples,
            "estimated_render_time": f"{obj_count * 2 + (60 if has_particles else 0)}秒",
        }

        # 保存优化后的场景
        scene.setdefault("render", {})
        scene["render"]["engine"] = recommended_engine
        scene["render"]["samples"] = recommended_samples
        self.save_scene(name, scene, version=scene.get("_meta", {}).get("version", "1.0") + "+opt")

        return optimization


if __name__ == "__main__":
    sm = SceneManager()
    print(f"场景目录: {sm.scenes_dir}")
    print(f"可用场景: {sm.list_scenes()}")
