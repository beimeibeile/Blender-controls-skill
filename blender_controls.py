"""
Blender Controls Skill - 统一入口模块
智能管理和控制Blender，3D场景管理、特效库、批量渲染、自我进化

使用方法：
    from blender_controls import BlenderControls
    bc = BlenderControls(blender_path="C:/Program Files/Blender Foundation/Blender 5.2/blender.exe")
    bc.render_intro(style="cinematic", text="AI VIDEO")
    bc.render_effect("particle_background", preset="stars", duration=3)
"""

import os
import sys
from typing import Dict, List, Optional, Any

# 添加能力模块路径
_cap_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "capabilities")
for sub in ["cap_api_wrapper", "cap_scene_manager", "cap_effects_library",
            "cap_batch_renderer", "cap_quality_control", "cap_self_evolution"]:
    sys.path.insert(0, os.path.join(_cap_dir, sub))

try:
    from cap_api_wrapper.blender_runner import BlenderRunner
    _BLENDER_RUNNER_AVAILABLE = True
except ImportError:
    _BLENDER_RUNNER_AVAILABLE = False

try:
    from cap_effects_library.blender_intro import create_blender_intro
    _BLENDER_INTRO_AVAILABLE = True
except ImportError:
    _BLENDER_INTRO_AVAILABLE = False

try:
    from cap_effects_library.blender_effects import (
        create_particle_background,
        create_text_intro,
        create_transition,
        create_light_sweep,
    )
    _BLENDER_EFFECTS_AVAILABLE = True
except ImportError:
    _BLENDER_EFFECTS_AVAILABLE = False

from cap_scene_manager.manager import SceneManager
from cap_batch_renderer.renderer import BatchRenderer
from cap_quality_control.controller import QualityController
from cap_self_evolution.evolution import SelfEvolution


class BlenderControls:
    """Blender智能控制器 - 统一入口"""

    # Blender默认路径（Windows）
    DEFAULT_BLENDER_PATHS = [
        r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe",
        r"C:\Program Files\Blender Foundation\Blender 4.1\blender.exe",
        "/Applications/Blender.app/Contents/MacOS/Blender",
        "blender",
    ]

    def __init__(self,
                 blender_path: str = None,
                 output_dir: str = None,
                 auto_evolve: bool = True):
        """
        初始化Blender控制器

        Args:
            blender_path: Blender可执行文件路径
            output_dir: 输出目录
            auto_evolve: 是否启用自动进化
        """
        self.blender_path = blender_path or self._find_blender()
        self.output_dir = output_dir or os.environ.get("BLENDER_OUTPUT_DIR", "./output")
        self.auto_evolve = auto_evolve
        os.makedirs(self.output_dir, exist_ok=True)

        # 初始化各模块
        self.runner = BlenderRunner(blender_path=self.blender_path) if _BLENDER_RUNNER_AVAILABLE else None
        self.scenes = SceneManager()
        self.batch = BatchRenderer(output_dir=self.output_dir)
        self.quality = QualityController()
        self.evolution = SelfEvolution()

        print(f"✅ BlenderControls 初始化完成")
        print(f"   Blender: {self.blender_path} {'可用' if self.is_available() else '不可用'}")
        print(f"   片头生成器: {'✅' if _BLENDER_INTRO_AVAILABLE else '❌'}")
        print(f"   扩展特效库: {'✅' if _BLENDER_EFFECTS_AVAILABLE else '❌'}")

    def _find_blender(self) -> str:
        """自动查找Blender路径"""
        for path in self.DEFAULT_BLENDER_PATHS:
            if os.path.exists(path):
                return path
        return "blender"

    def is_available(self) -> bool:
        """检查Blender是否可用"""
        if not self.blender_path:
            return False
        if self.blender_path == "blender":
            # 检查PATH中是否有blender
            import shutil
            return shutil.which("blender") is not None
        return os.path.exists(self.blender_path)

    def render_intro(self, style: str = "cinematic", text: str = "AI VIDEO",
                     duration: float = 3.0, width: int = 1080, height: int = 1920,
                     output_dir: str = None) -> Optional[str]:
        """
        渲染3D片头

        Args:
            style: 片头风格（cinematic/neon/minimal/epic）
            text: 片头文字
            duration: 时长（秒）
            width: 宽度
            height: 高度
            output_dir: 输出目录

        Returns:
            输出视频路径或None
        """
        if not _BLENDER_INTRO_AVAILABLE:
            print("❌ Blender片头生成器不可用")
            return None

        out_dir = output_dir or os.path.join(self.output_dir, "intro")
        return create_blender_intro(
            style=style,
            text=text,
            duration=duration,
            width=width,
            height=height,
            output_dir=out_dir,
            blender_path=self.blender_path,
        )

    def render_effect(self, effect_type: str, **kwargs) -> Optional[str]:
        """
        渲染特效

        Args:
            effect_type: 特效类型（particle_background/text_intro/transition/light_sweep）
            **kwargs: 特效参数

        Returns:
            输出视频路径或None
        """
        if not _BLENDER_EFFECTS_AVAILABLE:
            print("❌ Blender扩展特效库不可用")
            return None

        out_dir = kwargs.pop("output_dir", os.path.join(self.output_dir, "effects"))
        kwargs["output_dir"] = out_dir
        kwargs["blender_path"] = self.blender_path

        effect_map = {
            "particle_background": create_particle_background,
            "text_intro": create_text_intro,
            "transition": create_transition,
            "light_sweep": create_light_sweep,
        }

        func = effect_map.get(effect_type)
        if not func:
            print(f"❌ 未知特效类型: {effect_type}，可用: {list(effect_map.keys())}")
            return None

        return func(**kwargs)

    def list_effects(self) -> Dict[str, Any]:
        """列出可用特效"""
        return {
            "intro_styles": ["cinematic", "neon", "minimal", "epic"],
            "particle_presets": ["stars", "snow", "bokeh", "fireworks", "neon"],
            "text_intro_styles": ["zoom", "slide", "fade", "rotate"],
            "transition_styles": ["fade", "slide_left", "slide_right", "zoom_in", "zoom_out"],
            "light_sweep": "single light bar sweep",
        }

    def batch_render(self, tasks: List[Dict]) -> Dict:
        """批量渲染"""
        return self.batch.render(tasks)

    def check_quality(self, video_path: str) -> Dict:
        """检查视频质量"""
        return self.quality.check_video(video_path)

    def get_evolution_stats(self) -> Dict:
        """获取进化统计"""
        return self.evolution.get_learning_stats()

    def get_status(self) -> Dict:
        """获取完整状态"""
        return {
            "available": self.is_available(),
            "blender_path": self.blender_path,
            "intro_available": _BLENDER_INTRO_AVAILABLE,
            "effects_available": _BLENDER_EFFECTS_AVAILABLE,
            "effects": self.list_effects(),
            "evolution": self.get_evolution_stats(),
        }


def create_controls(blender_path: str = None, **kwargs) -> BlenderControls:
    """便捷创建BlenderControls实例"""
    return BlenderControls(blender_path=blender_path, **kwargs)


if __name__ == "__main__":
    print("=" * 60)
    print("Blender Controls Skill")
    print("=" * 60)
    bc = create_controls()
    print(f"\n状态: {bc.get_status()}")
    print(f"\n可用特效: {bc.list_effects()}")
