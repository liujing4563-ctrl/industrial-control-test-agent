# ADR-007：LangGraph 运行时边界

## 状态
已接受

## 背景

LangGraph 应该作为运行时编排引擎，不能污染领域模型。

## 决策

- CaseState/ActionIntent/Observation 等领域对象独立于 LangGraph。
- LangGraph 仅放在 agent_runtime/langgraph/ 目录。

## 影响

- 领域模型可替换运行时实现。
- 便于将来切换到其他工作流引擎。

## 已拒绝的替代方案

- 将领域对象直接绑定到 LangGraph：会导致高耦合。
