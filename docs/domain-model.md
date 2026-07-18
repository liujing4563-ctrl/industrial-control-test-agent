# Domain Model

## 核心概念

- `CaseState`：案件当前事实、生命周期、证据引用、故障假设、审批与回归状态。
- `ActionIntent`：Agent 生成的请求动作与原因说明。
- `Observation`：Runner / MCP 返回的原始证据。
- `SkillManifest`：Skill 的元数据与输入/输出定义。
- `CapabilityManifest`：能力包的能力声明与调用契约。

## 设计原则

- 领域模型必须统一、可序列化、可校验。
- 各模块通过 Schema 交互，避免跨模块直接依赖具体实现。
- CaseState 数据为单一事实源，服务于所有 Agent 和工作流。
