# ADR-007：LangGraph 运行时边界

## 状态
Superseded by ADR-009

## 背景

项目未来可能使用 LangGraph 作为编排引擎，但 M1 当前采用无外部工作流依赖的确定性 Runtime。无论运行时实现如何变化，都不能污染领域模型。

## 决策

- CaseState/ActionIntent/Observation 等领域对象独立于 LangGraph。
- 当前 Runtime 不依赖 LangGraph。
- 失效的早期 LangGraph 占位不作为公共接口保留。
- 未来引入 LangGraph 时，必须通过独立适配层复用现有 Pydantic 契约，不得复制领域模型。

## 影响

- 领域模型可替换运行时实现。
- 便于将来切换到其他工作流引擎。
- 当前仓库不会因占位模块形成第二套 Runtime 契约。

## 已拒绝的替代方案

- 将领域对象直接绑定到 LangGraph：会导致高耦合。
