# Safety Boundary

## 安全边界原则

- 设备写操作必须经过审批。
- 仅允许 Runner 负责实际执行和改设备。
- Agent 只能提出 Change Proposal，不能直接执行修复。
- 原始 Evidence 一律追加式保存，不允许覆盖或删除。

## 典型流程

1. Agent 生成 ActionIntent 或 Change Proposal。
2. Orchestrator 校验并提交给 Policy Engine。
3. 如果涉及写操作，进入审批流程。
4. Runner 执行经过批准的操作。
5. 自动执行回归测试，确认 Evidence 后关闭 Finding。
