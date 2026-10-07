# Blender Controls Skill - 使用规则

## AI调用规则
1. 初始化前必须检查is_available()，Blender不可用时不得调用渲染方法
2. blender_path应从环境变量BLENDER_PATH读取，不得硬编码
3. 单次渲染时长不超过30秒，长视频需分段渲染后合成
4. 批量渲染任务不超过10个，超出需分批
5. 渲染前必须检查输出目录可写
6. 与ai-video-editor集成时通过BlenderControls统一入口，不得直接import blender_runner
7. 渲染失败必须重试最多2次，记录错误日志
