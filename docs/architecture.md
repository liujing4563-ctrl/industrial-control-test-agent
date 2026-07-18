# Architecture

## 六层架构

1. Test Engineering Workspace
   - 提供测试案件视图、审批界面和结果查看。
   - 不直接执行设备操作。

2. Case & Workflow Orchestrator
   - 维护统一 CaseState。
   - 控制案件阶段、审批中断与回归闭环。
   - 负责工作流调度和状态持久化。

3. Multi-Agent Reasoning Layer
   - 包含 Executive、Specialist、Diagnosis/Critic Agent。
   - 仅生成结构化 ActionIntent 和推理结果。
   - 不直接调用设备工具。

4. Policy Engine & Test Runner
   - Policy Engine 校验 ActionIntent、权限与风险。
   - Test Runner 执行批准后的动作。
   - 所有写操作默认进入审批。

5. Skill Registry & MCP Gateway
   - Skill 注册与版本管理。
   - MCP Gateway 提供工具发现、输入输出校验、白名单和限流。

6. Evidence & Governance Plane
   - 保存原始 Observation 与 Evidence。
   - 记录审批、变更提案、回归结果。
   - 提供审计追踪与后续分析数据。

## 层间依赖

- 上层只能依赖下层，不反向。
- Agent 只能依赖领域模型、Skill 栈和 Runtime 抽象。
- Policy、Runner、MCP Gateway 不能依赖 Agent 推理实现。

## 数据流

1. Agent 读取 CaseState，生成 ActionIntent。
2. Orchestrator 接收 ActionIntent，进入 Policy 校验。
3. Policy 通过后交给 Runner。
4. Runner 调用 MCP Gateway，执行 Test Service。
5. Test Service 返回 Observation，写入 Evidence Store。
6. Orchestrator 更新 CaseState、假设和回归状态。

## 控制流

- Agent 发起请求，Orchestrator 判断是否继续、中断或审批。
- 所有写操作进入审批节点；人工批准后恢复执行。
- 当 Evidence 足够或达到终止条件时，案件结束。

## 失败处理

- 任何节点失败后记录 Failure Event。
- 如果 Runner/设备执行失败，进入 replan 或 escalate。
- 如果审批拒绝，案件进入人工中断状态。

## 人工审批

- 真实改设备前必须生成 ChangeProposal。
- 审批通过后，Runner 执行由 MCP Gateway 调用。
- 审批结果写回 CaseState 与 Evidence。

## 回归闭环

- 变更执行后自动触发回归测试。
- 回归结果作为 Evidence 记录并指向原始 ChangeProposal。
- 回归通过后关闭案件。
