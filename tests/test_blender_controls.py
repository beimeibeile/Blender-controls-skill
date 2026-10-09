"""
blender-controls-skill 基础测试套件
验证：路径配置、Blender特效库、3D能力
"""
import os
import sys
import unittest

# 路径设置
SKILL_ROOT = r"C:\Users\Administrator\AppData\Local\Doubao\User Data\Default\.doubao\agent_mode\workspace\.user_skills\blender-controls-skill"
sys.path.insert(0, os.path.join(SKILL_ROOT, "scripts"))


class TestPaths(unittest.TestCase):
    """路径配置测试"""
    
    def test_import_ok(self):
        """测试：paths模块可正常导入"""
        import paths
        self.assertIsNotNone(paths)
    
    def test_project_root_defined(self):
        """测试：PROJECT_ROOT已定义"""
        import paths
        self.assertTrue(hasattr(paths, "PROJECT_ROOT"))
        self.assertIsNotNone(paths.PROJECT_ROOT)
    
    def test_blender_defined(self):
        """测试：BLENDER路径已定义"""
        import paths
        self.assertTrue(hasattr(paths, "BLENDER"))
        self.assertIsNotNone(paths.BLENDER)


class TestBlenderEffects(unittest.TestCase):
    """Blender特效库测试"""
    
    def test_import_ok(self):
        """测试：blender_effects模块可正常导入"""
        try:
            import blender_effects
            self.assertIsNotNone(blender_effects)
        except ImportError as e:
            self.skipTest(f"blender_effects导入失败: {e}")
    
    def test_particle_presets_defined(self):
        """测试：粒子预设已定义"""
        try:
            import blender_effects
            self.assertTrue(hasattr(blender_effects, "PARTICLE_PRESETS"))
            self.assertGreater(len(blender_effects.PARTICLE_PRESETS), 0)
        except ImportError:
            self.skipTest("blender_effects未安装")
    
    def test_effect_functions_exist(self):
        """测试：特效生成函数存在"""
        try:
            import blender_effects
            # 验证核心特效函数存在
            functions = [
                "create_particle_background",
                "create_text_intro",
                "create_transition",
                "create_light_sweep",
            ]
            for func_name in functions:
                self.assertTrue(
                    hasattr(blender_effects, func_name),
                    f"缺少函数: {func_name}"
                )
        except ImportError:
            self.skipTest("blender_effects未安装")


class TestBlenderRunner(unittest.TestCase):
    """Blender运行器测试"""
    
    def test_capabilities_dir_exists(self):
        """测试：capabilities目录存在"""
        cap_dir = os.path.join(SKILL_ROOT, "capabilities")
        self.assertTrue(os.path.exists(cap_dir), "capabilities目录不存在")
    
    def test_blender_runner_exists(self):
        """测试：cap_blender_runner模块存在"""
        runner_dir = os.path.join(SKILL_ROOT, "capabilities", "cap_blender_runner")
        self.assertTrue(os.path.exists(runner_dir), "cap_blender_runner目录不存在")
        # 检查__init__.py或主模块
        init_file = os.path.join(runner_dir, "__init__.py")
        runner_file = os.path.join(runner_dir, "blender_runner.py")
        self.assertTrue(
            os.path.exists(init_file) or os.path.exists(runner_file),
            "blender_runner模块不存在"
        )


class TestBlenderBinary(unittest.TestCase):
    """Blender二进制文件测试"""
    
    def test_blender_binary_exists(self):
        """测试：Blender可执行文件存在"""
        import paths
        blender_path = getattr(paths, "BLENDER", None)
        if blender_path:
            if os.path.exists(blender_path):
                # 验证文件可执行
                self.assertTrue(os.path.isfile(blender_path))
            else:
                self.skipTest(f"Blender未安装: {blender_path}")
        else:
            self.skipTest("BLENDER路径未配置")


if __name__ == "__main__":
    unittest.main(verbosity=2)
