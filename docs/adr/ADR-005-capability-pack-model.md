# ADR-005: Capability Pack Model

## Status
Accepted

## Context

能力包需要定义测试 SOP、故障模型、证据要求和回归规则。

## Decision

- 使用 manifest + instructions + workflow + schemas 的目录结构。
- 将能力包作为独立可审核单元。

## Consequences

- 便于能力回溯与版本控制。
- 能力包可被测试工程师和领域专家共同维护。

## Rejected Alternatives

- 将能力内容直接硬编码到代码：会降低可扩展性。
