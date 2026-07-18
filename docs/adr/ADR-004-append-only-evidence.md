# ADR-004: Append-only Evidence

## Status
Accepted

## Context

Evidence 必须作为不可篡改的事实源，以避免 Agent 或后续节点覆盖原始工具返回。

## Decision

- 原始 Observation 和 Evidence 只追加。
- 任何派生结论与推理结果作为独立实体保存。
- Evidence Store 提供只追加接口。

## Consequences

- 提高审计性。
- 便于回溯和差异分析。
- 需要额外存储空间。

## Rejected Alternatives

- 允许更新原始证据：被拒绝，因为破坏了事实链。
