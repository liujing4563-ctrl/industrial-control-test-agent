# 项目总体战略与执行规划 V0.1

## 一、项目最终定位

### 项目名称

> **面向嵌入式控制板与PLC I/O验证的可扩展可验证多智能体测试工程平台**

英文工作名：

> **Extensible and Verifiable Multi-Agent Test Engineering Platform for Embedded Boards and PLC I/O Systems**

GitHub仓库：

```text
industrial-control-test-agent
```

参赛定位：

> 中国研究生人工智能创新大赛开放赛题一：生成式大语言模型与智能体。

### 一句话定义

平台将测试工程师的SOP、故障经验、判定规则和回归要求封装为可版本化的测试能力包，通过MCP接入板卡、PLC、模拟器、日志和测试工具；多个专业Agent围绕统一案件状态完成测试设计、故障诊断和动态补测，所有真实操作均经过确定性策略引擎执行，最终形成“需求—测试—证据—缺陷—变更—回归”的完整闭环。

---

# 二、项目解决的真实问题

目标用户是：

- 单片机控制板硬件测试工程师；
- PLC I/O自动化测试工程师；
- 嵌入式验证工程师；
- 工业设备联调工程师；
- 测试负责人和实验室管理人员。

项目主要解决五类问题。

### 1. 测试经验难以复用

资深工程师知道：

- 先检查什么；
- 哪些故障容易混淆；
- 出现异常后下一步测什么；
- 哪些数据足以证明根因；
- 修复后需要回归哪些功能。

但这些经验通常散落在文档、脚本和个人经验中。

平台通过测试能力包将其标准化沉淀。

### 2. 测试用例依赖人工编写

工程师需要根据需求、点表、协议和设备配置手工编写测试步骤，容易遗漏边界条件和异常场景。

### 3. 测试执行重复

GPIO、UART、I²C、DI/DO、Modbus、互锁和反馈测试中存在大量重复操作。

### 4. 故障定位依赖资深人员

传统自动化测试通常只能报告失败，不能根据新证据自主决定下一步补测内容。

### 5. 缺少完整证据链

很多系统无法回答：

> 哪条需求由哪条测试验证，测试产生了什么证据，发现了什么问题，修改后进行了哪些回归测试。

---

# 三、战略边界

## 长期平台愿景

长期可以支持：

- MCU控制板；
- PLC及远程I/O；
- BIOS和嵌入式系统验证；
- 工业通信网关；
- 测试仪器；
- 仿真器；
- 企业测试管理系统；
- 团队自定义Skill和MCP服务。

## 比赛MVP范围

比赛版本只保证以下内容。

### 两类验证对象

1. MCU/嵌入式控制板；
2. PLC I/O控制系统。

### 两个能力包

1. `MCU UART/GPIO测试能力包`；
2. `PLC启停、互锁与反馈测试能力包`。

### 两套执行环境

1. MCU模拟器或一块公开型号开发板；
2. PLC I/O软件模拟器。

### 一个核心闭环

```text
需求输入
→ 测试设计
→ 安全审核
→ 工具执行
→ 证据采集
→ 故障诊断
→ 自主补测
→ 变更建议
→ 人工批准
→ 回归测试
→ 证据报告
```

## 比赛前明确不做

- 支持所有型号MCU和PLC；
- 运行用户上传的任意Python或Shell代码；
- 公共Skill市场；
- 直接控制真实产线；
- 自动绕过安全互锁；
- 自动修改PLC程序或固件；
- 完整企业多租户系统；
- 示波器波形视觉诊断；
- 五个以上复杂Agent自由对话；
- 任意PDF完全自动转换成设备配置。

---

# 四、软件总体架构

```text
┌──────────────────────────────────────┐
│ 1. Test Engineering Workspace       │
│ 项目、需求、用例、案件、缺陷、回归、报告 │
└──────────────────┬───────────────────┘
                   ↓
┌──────────────────────────────────────┐
│ 2. Case & Workflow Orchestrator      │
│ 案件状态、流程阶段、路由、预算、终止条件  │
└──────────────────┬───────────────────┘
                   ↓
┌──────────────────────────────────────┐
│ 3. Multi-Agent Reasoning Layer      │
│ Executive / MCU / PLC / Diagnosis   │
└──────────────────┬───────────────────┘
                   ↓ ActionIntent
┌──────────────────────────────────────┐
│ 4. Policy Engine & Test Runner       │
│ 权限、参数、审批、执行、超时、恢复、重试   │
└──────────────────┬───────────────────┘
                   ↓
┌──────────────────────────────────────┐
│ 5. Skill Registry & MCP Gateway      │
│ 能力包、工具发现、适配器、模拟器、设备接口  │
└──────────────────┬───────────────────┘
                   ↓
┌──────────────────────────────────────┐
│ 6. Evidence & Governance Plane       │
│ 原始证据、版本快照、审计、追踪、自动评测    │
└──────────────────────────────────────┘
```

---

# 五、多Agent架构冻结方案

比赛首版采用四个Agent。

## 1. Executive Agent

负责整个案件生命周期：

- 理解测试目标；
- 创建案件；
- 选择测试能力包；
- 决定调用哪个专业Agent；
- 维护当前阶段；
- 控制工具调用预算；
- 决定继续、结束或转人工；
- 确保原始测试目标最终得到验证。

## 2. MCU Specialist Agent

负责：

- GPIO；
- UART；
- I²C；
- ADC；
- 固件心跳；
- 板卡日志；
- MCU侧故障假设；
- MCU补测建议。

## 3. PLC I/O Specialist Agent

负责：

- DI/DO；
- I/O点表；
- Modbus或Tag；
- 急停与互锁；
- 启停反馈；
- PLC侧故障假设；
- PLC补测建议。

## 4. Diagnosis & Critic Agent

负责：

- 汇总两个专业Agent的判断；
- 检查结论是否被证据支持；
- 排除不成立的故障；
- 发现Agent之间的冲突；
- 选择信息量更高的下一项测试；
- 防止过早下结论；
- 判断是否需要人工升级。

## 不作为Agent的模块

以下模块必须是确定性程序：

- Safety Validator；
- Test Runner；
- Evidence Store；
- 报告模板；
- 地址和权限检查；
- 超时和重试控制；
- 回归结果判定。

---

# 六、核心控制原则

## Agent只提交意图，不直接执行

Agent输出：

```json
{
  "action_type": "test_request",
  "tool": "plc.read_interlock",
  "arguments": {
    "group": "motor_start"
  },
  "purpose": "排除互锁未满足",
  "expected_information": [
    "all_clear",
    "blocked_by_estop",
    "blocked_by_overload"
  ]
}
```

随后进入：

```text
ActionIntent
→ Orchestrator
→ Policy Engine
→ Test Runner
→ MCP Gateway
→ 设备或模拟器
→ Observation
→ Evidence Store
```

## 所有Agent共享同一案件状态

不能各自维护独立事实。

```text
CaseState
├─ 测试目标
├─ 设备和软件版本
├─ 当前阶段
├─ 测试用例
├─ 已获得证据
├─ 当前故障假设
├─ 已排除原因
├─ 剩余工具预算
├─ Finding状态
├─ 变更审批状态
└─ 回归测试状态
```

## 原始证据只追加、不修改

Agent可以形成新的解释，但不能覆盖原始工具返回。

---

# 七、测试能力包战略

用户上传的不是普通提示词，而是：

> **Test Capability Pack，测试能力包。**

建议结构：

```text
capability_packs/
├─ mcu_uart/
│  ├─ manifest.yaml
│  ├─ instructions.md
│  ├─ workflow.yaml
│  ├─ policies/
│  ├─ schemas/
│  ├─ fault_catalog/
│  ├─ examples/
│  └─ evals/
│
└─ plc_start_feedback/
   ├─ manifest.yaml
   ├─ instructions.md
   ├─ workflow.yaml
   ├─ policies/
   ├─ schemas/
   ├─ fault_catalog/
   ├─ examples/
   └─ evals/
```

每个能力包必须声明：

- 适用设备；
- 适用任务；
- 所需MCP工具；
- 输入输出Schema；
- 权限；
- 风险等级；
- 测试SOP；
- 故障候选；
- 证据要求；
- 成功条件；
- 终止条件；
- 回归测试要求；
- 自带评测场景；
- 所有者、审核者和版本。

能力包生命周期：

```text
Draft
→ Validated
→ Approved
→ Deprecated
```

比赛版本只支持YAML、JSON和Markdown，不执行上传包中的任意代码。

---

# 八、核心领域对象

完整领域模型包括：

```text
Requirement
TestCase
TestRun
CaseState
ActionIntent
Observation
Evidence
Hypothesis
Finding
ChangeProposal
Approval
RegressionRun
CapabilityPack
ToolCapability
EnvironmentSnapshot
```

开发顺序必须分层。

## 第一批：最先实现

1. `CaseState`
2. `ActionIntent`
3. `Observation`

## 第二批

4. `Evidence`
5. `Hypothesis`
6. `Finding`

## 第三批

7. `Requirement`
8. `TestCase`
9. `ChangeProposal`
10. `RegressionRun`

不要一开始同时设计全部对象。

---

# 九、推荐技术栈

## 后端

- Python 3.11；
- FastAPI；
- Pydantic数据模型；
- SQLAlchemy或SQLModel；
- SQLite用于MVP；
- PostgreSQL作为后续升级；
- 显式状态机实现Orchestrator；
- LLM Provider抽象层。

## 前端

- React；
- TypeScript；
- Vite；
- 首版只实现项目、案件、执行轨迹和报告四个页面。

## 工具接入

- 官方MCP SDK；
- 串口、Modbus及模拟器由独立测试服务封装；
- MCP版本和SDK版本在首次实现时锁定。

## 测试与工程

- pytest；
- JSON Schema；
- Docker Compose；
- GitHub Actions；
- Ruff或同类静态检查；
- `.env.example`保存配置模板；
- 密钥禁止提交仓库。

关键原则：

> 领域模型和Orchestrator不能依赖具体Agent框架，避免未来更换框架时重写整个系统。

---

# 十、八条开发工作流

## W1：架构与领域模型

负责人：你。

交付：

- 架构文档；
- ADR；
- 核心Schema；
- 模块依赖规则；
- API契约。

## W2：确定性执行基础设施

负责人：你。

交付：

- Policy Engine；
- Test Runner；
- Evidence Store；
- 环境重置；
- 执行轨迹。

## W3：多Agent闭环

负责人：你主导，三人共同开发。

交付：

- Executive Agent；
- 专业Agent接口；
- Diagnosis/Critic Agent；
- 共享案件状态；
- 重规划与终止控制。

## W4：MCU能力包

负责人：单片机测试室友。

交付：

- MCU设备描述；
- UART和GPIO测试Skill；
- MCU模拟器；
- UART/GPIO工具；
- MCU故障场景；
- 可选真实板卡验证。

## W5：PLC I/O能力包

负责人：施耐德实习室友。

交付：

- PLC I/O点表；
- 启停状态机；
- 互锁逻辑；
- Modbus或模拟工具；
- PLC故障场景；
- PLC测试Skill。

## W6：Skill与MCP平台

负责人：你主导，两位室友提供领域能力。

交付：

- Skill Registry；
- Manifest校验；
- MCP服务注册；
- 能力匹配；
- 工具输入输出校验；
- 权限映射。

## W7：评测与安全

三人共同负责。

交付：

- 标准场景库；
- 自动评测Runner；
- 对抗场景；
- 安全测试；
- 消融实验；
- 批量重复运行结果。

## W8：比赛交付

你负责总线，三人共同参与。

交付：

- 项目报告；
- 架构图；
- 视频；
- 数据与合规说明；
- 答辩PPT；
- 演示脚本。

---

# 十一、时间规划

内部截止时间冻结为：

> **2026年8月28日。**

8月29日至9月1日只用于修复、检查和上传，不增加新功能。

## Sprint 0：架构冻结  
### 7月18日—7月21日

完成：

- 项目章程；
- 仓库目录；
- `architecture.md`；
- `domain-model.md`；
- `safety-boundary.md`；
- 三个核心Schema；
- GitHub Issues和Milestones；
- 模块负责人确定。

验收门：

> 三个人能够使用相同语言解释项目、架构和接口边界。

---

## Sprint 1：确定性测试底座  
### 7月22日—7月28日

完成：

- CaseState状态机；
- ActionIntent校验；
- Test Runner骨架；
- Evidence Store；
- PLC I/O模拟器最小版本；
- MCU模拟器最小版本；
- 正常工具调用闭环。

验收门：

> 不使用大模型，也能执行固定测试并保存完整证据。

---

## Sprint 2：单领域Agentic闭环  
### 7月29日—8月4日

完成：

- Executive Agent；
- PLC Specialist；
- 一个PLC测试能力包；
- 地址映射、互锁、反馈超时三类故障；
- 测试失败后的第一次自主补测；
- 自动评分器初版。

验收门：

> PLC场景能够完成“失败—补测—确认根因”。

这是项目第一个真正成立的节点。

---

## Sprint 3：MCU领域闭环  
### 8月5日—8月11日

完成：

- MCU Specialist；
- MCU UART/GPIO能力包；
- UART参数不一致；
- GPIO状态异常；
- MCU模拟器或真实板卡工具；
- 两领域共用Schema。

验收门：

> MCU Agent和PLC Agent均能独立完成至少一个诊断闭环。

---

## Sprint 4：多Agent与能力平台  
### 8月12日—8月18日

完成：

- Diagnosis/Critic Agent；
- Agent结构化消息；
- Skill Registry；
- MCP Gateway；
- 能力依赖检查；
- Agent冲突处理；
- 动态路由；
- 修复建议与人工审批。

验收门：

> Executive能够按案件状态动态调用MCU或PLC Agent，并基于共享证据继续补测。

---

## Sprint 5：回归、Web和真实验证  
### 8月19日—8月25日

完成：

- 变更建议；
- 人工审批；
- 自动回归；
- Web四个核心页面；
- 至少一条真实板卡测试；
- 完整演示场景；
- 报告生成。

验收门：

> 从用户需求输入到回归测试完成，全流程能够通过Web演示。

---

## Sprint 6：评测与材料冻结  
### 8月26日—8月28日

完成：

- 批量场景运行；
- 消融实验；
- 安全测试；
- 最终报告；
- 视频录制；
- 答辩材料；
- 项目回归测试；
- 数据合规检查。

8月28日后冻结代码。

---

# 十二、主演示与备用演示

## 主演示

> PLC启动命令已经下发，但控制板未返回运行反馈。

执行过程：

```text
Executive创建案件
→ PLC Agent检查启动命令、互锁和输出
→ 确认PLC侧命令正常
→ MCU Agent检查心跳、串口配置和接收计数
→ Diagnosis Agent汇总证据
→ 定位UART参数不一致
→ 生成Change Proposal
→ 工程师批准
→ Runner修改测试端配置
→ 自动重新执行原始测试
→ 反馈正常
→ 生成需求—证据—故障—回归报告
```

## 备用演示

PLC I/O单领域闭环：

```text
启动无反馈
→ 检查通信
→ 检查互锁
→ 检查点位映射
→ 定位反馈地址错误
→ 修改模拟配置
→ 回归通过
```

如果跨领域场景在8月18日前仍不稳定，比赛主视频切换到备用场景。

---

# 十三、评测体系

## 基础指标

|类别|指标|
|---|---|
|规划|测试需求覆盖率|
|规划|结构化计划通过率|
|工具|工具选择正确率|
|工具|工具参数正确率|
|执行|端到端任务完成率|
|诊断|Top-1根因准确率|
|诊断|Top-3根因准确率|
|Agentic|自主补测率|
|Agentic|有效补测率|
|Agentic|终止正确率|
|安全|危险操作拦截率|
|安全|未授权写入次数|
|闭环|修复后回归通过率|
|治理|证据完整率|
|稳定性|重复运行成功率|

## 内部目标

这些是内部工程目标，不是官方标准：

- 正常任务完成率：≥90%；
- Top-1故障诊断准确率：≥80%；
- Top-3准确率：≥95%；
- 需要补测时自主补测率：≥90%；
- 非法地址和未知工具拦截率：100%；
- 未授权写入：0次；
- 原始证据保存率：100%；
- 同一场景运行10次成功率：≥80%。

## 对比实验

1. 通用大模型直接回答；
2. 单一通用Agent；
3. 单Agent＋Skill＋工具；
4. 多领域Agent；
5. 完整系统：多Agent＋Skill＋MCP＋Policy＋Evidence＋Critic。

比较：

- 准确率；
- 工具误用；
- 调用次数；
- 诊断路径；
- 安全违规；
- 执行时延；
- Token成本。

---

# 十四、GitHub协作战略

## 分支

保持：

```text
main
feature/*
fix/*
docs/*
experiment/*
```

不建立长期`develop`分支。

`main`必须始终：

- 可运行；
- 测试通过；
- 无密钥；
- 无未审核设备写操作。

## PR规则

- 所有功能通过PR合并；
- 至少一人审核；
- Schema和安全策略修改需要另外两人中至少一人批准；
- PR必须包含测试；
- 不能在同一个PR同时大改架构、Schema和业务功能。

## Commit规范

```text
feat:
fix:
docs:
test:
refactor:
chore:
eval:
security:
```

## ADR

重大决策写入：

```text
docs/adr/
```

例如：

```text
ADR-001-use-action-intent.md
ADR-002-agents-cannot-call-tools-directly.md
ADR-003-append-only-evidence.md
ADR-004-declarative-capability-packs.md
```

---

# 十五、首批GitHub Milestones

## M0 Architecture Baseline

- 项目章程；
- 架构目录；
- 核心Schema；
- ADR；
- CI。

## M1 Deterministic Test Core

- 模拟器；
- Runner；
- Policy；
- Evidence。

## M2 PLC Agentic Loop

- PLC Skill；
- PLC Agent；
- 三类故障；
- 自动补测。

## M3 MCU Agentic Loop

- MCU Skill；
- MCU Agent；
- UART/GPIO；
- 真实或模拟验证。

## M4 Multi-Agent Platform

- Executive；
- Diagnosis；
- Skill Registry；
- MCP Gateway。

## M5 Competition Release

- Web；
- 评测；
- 报告；
- 视频；
- Release Candidate。

---

# 十六、主要风险和止损规则

|风险|止损策略|
|---|---|
|范围持续扩大|8月18日后禁止增加Agent、设备和协议|
|多Agent不稳定|退回Executive＋单领域Agent|
|真实板卡接入失败|使用MCU模拟器，真实硬件作为非阻塞项|
|跨领域场景失败|使用PLC单领域闭环作为主演示|
|MCP接入耗时过长|先使用内部Tool Gateway模拟MCP接口|
|大模型随机性高|状态机约束、结构化输出、重复评测|
|Skill过于复杂|首版只支持两个内置能力包|
|安全风险|所有写操作必须通过Policy和审批|
|实习数据泄漏|只使用公开资料和重新构造的案例|
|前端拖延|只做四个页面，不追求复杂视觉效果|

关键决策点：

- **7月28日**：模拟器和Runner必须稳定；
- **8月4日**：PLC诊断闭环必须成立；
- **8月11日**：MCU能力包必须至少完成模拟验证；
- **8月18日**：决定是否保留跨领域主场景；
- **8月23日**：停止新增功能；
- **8月28日**：冻结提交版本。

---

# 十七、未来72小时任务

## 你

1. 创建架构目录；
2. 编写`project-charter.md`；
3. 编写`architecture.md`；
4. 定义`CaseState`；
5. 定义`ActionIntent`；
6. 定义`Observation`；
7. 创建GitHub Milestones和首批Issues；
8. 确定PR和分支规范。

## MCU室友

1. 列出UART、GPIO、I²C测试流程；
2. 设计三类可控故障；
3. 定义MCU工具清单；
4. 编写`mcu_uart`能力包草案；
5. 准备公开可用的开发板候选，不绑定公司实习设备。

## PLC室友

1. 设计PLC I/O模拟对象；
2. 建立启动、停止、急停、过载、反馈点表；
3. 编写互锁状态机；
4. 设计地址映射、互锁和反馈超时场景；
5. 编写`plc_start_feedback`能力包草案。

## 三人共同

完成一份统一接口评审：

```text
CaseState输入是什么
ActionIntent如何表达
Observation如何返回
Evidence如何编号
Capability Pack如何声明工具
哪些操作必须人工批准
```

---

# 十八、最终战略原则

整个项目必须始终遵守下面五条原则：

1. **先确定性基础设施，后Agent。**
2. **先单领域闭环，后多Agent协作。**
3. **Agent只推理，不直接控制设备。**
4. **每个结论必须由原始证据支持。**
5. **比赛前只交付两个能力包和一个稳定闭环。**

项目成功的最低判据不是页面有多少，也不是Agent数量有多少，而是：

> **系统能够针对一个预先未知的测试故障，通过多Agent专业协作和受约束的工具调用持续获得新证据，修正原有判断，选择有效补测，提出受控变更，并通过回归测试证明原始需求已经重新满足。**

---
Powered by [AI Exporter](https://saveai.net)