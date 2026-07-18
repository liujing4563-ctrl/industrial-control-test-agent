# 0002 - Agent vs Skill Separation

Date: 2026-07-18

## Status

Accepted

## Context

需要明确 Agent 与 Skill 的职责，避免业务逻辑与操作策略混淆。

## Decision

- Agent 负责推理与决策。
- Skill 负责封装 SOP、故障经验、证据需求和判据。
- MCP 提供工具与数据能力。
- Runner 负责执行已批准的动作。

## Consequences

- 业务逻辑和执行策略分离，便于审计和替换。
- Agent 更专注于案件推进，Skill 可独立治理和版本控制。
