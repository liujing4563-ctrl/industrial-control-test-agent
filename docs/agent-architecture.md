# Agent Architecture

## 根图

Case Executive Graph 负责整个案件生命周期。

### 主要节点

- initialize_case
- load_capabilities
- design_test
- route_domain
- propose_action
- policy_validate
- approval_if_required
- execute_action
- record_observation
- update_hypotheses
- diagnose
- replan / propose_change / escalate
- regression_test
- finalize_case

## 专业子图

### MCU Specialist Subgraph
- 分析 MCU 证据
- 更新 MCU 故障候选
- 选择 MCU 补测
- 输出结构化 ActionIntent

### PLC Specialist Subgraph
- 分析 PLC I/O 和互锁证据
- 更新 PLC 故障候选
- 选择 PLC 补测
- 输出结构化 ActionIntent

### Diagnosis/Critic Subgraph
- 检查证据充分性
- 校验专业 Agent 冲突
- 检查重复测试
- 推荐继续 / 升级 / 复核

## 约束

- Agent 只生成结构化输出。
- Agent 不能直接调用 MCP 或设备。
- Agent 不能修改 Evidence。
- 所有 Agent 共享统一 CaseState。
- LangGraph 只负责流程编排。
