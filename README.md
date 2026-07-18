# industrial-control-test-agent

工业控制测试代理框架基线。

## 项目目标

构建一个可审计、可扩展、基于 Agent 的工业测试与诊断平台。项目首阶段聚焦于架构基线和数据契约，不直接开发生产 Agent 逻辑。

## 架构基线

- `apps/`：运行 API 和 Web 工作台。
- `src/industrial_test_agent/`：核心框架实现。
- `capability_packs/`：测试能力包。
- `schemas/`：JSON Schema 数据契约。
- `simulators/`：仿真环境。
- `tests/`：多层次测试目录。
- `evals/`：评估场景与报告。
- `docs/`：架构、域模型、安全、Skill 规范和 MCP 集成文档。

## 第一阶段规则

1. Agent 不能直接操作设备；必须生成 ActionIntent，经 Orchestrator、Policy、Runner、MCP 驱动。
2. 所有 Agent 共享统一 CaseState，禁止各自维护独立事实副本。
3. Agent 与 Skill 分离：Agent 负责推理，Skill 封装 SOP 和判据。
4. 原始证据仅追加，不允许 Agent 修改。
5. MCP 默认不可信，必须做输入/输出校验、白名单、超时、限流和审批。
6. 修复必须通过 Change Proposal + 工程师审批 + Runner 执行 + 回归验证。

## 现阶段状态

已完成：

- 创建架构目录结构。
- 添加核心 schema 占位文件。
- 生成初版架构文档。

后续：

- 等待仓库授权后推送 `architecture/bootstrap-v0` 分支。
- 继续完善数据模型、Domain 和 Orchestrator 文档。
