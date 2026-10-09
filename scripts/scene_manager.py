"""
Blender 3D场景管理器
管理3D场景的创建、配置、渲染和批量处理
"""

import os
import sys
import json
import logging
import subprocess
import tempfile
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum

logger = logging.getLogger(__name__)


class SceneType(Enum):
    """场景类型"""
    EMPTY = "empty"
    PRODUCT = "product"          # 产品展示
    LOGO = "logo"                # Logo动画
    PARTICLE = "particle"        # 粒子效果
    TEXT = "text"                # 文字动画
    ABSTRACT = "abstract"        # 抽象背景
    TRANSITION = "transition"    # 转场效果


class RenderEngine(Enum):
    """渲染引擎"""
    CYCLES = "CYCLES"
    EEVEE = "BLENDER_EEVEE"
    WORKBENCH = "BLENDER_WORKBENCH"


@dataclass
class SceneConfig:
    """场景配置"""
    name: str = "default_scene"
    scene_type: SceneType = SceneType.EMPTY
    width: int = 1920
    height: int = 1080
    fps: int = 30
    duration: float = 5.0  # 秒
    render_engine: RenderEngine = RenderEngine.EEVEE
    samples: int = 64
    transparent: bool = False
    background_color: Tuple[float, float, float, float] = (0.0, 0.0, 0.0, 1.0)
    camera_position: Tuple[float, float, float] = (0.0, -5.0, 2.0)
    camera_target: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    light_type: str = "SUN"
    light_energy: float = 2.0
    light_position: Tuple[float, float, float] = (5.0, -5.0, 10.0)
    output_format: str = "PNG"  # PNG/OPEN_EXR/JPEG
    output_path: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RenderResult:
    """渲染结果"""
    success: bool
    output_path: str = ""
    frame_count: int = 0
    duration: float = 0.0
    error: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


class BlenderSceneManager:
    """
    Blender 3D场景管理器
    
    功能：
    1. 场景创建与配置
    2. 批量渲染
    3. 渲染质量控制
    4. 场景模板管理
    """
    
    def __init__(self, blender_path: str = None):
        self.blender_path = blender_path or self._find_blender()
        self.scenes: Dict[str, SceneConfig] = {}
        self.render_history: List[RenderResult] = []
    
    def _find_blender(self) -> str:
        """查找Blender可执行文件"""
        # 常见安装路径
        candidates = [
            r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe",
            r"C:\Program Files\Blender Foundation\Blender 4.2\blender.exe",
            r"C:\Program Files\Blender Foundation\Blender 4.0\blender.exe",
            r"C:\Program Files\Blender Foundation\Blender 3.6\blender.exe",
        ]
        for path in candidates:
            if os.path.exists(path):
                return path
        # 尝试环境变量
        env_path = os.environ.get("BLENDER_PATH")
        if env_path and os.path.exists(env_path):
            return env_path
        logger.warning("未找到Blender可执行文件，使用默认路径")
        return candidates[0]
    
    def create_scene(self, config: SceneConfig) -> str:
        """
        创建3D场景
        
        Args:
            config: 场景配置
        
        Returns:
            场景ID
        """
        scene_id = f"scene_{len(self.scenes) + 1}"
        self.scenes[scene_id] = config
        logger.info("创建场景: %s (%s, %dx%d, %.1fs)", 
                   config.name, config.scene_type.value, 
                   config.width, config.height, config.duration)
        return scene_id
    
    def create_product_scene(self, name: str, 
                              model_path: str = None,
                              width: int = 1920, height: int = 1080,
                              duration: float = 5.0) -> str:
        """创建产品展示场景"""
        config = SceneConfig(
            name=name,
            scene_type=SceneType.PRODUCT,
            width=width,
            height=height,
            duration=duration,
            render_engine=RenderEngine.CYCLES,
            samples=128,
            camera_position=(0.0, -5.0, 2.0),
            light_energy=3.0,
            metadata={"model_path": model_path},
        )
        return self.create_scene(config)
    
    def create_logo_scene(self, name: str, 
                           logo_path: str = None,
                           width: int = 1920, height: int = 1080,
                           duration: float = 3.0) -> str:
        """创建Logo动画场景"""
        config = SceneConfig(
            name=name,
            scene_type=SceneType.LOGO,
            width=width,
            height=height,
            duration=duration,
            render_engine=RenderEngine.EEVEE,
            transparent=True,
            camera_position=(0.0, -5.0, 0.0),
            metadata={"logo_path": logo_path},
        )
        return self.create_scene(config)
    
    def create_particle_scene(self, name: str,
                               particle_type: str = "star",
                               count: int = 1000,
                               width: int = 1920, height: int = 1080,
                               duration: float = 5.0) -> str:
        """创建粒子效果场景"""
        config = SceneConfig(
            name=name,
            scene_type=SceneType.PARTICLE,
            width=width,
            height=height,
            duration=duration,
            render_engine=RenderEngine.EEVEE,
            transparent=True,
            metadata={"particle_type": particle_type, "count": count},
        )
        return self.create_scene(config)
    
    def create_text_scene(self, name: str,
                           text: str = "Hello",
                           font_size: int = 100,
                           width: int = 1920, height: int = 1080,
                           duration: float = 3.0) -> str:
        """创建文字动画场景"""
        config = SceneConfig(
            name=name,
            scene_type=SceneType.TEXT,
            width=width,
            height=height,
            duration=duration,
            render_engine=RenderEngine.EEVEE,
            transparent=True,
            metadata={"text": text, "font_size": font_size},
        )
        return self.create_scene(config)
    
    def generate_blender_script(self, scene_id: str) -> str:
        """
        生成Blender Python脚本
        
        Args:
            scene_id: 场景ID
        
        Returns:
            Python脚本内容
        """
        config = self.scenes.get(scene_id)
        if not config:
            raise ValueError(f"场景不存在: {scene_id}")
        
        frames = int(config.duration * config.fps)
        
        script = f"""import bpy
import os

# 清除默认场景
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# 场景设置
scene = bpy.context.scene
scene.render.resolution_x = {config.width}
scene.render.resolution_y = {config.height}
scene.render.fps = {config.fps}
scene.frame_end = {frames}
scene.render.engine = '{config.render_engine.value}'
scene.render.image_settings.file_format = '{config.output_format}'
scene.render.film_transparent = {str(config.transparent).lower()}

# 相机
bpy.ops.object.camera_add(location={list(config.camera_position)})
camera = bpy.context.active_object
camera.rotation_euler = (1.1, 0.0, 0.0)
scene.camera = camera

# 灯光
bpy.ops.object.light_add(type='{config.light_type}', location={list(config.light_position)})
light = bpy.context.active_object
light.data.energy = {config.light_energy}

# 输出路径
output_dir = r"{os.path.dirname(config.output_path) if config.output_path else tempfile.gettempdir()}"
os.makedirs(output_dir, exist_ok=True)
scene.render.filepath = os.path.join(output_dir, "{config.name}_")

# 渲染
bpy.ops.render.render(animation=True)
print("RENDER_COMPLETE:" + scene.render.filepath)
"""
        return script
    
    def render_scene(self, scene_id: str, 
                     output_dir: str = None) -> RenderResult:
        """
        渲染单个场景
        
        Args:
            scene_id: 场景ID
            output_dir: 输出目录
        
        Returns:
            渲染结果
        """
        config = self.scenes.get(scene_id)
        if not config:
            return RenderResult(success=False, error=f"场景不存在: {scene_id}")
        
        if not os.path.exists(self.blender_path):
            return RenderResult(
                success=False, 
                error=f"Blender未安装: {self.blender_path}"
            )
        
        # 设置输出路径
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            config.output_path = os.path.join(output_dir, f"{config.name}_")
        
        # 生成脚本
        script = self.generate_blender_script(scene_id)
        
        # 写入临时脚本文件
        script_path = os.path.join(tempfile.gettempdir(), f"blender_{scene_id}.py")
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(script)
        
        try:
            # 执行Blender渲染
            cmd = [
                self.blender_path,
                "--background",
                "--python", script_path,
            ]
            
            logger.info("开始渲染场景: %s", config.name)
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5分钟超时
            )
            
            if result.returncode == 0:
                frames = int(config.duration * config.fps)
                render_result = RenderResult(
                    success=True,
                    output_path=config.output_path,
                    frame_count=frames,
                    duration=config.duration,
                    metadata={"scene_type": config.scene_type.value},
                )
                logger.info("渲染完成: %s (%d帧)", config.name, frames)
            else:
                render_result = RenderResult(
                    success=False,
                    error=result.stderr[-500:] if result.stderr else "未知错误",
                )
                logger.error("渲染失败: %s", render_result.error)
            
            self.render_history.append(render_result)
            return render_result
            
        except subprocess.TimeoutExpired:
            return RenderResult(success=False, error="渲染超时")
        except Exception as e:
            return RenderResult(success=False, error=str(e))
        finally:
            # 清理临时文件
            if os.path.exists(script_path):
                os.remove(script_path)
    
    def batch_render(self, scene_ids: List[str], 
                     output_dir: str) -> List[RenderResult]:
        """
        批量渲染多个场景
        
        Args:
            scene_ids: 场景ID列表
            output_dir: 输出目录
        
        Returns:
            渲染结果列表
        """
        results = []
        for i, scene_id in enumerate(scene_ids):
            logger.info("批量渲染进度: %d/%d", i + 1, len(scene_ids))
            result = self.render_scene(scene_id, output_dir)
            results.append(result)
        return results
    
    def get_scene_summary(self) -> Dict[str, Any]:
        """获取场景摘要"""
        return {
            "total_scenes": len(self.scenes),
            "scenes": [
                {
                    "id": sid,
                    "name": cfg.name,
                    "type": cfg.scene_type.value,
                    "resolution": f"{cfg.width}x{cfg.height}",
                    "duration": cfg.duration,
                    "engine": cfg.render_engine.value,
                    "transparent": cfg.transparent,
                }
                for sid, cfg in self.scenes.items()
            ],
            "render_history_count": len(self.render_history),
        }
    
    def list_scene_templates(self) -> List[Dict[str, Any]]:
        """列出可用场景模板"""
        return [
            {"type": "product", "name": "产品展示", "description": "360度产品旋转展示", "engine": "CYCLES"},
            {"type": "logo", "name": "Logo动画", "description": "Logo入场/出场动画", "engine": "EEVEE", "transparent": True},
            {"type": "particle", "name": "粒子效果", "description": "星空/雪花/光斑/烟花", "engine": "EEVEE", "transparent": True},
            {"type": "text", "name": "文字动画", "description": "3D文字入场/循环", "engine": "EEVEE", "transparent": True},
            {"type": "abstract", "name": "抽象背景", "description": "动态抽象背景", "engine": "EEVEE"},
            {"type": "transition", "name": "转场效果", "description": "3D转场动画", "engine": "EEVEE", "transparent": True},
        ]


# ============ 便捷函数 ============
def create_scene_manager() -> BlenderSceneManager:
    """创建场景管理器实例"""
    return BlenderSceneManager()


def render_quick_scene(scene_type: str, name: str, 
                       output_dir: str, **kwargs) -> RenderResult:
    """便捷函数：快速创建并渲染场景"""
    manager = BlenderSceneManager()
    
    creators = {
        "product": manager.create_product_scene,
        "logo": manager.create_logo_scene,
        "particle": manager.create_particle_scene,
        "text": manager.create_text_scene,
    }
    
    creator = creators.get(scene_type)
    if not creator:
        return RenderResult(success=False, error=f"不支持的场景类型: {scene_type}")
    
    scene_id = creator(name, **kwargs)
    return manager.render_scene(scene_id, output_dir)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    manager = BlenderSceneManager()
    
    print("=" * 60)
    print("Blender 3D场景管理器")
    print("=" * 60)
    print(f"Blender路径: {manager.blender_path}")
    print(f"Blender已安装: {os.path.exists(manager.blender_path)}")
    
    print("\n可用场景模板:")
    for tpl in manager.list_scene_templates():
        print(f"  - {tpl['name']} ({tpl['type']}): {tpl['description']}")
    
    # 创建测试场景（不实际渲染）
    scene_id = manager.create_logo_scene("test_logo", duration=3.0)
    print(f"\n创建测试场景: {scene_id}")
    print(manager.get_scene_summary())
