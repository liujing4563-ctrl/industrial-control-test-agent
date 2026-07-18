# industrial-control-test-agent

Extensible and Verifiable Multi-Agent Test Engineering Platform for Embedded Boards and PLC I/O Systems.

## 当前阶段

本阶段建立顶层设计、系统架构基线、领域模型、Schema 和接口骨架。
不实现真实 Agent、LangGraph、MCP 或设备驱动。

## 目标

构建一个可扩展、可验证的工业测试平台基线，支持 MCU 和 PLC I/O 两个领域，并明确多 Agent、Skill、Policy、Runner、Evidence 的边界。

## 目录说明

- `apps/`：API 与 Web 工作台。
- `src/industrial_test_agent/`：核心领域、Orchestrator、Agent Runtime、Skill、MCP、Policy、Runner、Evidence。
- `capability_packs/`：能力包定义。
- `schemas/`：JSON Schema 数据契约。
- `simulators/`：仿真环境占位。
- `tests/`：单元、契约、集成、安全和端到端测试占位。
- `docs/`：架构、域模型、安全、能力包、MCP 集成、团队工作包和 ADR。

## 本阶段边界

- 仅完成架构基线、文档、契约与接口骨架。
- 不接入真实 LL M、MCP、PLC、MCU 或数据库。
- 不实现 Web 页面和完整设备驱动。

## 运行检查

```bash
PYTHONPATH=src python -m compileall src
python -m unittest discover -s tests/unit
```
