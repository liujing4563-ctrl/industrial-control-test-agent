# industrial-control-test-agent

Extensible and Verifiable Multi-Agent Test Engineering Platform for Embedded Boards and PLC I/O Systems.

---

## 快速开始

```bash
# 安装依赖
pip install -e ".[dev]"

# 编译检查
python -m compileall src

# 运行测试
pytest -q
```

> 当前状态：**47 passed** ✅  · 分支：`main`  · 阶段：**M1 — Agent Runtime V0**

---

## 演示

```bash
python -m industrial_test_agent.agent_runtime.demo
```

预期输出：

```
case initialized
action proposed
policy allowed
mock runner executed
observation recorded
evidence appended: ev-xxx
case completed
final state: stage=completed
reason=Case completed — 3 evidence records collected (threshold=3)
```

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

## 当前阶段 — M1: Agent Runtime V0

已实现确定性闭环执行链路：

```
CaseState → Mock Agent → ActionIntent → Policy Validator
→ Mock Runner → Observation → Evidence Store → CaseState 更新 → 结束
```

### 已交付模块

| 模块 | 文件 | 说明 |
|------|------|------|
| Domain | `domain/` | CaseState, ActionIntent, Observation, Evidence, Hypothesis, Finding |
| Agent | `agents/mock_agent.py` | 确定性 ActionIntent 生成器 (无 LLM) |
| Policy | `policy/validator.py` | 4 条规则：白名单、参数校验、调用预算、写操作审批 |
| Runner | `runner/mock_runner.py` | 3 个 PLC 工具：read_interlock, read_signal, wait_feedback |
| Evidence | `evidence/in_memory_store.py` | 只追加内存存储，不暴露 update/delete |
| Runtime | `agent_runtime/` | GraphRunner, CaseGraphState, 7 个节点, demo |

### 能力包

| 能力包 | 领域 | 工具数 | 故障场景 |
|--------|------|--------|---------|
| `capability_packs/mcu_uart/` | MCU | 5 (heartbeat, uart_frame, gpio, i2c…) | 4 (心跳/波特率/帧丢失/GPIO) |
| `capability_packs/plc_start_feedback/` | PLC I/O | 5 (信号读写, 互锁, 反馈, 复位) | 4 (互锁/无反馈/映射/复位) |

### 本阶段边界

- ✅ 确定性 Runner + Policy + Evidence 闭环
- ✅ 能力包骨架 (manifest + workflow + faults + examples)
- ❌ 不接入真实 LLM、MCP、PLC、MCU 或数据库
- ❌ 不实现 Web 页面和完整设备驱动

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
