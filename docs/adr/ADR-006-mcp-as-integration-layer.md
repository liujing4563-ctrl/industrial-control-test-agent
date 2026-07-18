# ADR-006: MCP as Integration Layer

## Status
Accepted

## Context

MCP 本质上是测试工具和设备能力的桥梁，不能承载业务决策。

## Decision

- MCP 仅暴露工具和资源接口。
- 所有业务决策由 Policy、Runner 和 Orchestrator 负责。

## Consequences

- 业务与执行清晰分离。
- MCP 鉴权、校验和限流成为边界责任。

## Rejected Alternatives

- 让 MCP 直接决定写操作：会混淆职责。
