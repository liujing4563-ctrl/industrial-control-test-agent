# 领域模型

本文件区分当前可执行契约与目标架构对象。只有列入“当前可执行模型”的
Pydantic 模型才是当前代码契约；项目、需求、测试用例、审批和回归等对象
仍属于后续路线图。

## 当前可执行模型

## 案件状态（CaseState）
- 含义：案件当前事实与生命周期。
- 关键字段：case_id、goal、stage、next_node、action_ids、observation_ids、evidence_ids、hypotheses、findings、remaining_steps、termination_reason、created_at、updated_at、metadata。
- 当前由确定性 Runtime 创建和更新。

## 动作意图（ActionIntent）
- 含义：智能体提出的结构化执行请求。
- 关键字段：action_id、case_id、capability_id、arguments、risk_level、requested_by、reason、created_at、idempotency_key、metadata。
- `risk_level` 是请求方声明，Policy 最终以 ToolCapability 的风险为准。

## 观测结果（Observation）
- 含义：执行器返回或 Runtime 标准化后的执行结果。
- 关键字段：observation_id、case_id、action_id、tool_id、status、success、data、error_code、error_message、received_at、source_type、metadata。
- 状态区分 policy_rejected、execution_failed、test_failed 和 succeeded。

## 证据（Evidence）
- 含义：由证据存储根据 Observation 生成的只追加记录。
- 关键字段：evidence_id、case_id、observation_id、action_id、evidence_type、payload、source、content_hash、created_at、idempotency_key、metadata。
- 顶层模型不可赋值；嵌套读取隔离由 Evidence Store 保证。

## 假设（Hypothesis）
- 含义：故障假设或诊断结论。
- 关键字段：hypothesis_id、case_id、statement、confidence、supporting_evidence_ids、contradicting_evidence_ids、status、created_at、updated_at、metadata。
- confidence 范围为 0 到 1。

## 发现项（Finding）
- 含义：确认的故障或问题点。
- 关键字段：finding_id、case_id、title、description、severity、status、evidence_ids、hypothesis_ids、created_at、closed_at、metadata。
- 只有允许关闭的状态才能包含 closed_at。

## 能力包清单（CapabilityPackManifest）
- 含义：测试能力包元数据与规则。
- 关键字段：schema_version、pack_id、name、domain、version、status、description、entrypoints、ownership、review、safety、metadata。
- 当前 Manifest 仅通过平台结构校验，不代表领域内容获批。

## 工具能力（ToolCapability）
- 含义：Runner 和 Policy 共享的工具能力声明。
- 关键字段：capability_id、display_name、description、input_schema、risk_level、requires_approval、side_effect_type、timeout_seconds、retry_policy、tags、metadata。

## 后续路线图对象

Project、Requirement、TestCase、TestRun、ChangeProposal、Approval 和
RegressionRun 尚未成为当前可执行 Pydantic 契约。实现前不得把本文中的
概念说明当作稳定接口。

## 契约约定

- Pydantic 模型是可执行契约唯一来源。
- Python、YAML 和 JSON 字段统一使用 `snake_case`。
- 未声明字段默认拒绝。
- `schemas/` 中的 JSON Schema 由模型生成并通过 CI 检查漂移。
- 新数据默认只输出 `snake_case`；旧 M1 Checkpoint 通过版本化迁移读取。
