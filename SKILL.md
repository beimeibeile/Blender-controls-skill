---
name: Blender-controls-skill
version: 1.0.0
description: |
  Blender 智能管理与控制技能。核心能力：3D场景管理、特效库、批量渲染、
  质量门控制、API统一封装、自我学习进化。与 ai-video-editor、anysearch-skill、
  Comfyui-controls-skill 为姊妹项目，四项目更新须同步。
  Use when asked to 管理Blender、控制Blender、Blender场景、3D特效、批量渲染、Blender自动化。
allowed-tools:
  - Read
  - Write
  - Bash
  - Glob
  - Grep
triggers:
  - blender
  - Blender
  - 3D场景
  - 3D特效
  - 批量渲染
  - blender控制
  - blender管理
metadata:
  license: MIT
  requires:
    bins:
      - python
      - git
      - blender
---

# Blender Controls Skill

> **Blender 智能管理与控制框架** —— 让 Blender 从工具变成自动出3D产品的智能体。场景管理 + 特效库 + 批量渲染 + 质量控制，全链路自动化。

## 姊妹项目（航空母舰战斗群）

| 项目 | 定位 | 角色 |
|------|------|------|
| **ai-video-editor** | AI视频剪辑框架 | 🚢 航空母舰（集成平台） |
| **anysearch-skill** | 深度搜索技能 | 📡 雷达（情报搜索） |
| **Comfyui-controls-skill** | ComfyUI智能管理与控制 | 🚀 导弹（AI算力生成） |
| **Blender-controls-skill** | Blender智能管理与控制（本项目） | 🚀 新导弹（3D合成特效） |

> 单体都能干活，任意组合互相增强，聚齐就是航空母舰！

## 核心能力

| 能力 | 说明 |
|------|------|
| **3D场景管理** | 场景模板库、版本控制、参数优化、一键运行 |
| **特效库** | 粒子背景、文字动画、转场遮罩、光线扫描、3D片头 |
| **批量渲染** | 批量渲染、队列管理、进度监控、结果归档 |
| **质量门控制** | 渲染结果质量检测、自动筛选、不合格重渲染 |
| **API统一封装** | 统一接口调用Blender，屏蔽版本差异（4.x/5.x） |
| **自我学习进化** | 从渲染结果中学习优化参数、积累最佳实践 |
| **算力监控** | GPU使用监控、渲染队列管理、资源调度 |
| **环境自适应** | 自动检测Blender版本、可用插件、渲染引擎 |

## 快速开始

```bash
# 1. 克隆项目
git clone https://github.com/beimeibeile/Blender-controls-skill.git
cd Blender-controls-skill

# 2. 配置环境
cp .env.example .env
# 编辑 .env，填入 Blender 路径

# 3. 验证连接
python -c "from capabilities.cap_api_wrapper import BlenderAPI; api = BlenderAPI(); print(api.get_version())"
```

## 环境要求

| 组件 | 必需？ | 说明 |
|------|--------|------|
| **Python** | ✅ 必需 | ≥ 3.10 |
| **Blender** | ✅ 必需 | 4.x 或 5.x，默认 5.2 |
| **GPU** | ⚡ 推荐 | NVIDIA CUDA，显存 ≥ 8GB |
| **FFmpeg** | 可选 | 视频后处理 |

## 项目架构

```
Blender-controls-skill/
├── capabilities/              # 能力模块（可插拔）
│   ├── cap_scene_manager/         # 3D场景管理
│   ├── cap_effects_library/       # 特效库
│   ├── cap_batch_renderer/        # 批量渲染
│   ├── cap_quality_control/       # 质量控制
│   ├── cap_api_wrapper/           # API封装
│   └── cap_self_evolution/        # 自我进化
├── scenes/                    # 场景模板库
├── knowledge/                 # 知识库（自学习）
├── scripts/                   # 工具脚本
├── utils/                     # 工具函数
├── SKILL.md                   # 本文件
└── README.md                  # 项目说明
```

## 使用示例

### 1. 批量渲染场景

```python
from capabilities.cap_batch_renderer import BatchRenderer

renderer = BatchRenderer()
results = renderer.render_batch(
    scenes=["intro_cinematic", "intro_neon", "intro_minimal"],
    output_dir="./output",
    quality_check=True,
)
print(f"渲染完成: {len(results['success'])}成功, {len(results['failed'])}失败")
```

### 2. 特效生成

```python
from capabilities.cap_effects_library import EffectsLibrary

effects = EffectsLibrary()
effects.list_effects()           # 列出所有特效
effects.generate("particle_stars", duration=3.0, output_dir="./output")
effects.generate("text_intro", text="AI VIDEO", style="zoom")
```

### 3. 场景管理

```python
from capabilities.cap_scene_manager import SceneManager

sm = SceneManager()
sm.list_scenes()             # 列出场景
sm.run("intro_cinematic", {"title": "Hello"})
sm.optimize("intro_cinematic")  # 自动优化场景参数
```

## 配置说明

复制 `.env.example` 为 `.env` 并配置：

```env
# Blender 连接配置
BLENDER_PATH=C:\Program Files\Blender Foundation\Blender 5.2\blender.exe
BLENDER_VERSION=5.2

# 渲染配置
DEFAULT_OUTPUT_DIR=./output
DEFAULT_RENDER_ENGINE=BLENDER_EEVEE
MAX_RENDER_QUEUE=10
QUALITY_CHECK_ENABLED=true

# 算力监控
GPU_MONITOR_INTERVAL=5
MAX_GPU_MEMORY_PERCENT=90

# 自我进化
SELF_LEARNING_ENABLED=true
LEARNING_RATE=0.1
```

## License

[MIT](LICENSE)
