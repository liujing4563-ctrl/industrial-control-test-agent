# ADR-008: Human Approval for Device Changes

## Status
Accepted

## Context

真实设备写操作存在风险，必须提供人工审批节点。

## Decision

- 写操作生成 ChangeProposal。
- 进入审批流程后才允许 Runner 执行。
- 审批结果写回 CaseState。

## Consequences

- 降低误操作风险。
- 增加审批延迟。

## Rejected Alternatives

- 直接自动执行所有写操作：风险过高。
