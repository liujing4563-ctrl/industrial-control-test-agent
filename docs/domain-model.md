# 领域模型

## 项目（Project）
- 含义：测试项目或验证任务集合。
- 关键字段：project_id、name、description、owner、created_at。
- 生命周期：创建 → 规划 → 执行 → 验收。
- 关系：包含 Requirement、TestCase、CaseState。

## 需求（Requirement）
- 含义：测试需求或验收标准。
- 关键字段：requirement_id、description、priority、status。
- 生命周期：定义 → 验证 → 关闭。
- 谁能创建：测试工程师。
- 谁能修改：系统负责人、验证工程师。

## 测试用例（TestCase）
- 含义：具体测试用例。
- 关键字段：test_case_id、description、expected_result、domain、status。
- 关系：属于 Requirement，生成 Observation。

## 测试执行（TestRun）
- 含义：一次测试执行。
- 关键字段：run_id、case_id、start_time、end_time、outcome。
- 关系：关联 TestCase、Observation、Evidence。

## 案件状态（CaseState）
- 含义：案件当前事实与生命周期。
- 关键字段：case_id、current_phase、evidence_ids、hypotheses、approval_status、regression_status。
- 谁能创建：Orchestrator。
- 谁能读取：所有智能体与工作流。
- 谁能修改：Orchestrator 与 Policy。

## 动作意图（ActionIntent）
- 含义：智能体提出的结构化执行请求。
- 关键字段：intent_id、case_id、action_type、action_details、reason、requested_by、status。
- 谁能创建：智能体。
- 谁能修改：Policy 或审批模块。

## 观测结果（Observation）
- 含义：执行器或 MCP 返回的原始结果。
- 关键字段：observation_id、case_id、source、payload、schema_id、timestamp。
- 谁能创建：执行器或 MCP。
- 只能追加，不可修改。

## 证据（Evidence）
- 含义：原始证据记录。
- 关键字段：evidence_id、observation_id、case_id、source、content_hash、created_at。
- 谁能创建：证据存储。
- 只能追加。

## 假设（Hypothesis）
- 含义：故障假设或诊断结论。
- 关键字段：hypothesis_id、case_id、description、confidence、status。
- 谁能创建：智能体。
- 谁能修改：诊断与审查智能体或编排器。

## 发现项（Finding）
- 含义：确认的故障或问题点。
- 关键字段：finding_id、case_id、summary、severity、status。
- 谁能创建：智能体或诊断模块。
- 谁能修改：验证工程师。

## 变更提案（ChangeProposal）
- 含义：对设备或配置的修改提议。
- 关键字段：proposal_id、case_id、action_intent_id、requested_by、reason、status。
- 谁能创建：智能体。
- 谁能修改：人工审批模块。

## 审批（Approval）
- 含义：人工审批记录。
- 关键字段：approval_id、proposal_id、case_id、approver、decision、comments。
- 谁能创建：审核人员。

## 回归执行（RegressionRun）
- 含义：回归测试执行记录。
- 关键字段：regression_id、case_id、triggered_by、outcome、evidence_ids。
- 谁能创建：执行器。

## 能力包（CapabilityPack）
- 含义：测试能力包元数据与规则。
- 关键字段：capability_pack_id、name、version、domain、risk_level。

## 工具能力（ToolCapability）
- 含义：MCP 工具能力声明。
- 关键字段：tool_id、name、transport、input_schema、output_schema、permissions。
