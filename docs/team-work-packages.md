# Team Work Packages

## 负责人一：系统负责人

职责：
- 统筹顶层架构与设计
- 定义领域模型与 CaseState
- 设计 Agent Runtime 与根图
- 定义 Policy、Runner、Evidence、MCP 边界
- 负责系统集成、Web/API 与比赛材料

负责目录：
- domain/
- orchestrator/
- agent_runtime/
- agents/executive/
- agents/diagnosis_critic/
- skills/registry/
- mcp/gateway/
- policy/
- runner/
- evidence/
- governance/
- apps/api/
- apps/web/
- evals/
- competition/

## 负责人二：MCU 测试成员

职责：
- MCU 测试领域说明与能力包
- MCU Specialist 输入输出规范
- MCU 模拟器与适配器接口定义
- MCU 测试场景与故障分类

负责目录：
- agents/specialists/mcu/
- capability_packs/mcu_uart/
- simulators/mcu/
- adapters/mcu/
- hardware/mcu/
- tests/mcu/
- evals/scenarios/mcu/

## 负责人三：PLC I/O 测试成员

职责：
- PLC I/O 测试领域说明与能力包
- PLC Specialist 输入输出规范
- PLC 仿真与适配器接口定义
- PLC 测试场景与故障分类

负责目录：
- agents/specialists/plc_io/
- capability_packs/plc_start_feedback/
- simulators/plc_io/
- adapters/plc_io/
- hardware/plc_io/
- tests/plc_io/
- evals/scenarios/plc_io/
