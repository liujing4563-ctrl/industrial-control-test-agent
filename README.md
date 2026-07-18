# industrial-control-test-agent

Extensible and Verifiable Multi-Agent Test Engineering Platform for Embedded Boards and PLC I/O Systems.

---

## 快速开始

```bash
# 安装依赖
pip install -e .

# 编译检查
PYTHONPATH=src python -m compileall src

# 运行测试
PYTHONPATH=src python -m pytest -q tests/unit
```

> 当前状态：**8 passed** ✅  · 分支：`main`  · 阶段：V1 架构基线

---

## 系统架构

```
┌──────────────────────────────────────────────┐
│         Test Engineering Workspace           │  ← 测试案件视图 & 审批
├──────────────────────────────────────────────┤
│       Case & Workflow Orchestrator           │  ← CaseState · 工作流 · 中断/回归
├──────────────────────────────────────────────┤
│      Multi-Agent Reasoning Layer             │  ← Executive · MCU/PLC Specialist · Critic
│      (仅生成 ActionIntent，不调设备)           │
├──────────────────────────────────────────────┤
│      Policy Engine & Test Runner             │  ← 校验 · 审批 · 安全执行
├──────────────────────────────────────────────┤
│      Skill Registry & MCP Gateway            │  ← 工具发现 · 白名单 · 限流
├──────────────────────────────────────────────┤
│      Evidence & Governance Plane             │  ← 只追加证据 · 审计链 · 变更记录
└──────────────────────────────────────────────┘
```

**核心原则：**
- Agent 不能直接调用设备
- 共享 `CaseState`，只追加 `Evidence`
- Skill ≠ Agent，人审批后才能改设备
- 领域模型独立于 LangGraph 运行时

---

## 当前阶段

本阶段建立顶层设计、系统架构基线、领域模型、Schema 和接口骨架。
不实现真实 Agent、LangGraph、MCP 或设备驱动。

## 目标

构建一个可扩展、可验证的工业测试平台基线，支持 MCU 和 PLC I/O 两个领域，并明确多 Agent、Skill、Policy、Runner、Evidence 的边界。

## 目录说明

| 目录 | 说明 |
|------|------|
| `apps/` | API 与 Web 工作台 |
| `src/industrial_test_agent/` | 核心领域、Orchestrator、Agent Runtime、Skill、MCP、Policy、Runner、Evidence |
| `capability_packs/` | 能力包定义 |
| `schemas/` | JSON Schema 数据契约 |
| `simulators/` | 仿真环境占位 |
| `tests/` | 单元、契约、集成、安全和端到端测试 |
| `docs/` | 架构、域模型、安全、能力包、MCP 集成、团队工作包和 ADR |

## 关键文档

| 文档 | 内容 |
|------|------|
| [项目章程](docs/project-charter.md) | 背景、痛点、产品目标、MVP、非目标 |
| [系统上下文](docs/system-context.md) | 外部角色与系统边界 |
| [架构设计](docs/architecture.md) | 六层架构、数据流、控制流、失败处理 |
| [Agent 架构](docs/agent-architecture.md) | 根图、子图、约束 |
| [领域模型](docs/domain-model.md) | 核心实体定义与关系 |
| [能力包规范](docs/capability-pack-specification.md) | 目录结构、生命周期 |
| [MCP 集成](docs/mcp-integration.md) | 关键链路与注册信息 |
| [安全边界](docs/safety-boundary.md) | 注册/计划/执行三阶段安全 |
| [团队工作包](docs/team-work-packages.md) | 三人分工与负责目录 |
| [ADR 记录](docs/adr/) | 8 条架构决策记录 |

## 本阶段边界

- 仅完成架构基线、文档、契约与接口骨架
- 不接入真实 LLM、MCP、PLC、MCU 或数据库
- 不实现 Web 页面和完整设备驱动

## 运行检查

```bash
# 编译验证
PYTHONPATH=src python -m compileall src

# 运行全部测试
PYTHONPATH=src python -m pytest -q tests/unit
```
