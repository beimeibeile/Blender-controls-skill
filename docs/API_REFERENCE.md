# Blender Controls Skill - API 参考文档

## 主控入口: BlenderControls

```python
from blender_controls import BlenderControls, create_controls
bc = create_controls(blender_path="C:/Program Files/Blender Foundation/Blender 5.2/blender.exe")
```

### 核心方法

| 方法 | 说明 | 返回值 |
|------|------|--------|
| `is_available()` | 检查Blender是否可用 | bool |
| `render_intro(style, text, duration, width, height)` | 渲染3D片头 | Optional[str] |
| `render_effect(effect_type, **kwargs)` | 渲染特效 | Optional[str] |
| `list_effects()` | 列出可用特效 | Dict |
| `batch_render(tasks)` | 批量渲染 | Dict |
| `check_quality(video_path)` | 检查视频质量 | Dict |
| `get_status()` | 获取完整状态 | Dict |

### 片头风格 (intro_styles)
- cinematic: 电影感
- neon: 霓虹
- minimal: 极简
- epic: 史诗

### 特效类型 (effect_type)
- particle_background: 粒子背景（stars/snow/bokeh/fireworks/neon）
- text_intro: 文字片头（zoom/slide/fade/rotate）
- transition: 转场（fade/slide_left/slide_right/zoom_in/zoom_out）
- light_sweep: 光扫

## 能力模块
- cap_api_wrapper: BlenderRunner（Blender进程管理+脚本执行）
- cap_scene_manager: SceneManager（3D场景管理）
- cap_effects_library: 特效库（片头+粒子+转场+光扫）
- cap_batch_renderer: BatchRenderer（批量渲染）
- cap_quality_control: QualityController（质量检测）
- cap_self_evolution: SelfEvolution（自学习进化）
