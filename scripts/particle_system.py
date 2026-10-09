"""
Blender粒子系统模块
- 粒子发射器配置
- 力场系统（重力/风力/磁力/湍流）
- 碰撞检测
- 粒子类型（点/线/面/集合）
- 粒子渲染设置
"""

import os
import sys
import logging
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

BLENDER_PATH = r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"


@dataclass
class ParticleEmitterConfig:
    """粒子发射器配置"""
    count: int = 1000
    frame_start: int = 1
    frame_end: int = 100
    lifetime: int = 50
    lifetime_random: float = 0.5
    emit_from: str = "FACE"  # VERT/FACE/VOLUME
    distribution: str = "RAND"  # RAND/JIT/GRID
    normal_factor: float = 1.0
    tangential_factor: float = 0.0
    factor_random: float = 0.5
    physics_type: str = "NEWTONIAN"  # NEWTONIAN/KEYED/BOIDS/FLUID
    particle_size: float = 0.05
    size_random: float = 0.5
    render_type: str = "HALO"  # NONE/LINE/PATH/OBJECT/GROUP/COLLECTION/HALO
    material_index: int = 0


@dataclass
class ForceFieldConfig:
    """力场配置"""
    type: str = "WIND"  # FORCE/WIND/VORTEX/MAGNETIC/HARMONIC/CHARGE/LENNARDJONES/TEXTURE/GUIDE/BOID/TURBULENCE/DRAG/SMOKE_FLOW
    strength: float = 10.0
    flow: float = 1.0
    noise: float = 0.0
    seed: int = 0
    falloff_type: str = "SPHERE"  # SPHERE/CONE/TUBE
    falloff_power: float = 2.0
    use_max_distance: bool = False
    max_distance: float = 10.0
    use_min_distance: bool = False
    min_distance: float = 0.0


@dataclass
class CollisionConfig:
    """碰撞配置"""
    damping: float = 0.0
    friction: float = 0.0
    permeability: float = 0.0
    use_kill: bool = False
    stickiness: float = 0.0
    thickness_outer: float = 0.02
    thickness_inner: float = 0.0
    cloth_friction: float = 5.0
    cloth_killing: float = 0.0


class ParticleSystem:
    """Blender粒子系统管理器"""

    def __init__(self, blender_path: str = None):
        self.blender_path = blender_path or BLENDER_PATH

    def create_particle_explosion(
        self,
        output_path: str,
        particle_count: int = 2000,
        explosion_force: float = 50.0,
        center_location: Tuple[float, float, float] = (0, 0, 0),
        duration: int = 60,
    ) -> bool:
        """创建粒子爆炸效果

        Args:
            output_path: 输出路径
            particle_count: 粒子数量
            explosion_force: 爆炸力度
            center_location: 爆炸中心
            duration: 持续帧数

        Returns:
            True成功，False失败
        """
        script = f"""
import bpy
import math

# 清除场景
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# 创建粒子发射器（球体）
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.5, location={center_location})
emitter = bpy.context.active_object
emitter.name = "Explosion_Emitter"

# 添加粒子系统
ps_mod = emitter.modifiers.new(name="ParticleSystem", type='PARTICLE_SYSTEM')
ps = emitter.particle_systems[-1]
ps.settings.count = {particle_count}
ps.settings.frame_start = 1
ps.settings.frame_end = 5
ps.settings.lifetime = {duration}
ps.settings.lifetime_random = 0.3
ps.settings.emit_from = 'FACE'
ps.settings.normal_factor = {explosion_force}
ps.settings.factor_random = 0.8
ps.settings.physics_type = 'NEWTONIAN'
ps.settings.particle_size = 0.1
ps.settings.size_random = 0.5
ps.settings.render_type = 'HALO'
ps.settings.use_advanced_hair = False

# 添加重力场（减弱）
bpy.context.scene.gravity = (0, 0, -2.0)

# 添加湍流场
bpy.ops.object.effector_add(type='TURBULENCE', location={center_location})
turbulence = bpy.context.active_object
turbulence.name = "Turbulence"
turbulence.field.strength = 5.0
turbulence.field.size = 2.0
turbulence.field.flow = 1.0

# 添加地面碰撞
bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, -5))
ground = bpy.context.active_object
ground.name = "Ground"
ground.modifiers.new(name="Collision", type='COLLISION')
ground.collision.damping = 0.5
ground.collision.friction = 0.3

# 烘焙粒子
bpy.context.scene.frame_set(1)
bpy.ops.ptcache.free_bake_all()
bpy.ops.ptcache.bake_all(bake=True)

# 保存
bpy.ops.wm.save_as_mainfile(filepath=r'{output_path}')
print("PARTICLE_EXPLOSION_DONE")
"""
        return self._run_blender(script, output_path)

    def create_particle_rain(
        self,
        output_path: str,
        particle_count: int = 5000,
        rain_area: float = 10.0,
        rain_height: float = 10.0,
        duration: int = 200,
    ) -> bool:
        """创建粒子雨效果

        Args:
            output_path: 输出路径
            particle_count: 粒子数量
            rain_area: 雨区域大小
            rain_height: 雨高度
            duration: 持续帧数

        Returns:
            True成功，False失败
        """
        script = f"""
import bpy

# 清除场景
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# 创建雨滴发射器（平面）
bpy.ops.mesh.primitive_plane_add(size={rain_area}, location=(0, 0, {rain_height}))
emitter = bpy.context.active_object
emitter.name = "Rain_Emitter"

# 添加粒子系统
ps_mod = emitter.modifiers.new(name="RainSystem", type='PARTICLE_SYSTEM')
ps = emitter.particle_systems[-1]
ps.settings.count = {particle_count}
ps.settings.frame_start = 1
ps.settings.frame_end = {duration}
ps.settings.lifetime = 100
ps.settings.lifetime_random = 0.2
ps.settings.emit_from = 'FACE'
ps.settings.distribution = 'JIT'
ps.settings.normal_factor = 0.0
ps.settings.factor_random = 0.1
ps.settings.physics_type = 'NEWTONIAN'
ps.settings.particle_size = 0.02
ps.settings.render_type = 'LINE'
ps.settings.line_length_tail = 0.5
ps.settings.line_length_head = 0.1

# 设置重力
bpy.context.scene.gravity = (0, 0, -9.81)

# 添加风力（微风）
bpy.ops.object.effector_add(type='WIND', location=(0, 0, {rain_height/2}))
wind = bpy.context.active_object
wind.name = "Wind"
wind.field.strength = 2.0
wind.field.flow = 0.5
wind.rotation_euler = (0, 1.5708, 0)

# 添加地面碰撞（雨滴消失）
bpy.ops.mesh.primitive_plane_add(size={rain_area * 2}, location=(0, 0, 0))
ground = bpy.context.active_object
ground.name = "Ground"
ground.modifiers.new(name="Collision", type='COLLISION')
ground.collision.use_kill = True

# 烘焙粒子
bpy.context.scene.frame_set(1)
bpy.ops.ptcache.free_bake_all()
bpy.ops.ptcache.bake_all(bake=True)

# 保存
bpy.ops.wm.save_as_mainfile(filepath=r'{output_path}')
print("PARTICLE_RAIN_DONE")
"""
        return self._run_blender(script, output_path)

    def create_particle_smoke(
        self,
        output_path: str,
        smoke_resolution: int = 64,
        smoke_duration: int = 150,
        emitter_location: Tuple[float, float, float] = (0, 0, 0),
    ) -> bool:
        """创建烟雾粒子效果

        Args:
            output_path: 输出路径
            smoke_resolution: 烟雾分辨率
            smoke_duration: 持续帧数
            emitter_location: 发射器位置

        Returns:
            True成功，False失败
        """
        script = f"""
import bpy

# 清除场景
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# 创建烟雾域（大立方体）
bpy.ops.mesh.primitive_cube_add(size=10, location=(0, 0, 5))
domain = bpy.context.active_object
domain.name = "Smoke_Domain"

# 添加烟雾流体修改器
domain.modifiers.new(name="Fluid", type='FLUID')
domain.fluid.type = 'DOMAIN'
domain.fluid.domain_settings.domain_type = 'GAS'
domain.fluid.domain_settings.resolution_max = {smoke_resolution}
domain.fluid.domain_settings.use_collision_border = True
domain.fluid.domain_settings.use_dissolve_smoke = True
domain.fluid.domain_settings.dissolve_smoke = 0.1

# 创建烟雾发射器
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.5, location={emitter_location})
emitter = bpy.context.active_object
emitter.name = "Smoke_Emitter"
emitter.modifiers.new(name="Fluid", type='FLUID')
emitter.fluid.type = 'FLOW'
emitter.fluid.flow_settings.flow_type = 'SMOKE'
emitter.fluid.flow_settings.smoke_color = (0.8, 0.8, 0.8)
emitter.fluid.flow_settings.temperature = 1.0
emitter.fluid.flow_settings.use_absolute = True

# 设置动画时长
bpy.context.scene.frame_end = {smoke_duration}

# 烘焙烟雾
bpy.ops.fluid.bake_all()

# 保存
bpy.ops.wm.save_as_mainfile(filepath=r'{output_path}')
print("PARTICLE_SMOKE_DONE")
"""
        return self._run_blender(script, output_path)

    def create_force_field_scene(
        self,
        output_path: str,
        force_fields: List[Dict[str, Any]] = None,
        particle_count: int = 1000,
    ) -> bool:
        """创建多力场粒子场景

        Args:
            output_path: 输出路径
            force_fields: 力场列表 [{type, location, strength, ...}]
            particle_count: 粒子数量

        Returns:
            True成功，False失败
        """
        force_fields = force_fields or [
            {"type": "WIND", "location": (0, 0, 5), "strength": 10.0},
            {"type": "TURBULENCE", "location": (0, 0, 0), "strength": 5.0},
        ]

        fields_script = ""
        for i, ff in enumerate(force_fields):
            ff_type = ff.get("type", "WIND")
            location = ff.get("location", (0, 0, 0))
            strength = ff.get("strength", 10.0)
            fields_script += f"""
bpy.ops.object.effector_add(type='{ff_type}', location={location})
ff_{i} = bpy.context.active_object
ff_{i}.name = "ForceField_{i}_{ff_type}"
ff_{i}.field.strength = {strength}
"""

        script = f"""
import bpy

# 清除场景
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# 创建粒子发射器
bpy.ops.mesh.primitive_plane_add(size=5, location=(0, 0, 5))
emitter = bpy.context.active_object
emitter.name = "Particle_Emitter"

# 添加粒子系统
ps_mod = emitter.modifiers.new(name="ParticleSystem", type='PARTICLE_SYSTEM')
ps = emitter.particle_systems[-1]
ps.settings.count = {particle_count}
ps.settings.frame_start = 1
ps.settings.frame_end = 100
ps.settings.lifetime = 80
ps.settings.normal_factor = 0.5
ps.settings.physics_type = 'NEWTONIAN'
ps.settings.render_type = 'HALO'

# 添加力场
{fields_script}

# 烘焙粒子
bpy.context.scene.frame_set(1)
bpy.ops.ptcache.free_bake_all()
bpy.ops.ptcache.bake_all(bake=True)

# 保存
bpy.ops.wm.save_as_mainfile(filepath=r'{output_path}')
print("FORCE_FIELD_DONE")
"""
        return self._run_blender(script, output_path)

    def _run_blender(self, script: str, output_path: str) -> bool:
        """运行Blender脚本"""
        import subprocess
        import tempfile

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        script_path = os.path.join(tempfile.gettempdir(), "blender_particles.py")
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(script)

        try:
            result = subprocess.run(
                [self.blender_path, "--background", "--python", script_path],
                capture_output=True, text=True, timeout=300
            )
            if "DONE" in result.stdout or os.path.exists(output_path):
                logger.info(f"粒子场景已生成: {output_path}")
                return True
            else:
                logger.error(f"Blender执行失败: {result.stderr[-500:]}")
                return False
        except subprocess.TimeoutExpired:
            logger.error("Blender执行超时")
            return False
        except Exception as e:
            logger.error(f"Blender执行异常: {e}")
            return False
        finally:
            if os.path.exists(script_path):
                os.remove(script_path)


def main():
    """测试粒子系统"""
    ps = ParticleSystem()

    # 测试粒子爆炸
    output = r"D:\DobaoWork_Project\Ai_Video_Editor\test_output\particle_explosion.blend"
    success = ps.create_particle_explosion(output, particle_count=1000)
    print(f"粒子爆炸: {'成功' if success else '失败'}")

    # 测试粒子雨
    output2 = r"D:\DobaoWork_Project\Ai_Video_Editor\test_output\particle_rain.blend"
    success2 = ps.create_particle_rain(output2, particle_count=2000)
    print(f"粒子雨: {'成功' if success2 else '失败'}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    main()
