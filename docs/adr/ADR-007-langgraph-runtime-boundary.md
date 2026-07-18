# ADR-007: LangGraph Runtime Boundary

## Status
Accepted

## Context

LangGraph 应该作为运行时编排引擎，不能污染领域模型。

## Decision

- CaseState/ActionIntent/Observation 等领域对象独立于 LangGraph。
- LangGraph 仅放在 agent_runtime/langgraph/ 目录。

## Consequences

- 领域模型可替换运行时实现。
- 便于将来切换到其他工作流引擎。

## Rejected Alternatives

- 将领域对象直接绑定到 LangGraph：会导致高耦合。
