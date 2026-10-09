"""
Blender物理模拟模块
- 刚体模拟（Rigid Body）
- 柔体模拟（Soft Body）
- 流体模拟（Fluid）
- 布料模拟（Cloth）
- 碰撞检测与设置
"""

import os
import sys
import logging
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

# Blender Python路径
BLENDER_PATH = r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"


@dataclass
class PhysicsConfig:
    """物理模拟配置"""
    gravity: Tuple[float, float, float] = (0, 0, -9.81)
    time_scale: float = 1.0
    steps_per_second: int = 60
    solver_iterations: int = 10
    collision_margin: float = 0.001


@dataclass
class RigidBodyConfig:
    """刚体配置"""
    mass: float = 1.0
    friction: float = 0.5
    restitution: float = 0.0
    linear_damping: float = 0.04
    angular_damping: float = 0.1
    collision_shape: str = "CONVEX_HULL"  # BOX/SPHERE/CONE/CYLINDER/CONVEX_HULL/MESH
    collision_margin: float = 0.001
    use_deform: bool = False
    use_margin: bool = True


@dataclass
class SoftBodyConfig:
    """柔体配置"""
    friction: float = 0.5
    mass: float = 1.0
    stiffness: float = 0.5
    damping: float = 0.5
    pull: float = 0.5
    push: float = 0.5
    speed: float = 1.0
    use_goal: bool = True
    goal_default: float = 0.5
    goal_min: float = 0.0
    goal_max: float = 1.0


@dataclass
class ClothConfig:
    """布料配置"""
    mass: float = 0.3
    structural_stiffness: float = 40.0
    bending_stiffness: float = 0.1
    spring_damping: float = 5.0
    air_damping: float = 1.0
    friction: float = 5.0
    collision_quality: float = 2.0
    use_sewing: bool = False
    use_pressure: bool = False
    pressure_factor: float = 0.0


@dataclass
class FluidConfig:
    """流体配置"""
    domain_type: str = "LIQUID"  # LIQUID/SMOKE/FIRE
    resolution: int = 64
    time_scale: float = 1.0
    viscosity: float = 0.0
    use_collision: bool = True
    use_inflow: bool = True
    use_outflow: bool = False
    particle_type: str = "FLIP"  # FLIP/APIC
    particle_randomness: float = 0.0
    particle_max: int = 0


class PhysicsSimulator:
    """Blender物理模拟器"""

    def __init__(self, blender_path: str = None):
        self.blender_path = blender_path or BLENDER_PATH
        self.config = PhysicsConfig()
        self._script_dir = os.path.dirname(os.path.abspath(__file__))

    def _build_blender_script(self, operations: List[str]) -> str:
        """构建Blender Python脚本"""
        script = f"""
import bpy
import math

# 清除场景
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# 设置重力
bpy.context.scene.gravity = {self.config.gravity}
bpy.context.scene.rigidbody_world.time_scale = {self.config.time_scale}
bpy.context.scene.rigidbody_world.steps_per_second = {self.config.steps_per_second}
bpy.context.scene.rigidbody_world.solver_iterations = {self.config.solver_iterations}

{chr(10).join(operations)}

# 保存
bpy.ops.wm.save_as_mainfile(filepath=r'{{output_path}}')
print("PHYSICS_DONE")
"""
        return script

    def create_rigid_body_scene(
        self,
        output_path: str,
        objects: List[Dict[str, Any]] = None,
        config: RigidBodyConfig = None,
        ground: bool = True,
    ) -> bool:
        """创建刚体模拟场景

        Args:
            output_path: 输出.blend文件路径
            objects: 对象列表 [{type, location, scale, rigid_body}]
            config: 刚体配置
            ground: 是否添加地面

        Returns:
            True成功，False失败
        """
        config = config or RigidBodyConfig()
        ops = []

        # 添加地面
        if ground:
            ops.append("""
# 添加地面
bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, 0))
ground = bpy.context.active_object
ground.name = "Ground"
ground.rigid_body.type = 'PASSIVE'
ground.rigid_body.collision_shape = 'BOX'
ground.rigid_body.friction = 0.8
ground.rigid_body.restitution = 0.2
""")

        # 添加对象
        if objects:
            for i, obj in enumerate(objects):
                obj_type = obj.get("type", "CUBE")
                location = obj.get("location", (0, 0, 2 + i * 2))
                scale = obj.get("scale", (1, 1, 1))
                rb_config = obj.get("rigid_body", {})

                if obj_type == "CUBE":
                    ops.append(f"bpy.ops.mesh.primitive_cube_add(size=2, location={location})")
                elif obj_type == "SPHERE":
                    ops.append(f"bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location={location})")
                elif obj_type == "CYLINDER":
                    ops.append(f"bpy.ops.mesh.primitive_cylinder_add(radius=1, depth=2, location={location})")
                elif obj_type == "CONE":
                    ops.append(f"bpy.ops.mesh.primitive_cone_add(radius=1, depth=2, location={location})")
                else:
                    ops.append(f"bpy.ops.mesh.primitive_cube_add(size=2, location={location})")

                ops.append(f"""
obj = bpy.context.active_object
obj.name = "Object_{i}"
obj.scale = {scale}
obj.rigid_body.type = 'ACTIVE'
obj.rigid_body.mass = {rb_config.get('mass', config.mass)}
obj.rigid_body.friction = {rb_config.get('friction', config.friction)}
obj.rigid_body.restitution = {rb_config.get('restitution', config.restitution)}
obj.rigid_body.linear_damping = {rb_config.get('linear_damping', config.linear_damping)}
obj.rigid_body.angular_damping = {rb_config.get('angular_damping', config.angular_damping)}
obj.rigid_body.collision_shape = '{rb_config.get('collision_shape', config.collision_shape)}'
""")

        # 烘焙模拟
        ops.append("""
# 烘焙刚体模拟
bpy.context.scene.frame_set(1)
if bpy.context.scene.rigidbody_world:
    bpy.ops.ptcache.free_bake_all()
    bpy.ops.ptcache.bake_all(bake=True)
""")

        script = self._build_blender_script(ops).replace("{{output_path}}", output_path)
        return self._run_blender(script, output_path)

    def create_cloth_simulation(
        self,
        output_path: str,
        cloth_size: float = 2.0,
        config: ClothConfig = None,
        wind: Tuple[float, float, float] = (0, 0, 0),
    ) -> bool:
        """创建布料模拟场景

        Args:
            output_path: 输出路径
            cloth_size: 布料尺寸
            config: 布料配置
            wind: 风力

        Returns:
            True成功，False失败
        """
        config = config or ClothConfig()
        ops = []

        # 添加布料平面
        ops.append(f"""
# 添加布料
bpy.ops.mesh.primitive_grid_add(x_subdivisions=32, y_subdivisions=32, size={cloth_size}, location=(0, 0, 5))
cloth = bpy.context.active_object
cloth.name = "Cloth"
cloth.modifiers.new(name="Cloth", type='CLOTH')
cloth.modifiers['Cloth'].settings.mass = {config.mass}
cloth.modifiers['Cloth'].settings.structural_stiffness = {config.structural_stiffness}
cloth.modifiers['Cloth'].settings.bending_stiffness = {config.bending_stiffness}
cloth.modifiers['Cloth'].settings.spring_damping = {config.spring_damping}
cloth.modifiers['Cloth'].settings.air_damping = {config.air_damping}
cloth.modifiers['Cloth'].collision_settings.collision_quality = {config.collision_quality}
cloth.modifiers['Cloth'].settings.effector_weights.wind = 1.0
""")

        # 添加风力
        if wind != (0, 0, 0):
            ops.append(f"""
# 添加风力场
bpy.ops.object.effector_add(type='WIND', location=(0, 0, 5))
wind_obj = bpy.context.active_object
wind_obj.name = "Wind"
wind_obj.field.strength = 10.0
wind_obj.field.flow = 1.0
wind_obj.rotation_euler = (0, 1.5708, 0)
""")

        # 添加碰撞体（球体）
        ops.append("""
# 添加碰撞球体
bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(0, 0, 2))
sphere = bpy.context.active_object
sphere.name = "Collision_Sphere"
sphere.modifiers.new(name="Collision", type='COLLISION')
""")

        script = self._build_blender_script(ops).replace("{{output_path}}", output_path)
        return self._run_blender(script, output_path)

    def create_particle_rain(
        self,
        output_path: str,
        particle_count: int = 1000,
        duration: int = 100,
    ) -> bool:
        """创建粒子雨场景

        Args:
            output_path: 输出路径
            particle_count: 粒子数量
            duration: 持续帧数

        Returns:
            True成功，False失败
        """
        ops = [f"""
# 添加粒子发射器
bpy.ops.mesh.primitive_plane_add(size=10, location=(0, 0, 10))
emitter = bpy.context.active_object
emitter.name = "Particle_Emitter"

# 添加粒子系统
particle_system = emitter.modifiers.new(name="ParticleSystem", type='PARTICLE_SYSTEM')
ps = emitter.particle_systems[-1]
ps.settings.count = {particle_count}
ps.settings.frame_start = 1
ps.settings.frame_end = {duration}
ps.settings.lifetime = 50
ps.settings.lifetime_random = 0.5
ps.settings.normal_factor = 0.0
ps.settings.factor_random = 0.5
ps.settings.physics_type = 'NEWTONIAN'
ps.settings.effector_weights.gravity = 1.0

# 添加地面碰撞
bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, 0))
ground = bpy.context.active_object
ground.name = "Ground_Collision"
ground.modifiers.new(name="Collision", type='COLLISION')
"""]

        script = self._build_blender_script(ops).replace("{{output_path}}", output_path)
        return self._run_blender(script, output_path)

    def _run_blender(self, script: str, output_path: str) -> bool:
        """运行Blender脚本"""
        import subprocess
        import tempfile

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # 写入临时脚本
        script_path = os.path.join(tempfile.gettempdir(), "blender_physics.py")
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(script)

        try:
            result = subprocess.run(
                [self.blender_path, "--background", "--python", script_path],
                capture_output=True, text=True, timeout=300
            )
            if "PHYSICS_DONE" in result.stdout or os.path.exists(output_path):
                logger.info(f"物理模拟场景已生成: {output_path}")
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
    """测试物理模拟器"""
    simulator = PhysicsSimulator()

    # 测试刚体场景
    output = r"D:\DobaoWork_Project\Ai_Video_Editor\test_output\rigid_body_test.blend"
    objects = [
        {"type": "CUBE", "location": (0, 0, 3), "rigid_body": {"mass": 2.0}},
        {"type": "SPHERE", "location": (2, 0, 5), "rigid_body": {"mass": 1.0, "restitution": 0.8}},
        {"type": "CYLINDER", "location": (-2, 1, 4), "rigid_body": {"mass": 1.5}},
    ]
    success = simulator.create_rigid_body_scene(output, objects=objects)
    print(f"刚体场景: {'成功' if success else '失败'}")

    # 测试布料场景
    output2 = r"D:\DobaoWork_Project\Ai_Video_Editor\test_output\cloth_test.blend"
    success2 = simulator.create_cloth_simulation(output2, wind=(5, 0, 0))
    print(f"布料场景: {'成功' if success2 else '失败'}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    main()
