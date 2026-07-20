# 智能体架构

## 根图

案件执行图（Case Executive Graph）负责整个案件生命周期。

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

### MCU 专业子图
- 分析 MCU 证据
- 更新 MCU 故障候选
- 选择 MCU 补测
- 输出结构化 ActionIntent

### PLC 专业子图
- 分析 PLC I/O 和互锁证据
- 更新 PLC 故障候选
- 选择 PLC 补测
- 输出结构化 ActionIntent

### 诊断与审查子图
- 检查证据充分性
- 校验专业智能体冲突
- 检查重复测试
- 推荐继续 / 升级 / 复核

## 约束

- 智能体只生成结构化输出。
- 智能体不能直接调用 MCP 或设备。
- 智能体不能修改 Evidence。
- 所有智能体共享统一 CaseState。
- LangGraph 只负责流程编排。
