# Skill Specification

## Skill 与 Agent 的分工

- Agent：负责推理、决策、案件推进。
- Skill：封装 SOP、故障经验、证据要求和判据。
- MCP：提供外部工具与数据能力。
- Runner：执行已批准的测试动作。

## Skill 设计要点

- Skill 不直接调用设备或 MCP 客户端。
- Skill 输出应遵循 `SkillManifest` 定义。
- Skill 注册、加载和校验由独立模块负责。

## 校验与治理

- Skill 需声明输入、输出、允许工具。
- Skill 运行前必须通过版本和准入校验。
- 任何 Skill 结果都应可追溯到 Evidence ID。
