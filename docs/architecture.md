# Architecture

## 目标

本档描述项目第一版架构基线，并锁定核心依赖方向、数据契约和安全边界。

## 目录结构

```
industrial-control-test-agent/
├─ apps/
│  ├─ api/
│  └─ web/
├─ src/
│  └─ industrial_test_agent/
│     ├─ domain/
│     ├─ orchestrator/
│     ├─ agents/
│     ├─ skills/
│     ├─ mcp/
│     ├─ policy/
│     ├─ runner/
│     ├─ adapters/
│     ├─ evidence/
│     ├─ governance/
│     └─ reporting/
├─ capability_packs/
├─ schemas/
├─ simulators/
├─ tests/
├─ evals/
├─ docs/
├─ pyproject.toml
├─ README.md
└─ .gitignore
```

## 依赖方向

代码依赖只能从上往下：

```
Web/API
   ↓
Orchestrator
   ↓
Agent Reasoning Services
   ↓
ActionIntent
   ↓
Policy Engine + Test Runner
   ↓
MCP Gateway + Device Adapters
   ↓
Simulator / MCU / PLC / Test Tools
```

横向贯穿：

```
Domain Model
Evidence Store
Governance
Schemas
```

## 基架规则

1. Agent 不直接操作设备。
2. 多 Agent 共享统一 CaseState。
3. Skill 与 Agent 分离。
4. 原始证据不可被 Agent 修改。
5. MCP 默认不可信。
6. 修复不等于直接改设备。

## 第一阶段重点

- 冻结目录结构。
- 完成 `CaseState`、`ActionIntent`、`Observation` 数据契约。
- 不立即写五个 Agent；先搭建框架与文档。
