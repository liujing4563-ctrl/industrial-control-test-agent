# 0001 - Architecture Baseline

Date: 2026-07-18

## Status

Accepted

## Context

项目初期需要一个稳定的架构基线，避免后续多 Agent、Skill、MCP 和测试评测出现反复返工。

## Decision

- 采用清晰的目录结构，将应用、核心框架、能力包、Schema、仿真、测试和文档分离。
- 先构建`CaseState`、`ActionIntent`、`Observation` 三个核心数据契约。
- 禁止 Agent 直接访问设备或修改证据。

## Consequences

- 代码边界清晰，后续模块可独立实现。
- 架构变更影响控制在数据契约层面，减少多模块联动风险。
