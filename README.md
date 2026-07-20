# 工业控制测试智能体

面向嵌入式控制板与 PLC I/O 系统的可扩展、可验证多智能体测试工程平台。

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

> 当前状态：M1 智能体运行时 V0 已完成 · 56 项测试通过 · 分支：`feat/agent-runtime-v0-hardening`

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

## 系统架构

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

## M1 智能体运行时 V0

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
- JSON 检查点；
- 图状态恢复；
- 完整 pytest CI。

当前未接入：

- 真实 LLM；
- MCP Server；
- PLC 或 MCU 真实硬件；
- Web 前端；
- 多智能体协作。

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

| 能力包 | 当前状态 | 领域审核要求 |
|---|---|---|
| `plc_start_feedback` | 草案（Draft） | 需要 PLC I/O 领域负责人审核信号、互锁、超时、故障判据和恢复方法 |
| `mcu_uart` | 草案（Draft） | 需要 MCU 领域负责人审核测试帧、引脚、波特率、故障判据和硬件检查方法 |

这些能力包当前用于架构验证和接口设计。

在对应领域负责人完成审核前，它们不代表正式工业测试规范，也不应作为真实设备自动测试依据。

## 下一阶段

下一阶段为 M2：PLC 模拟器与单领域诊断闭环。

平台负责人负责：

- 模拟器公共接口；
- 运行时接入；
- 假设（Hypothesis）和发现项（Finding）公共模型；
- 证据驱动的诊断循环；
- 评测框架。

PLC I/O 领域负责人负责：

- PLC 状态机业务语义；
- I/O 信号和点表；
- 互锁规则；
- 故障判据；
- 标准答案；
- 能力包审核。

M2 不接入真实 PLC，不实现自动修改 PLC 程序。

## 目录说明

| 目录 | 说明 |
|------|------|
| `apps/` | API 与 Web 工作台 |
| `src/industrial_test_agent/` | 核心领域、编排器、智能体运行时、技能、MCP、策略、执行器、证据 |
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
| [智能体架构](docs/agent-architecture.md) | 根图、子图、约束 |
| [领域模型](docs/domain-model.md) | 核心实体定义与关系 |
| [能力包规范](docs/capability-pack-specification.md) | 目录结构、生命周期 |
| [MCP 集成](docs/mcp-integration.md) | 关键链路与注册信息 |
| [安全边界](docs/safety-boundary.md) | 注册/计划/执行三阶段安全 |
| [职责边界](docs/ownership-boundary.md) | 平台、PLC I/O 与 MCU 领域的所有权和审核规则 |
| [团队工作包](docs/team-work-packages.md) | 三人分工与负责目录 |
| [ADR 记录](docs/adr/) | 8 条架构决策记录 |

## 运行检查

```bash
# 安装
pip install -e .

# 运行 M1 演示
python -m industrial_test_agent.agent_runtime.demo

# 运行全部测试
pytest
```
