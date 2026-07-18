# 0003 - MCP Trust Boundary

Date: 2026-07-18

## Status

Accepted

## Context

MCP 工具属于外部能力，默认不可完全信任，需要明确安全和校验边界。

## Decision

- 所有 MCP 调用必须经过输入/输出 Schema 校验。
- 仅允许白名单工具。
- 强制超时、调用次数限制和写操作审批。
- Gateway 统一负责认证、授权与限流。

## Consequences

- 强化安全边界，避免未校验工具输出污染系统事实。
- 提供可审计的 MCP 调用链路。
