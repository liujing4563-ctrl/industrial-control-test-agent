# 工业控制测试智能体

面向嵌入式控制板与 PLC I/O 系统的可扩展、可验证多智能体测试工程平台。

---

## 快速开始

```bash
# 安装依赖
pip install -e ".[dev]"

# 静态检查
ruff check .

# 契约漂移检查
python -m industrial_test_agent.schemas.generate --check

# 编译检查
python -m compileall src

# 运行测试
pytest -q
```

> 当前分支状态：M1 智能体运行时 V0、恢复可靠性强化与可执行契约统一已完成 · 121 项测试通过 · CI 验证 Python 3.11/3.12

---

## 演示

```bash
python -m industrial_test_agent.agent_runtime.demo
```

预期输出：

```
case initialized
action proposed: plc.read_interlock
policy decision: allowed
mock runner executed
observation recorded
evidence appended: ev-xxx
case completed
final state: stage=completed
reason=Case completed - 1 evidence record collected (threshold=1)
```

---

## 目标系统架构

下图描述项目目标架构。当前仓库只实现了 M1 确定性 Runtime
及其公共契约，未实现的组件见后文“当前未接入”。

```
┌──────────────────────────────────────────────┐
│                测试工程工作台                 │  ← 测试案件视图与审批
├──────────────────────────────────────────────┤
│              案件与工作流编排器               │  ← CaseState · 工作流 · 中断/回归
├──────────────────────────────────────────────┤
│               多智能体推理层                  │  ← 执行 · MCU/PLC 专业 · 审查智能体
│      （仅生成 ActionIntent，不调用设备）        │
├──────────────────────────────────────────────┤
│              策略引擎与测试执行器              │  ← 校验 · 审批 · 安全执行
├──────────────────────────────────────────────┤
│              技能注册中心与 MCP 网关           │  ← 工具发现 · 白名单 · 限流
├──────────────────────────────────────────────┤
│                证据与治理平面                 │  ← 只追加证据 · 审计链 · 变更记录
└──────────────────────────────────────────────┘
```

**核心原则：**
- 智能体不能直接调用设备
- 共享 `CaseState`，只追加 `Evidence`
- 技能不等于智能体，人工审批后才能修改设备
- 领域模型独立于 LangGraph 运行时

---

## M1 智能体运行时 V0（已完成）

当前版本已经完成平台最小可执行闭环：

```text
动作意图（ActionIntent）
→ 策略校验
→ 模拟执行器
→ 观测结果（Observation）
→ 只追加证据
→ 案件状态（CaseState）转换
→ 重规划或结束
```

已实现：

- ActionIntent 结构化动作请求；
- 工具白名单校验；
- 参数 Schema 校验；
- 风险等级判断；
- 调用预算控制；
- 执行器失败后进入重规划；
- Observation 标准化返回；
- Evidence 只追加存储；
- Evidence ID 防重复；
- 读取副本隔离，外部修改不会污染存储记录；
- Evidence 幂等写入与冲突检测；
- 带版本、图状态和 Evidence 快照的 Checkpoint Envelope；
- 检查点版本、字段、状态与节点组合完整校验；
- 恢复后 Evidence 引用完整性校验；
- 检查点重复恢复不新增 Evidence；
- 已产生 Observation 的动作不会在恢复时重复执行；
- Runner 异常统一转换为失败 Observation；
- `execution_failed` 与 `test_failed` 分类及重规划；
- 异常输出中的常见凭据和本机路径脱敏；
- Pydantic 模型作为 JSON Schema 唯一来源；
- Runner、Policy、Evidence、Checkpointer 公共协议；
- Capability Pack Manifest 实际校验；
- JSON Schema 漂移检查；
- 完整 pytest CI。

当前未接入：

- LangGraph 正式运行时；
- 真实 LLM；
- MCP Server；
- PLC 完整领域闭环；
- MCU 完整领域闭环；
- PLC 或 MCU 真实硬件；
- Web 前端；
- 数据库；
- 多智能体协作。

### 当前恢复边界

当前 Runtime 可以防止检查点重放造成的重复 Mock Runner 调用和重复 Evidence。

真实外部设备仍存在一个已知窗口：物理动作可能已经完成，但进程在 Observation 持久化前崩溃。未来真实设备 Adapter 和 Runner 必须使用外部幂等键、执行回执或持久化事务日志解决这一问题。

## 职责边界

### 平台核心负责人

负责：

- 领域模型；
- CaseState；
- ActionIntent；
- Observation；
- Evidence；
- 智能体运行时；
- 编排器；
- 策略引擎；
- 测试执行器；
- 检查点；
- 技能注册中心；
- MCP 网关；
- 评测框架；
- 系统集成。

### PLC I/O 领域负责人

负责：

- PLC 信号语义；
- I/O 点表；
- 互锁逻辑；
- 启停与反馈流程；
- PLC 故障分类；
- PLC 诊断判据；
- PLC 模拟器业务行为；
- PLC Capability Pack 专业内容；
- PLC 场景标准答案。

### MCU 领域负责人

负责：

- UART、GPIO、I²C 测试方法；
- 板卡心跳和状态定义；
- MCU 故障分类；
- MCU 诊断判据；
- MCU 模拟器业务行为；
- MCU Capability Pack 专业内容；
- MCU 场景标准答案；
- 真实开发板验证流程。

平台负责人可以创建领域目录、Schema、模板和 Mock 接口，但不能独自冻结领域业务规则。

## 能力包状态

仓库当前包含两个能力包草案：

| 能力包 | 状态 | 领域审核 | 硬件验证 |
|---|---|---|---|
| `plc_start_feedback` | `draft` | `pending` | `not_started` |
| `mcu_uart` | `draft` | `pending` | `not_started` |

这些能力包当前仅用于架构验证和接口设计。PLC I/O 领域负责人仍需审核信号、互锁、超时、故障判据和恢复方法；MCU 领域负责人仍需审核测试帧、引脚、波特率、故障判据和硬件检查方法。

在对应领域负责人完成审核前，它们不代表正式工业测试规范，也不应作为真实设备自动测试依据。

## 近期工程顺序

M1 完成后不直接进入 PLC 或 MCU 业务实现。当前固定顺序为：

```text
Ruff 基线清理（已完成）
→ 统一可执行契约（已完成）
→ 领域接入公共接口（下一阶段）
→ 通用评测框架 V0
→ PLC 与 MCU 领域实现
```

### 1. Ruff 基线清理（已完成）

已使用独立 PR 清理 Ruff 基线，并将 `ruff check .` 加入 CI。该工作只涉及工程治理，没有修改业务逻辑或领域内容。

### 2. 统一可执行契约（已完成）

平台公共契约已经统一：

- 以 Pydantic 模型作为可执行契约唯一来源；
- 自动生成 JSON Schema 并增加漂移测试；
- 统一 Runner、Policy、Evidence 和 Checkpointer 接口；
- 统一 Capability Pack Manifest 格式，但不修改专业参数；
- 清理或隔离失效的旧 Runtime/LangGraph 占位；
- 明确 CI 当前验证 Python 3.11 和 3.12；
- 增加真正的契约测试。

下一阶段只建立领域接入公共接口。PLC 与 MCU 领域负责人继续负责专业事实审核；在领域审核前，不冻结信号、互锁、波特率、引脚、故障判据、恢复方法或领域标准答案。

## 目录说明

| 目录 | 说明 |
|------|------|
| `apps/` | API 与 Web 工作台 |
| `src/industrial_test_agent/` | 核心领域、编排器、智能体运行时、技能、MCP、策略、执行器、证据 |
| `capability_packs/` | 能力包定义 |
| `schemas/` | 由 Pydantic 模型生成的 JSON Schema 数据契约 |
| `simulators/` | 仿真环境占位 |
| `tests/` | 单元、契约、集成、安全和端到端测试 |
| `docs/` | 架构、域模型、安全、能力包、MCP 集成、团队工作包和 ADR |

## 关键文档

| 文档 | 内容 |
|------|------|
| [项目章程](docs/project-charter.md) | 背景、痛点、产品目标、MVP、非目标 |
| [系统上下文](docs/system-context.md) | 外部角色与系统边界 |
| [架构设计](docs/architecture.md) | 六层架构、数据流、控制流、失败处理 |
| [智能体架构](docs/agent-architecture.md) | 根图、子图、约束 |
| [领域模型](docs/domain-model.md) | 核心实体定义与关系 |
| [能力包规范](docs/capability-pack-specification.md) | 目录结构、生命周期 |
| [MCP 集成](docs/mcp-integration.md) | 关键链路与注册信息 |
| [安全边界](docs/safety-boundary.md) | 注册/计划/执行三阶段安全 |
| [职责边界](docs/ownership-boundary.md) | 平台、PLC I/O 与 MCU 领域的所有权和审核规则 |
| [团队工作包](docs/team-work-packages.md) | 三人分工与负责目录 |
| [ADR 记录](docs/adr/) | 架构决策记录 |

## 运行检查

```bash
# 安装
pip install -e ".[dev]"

# 静态检查
ruff check .

# 契约漂移检查
python -m industrial_test_agent.schemas.generate --check

# 运行 M1 演示
python -m industrial_test_agent.agent_runtime.demo

# 运行全部测试
pytest
```
