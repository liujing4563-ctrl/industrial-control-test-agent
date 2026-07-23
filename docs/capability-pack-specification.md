# 能力包规范

## 目录结构

```
capability_pack/
├── manifest.yaml
├── instructions.md
├── workflow.yaml
├── schemas/
├── policies/
├── fault_catalog/
├── examples/
└── evals/
```

## 必要字段

- schema_version
- pack_id
- name
- domain
- version
- status
- description
- entrypoints
- ownership
- review
- safety
- metadata

嵌套结构如下：

- `entrypoints`：说明、工作流、故障目录、示例和评测入口；
- `ownership`：实现负责人、领域负责人、平台审核人和领域审核人；
- `review`：实现状态、领域审核状态和硬件验证状态；
- `safety`：平台风险等级和权限声明；
- `metadata`：原有设备、工具、证据、成功、终止和回归要求。

Manifest 字段统一使用 `snake_case`。可执行格式由
`industrial_test_agent.skills.models.CapabilityPackManifest` 定义，未声明字段会被拒绝。该模型只约束平台结构，不替领域成员决定信号、互锁、波特率、引脚、故障判据或恢复方法。

仓库中的 JSON Schema 由 Pydantic 模型生成：

```bash
python -m industrial_test_agent.schemas.generate
python -m industrial_test_agent.schemas.generate --check
```

## 生命周期

- 草案（`draft`）
- 已验证（`validated`）
- 已批准（`approved`）
- 已弃用（`deprecated`）

仓库中的 PLC 与 MCU 能力包当前均为 `draft`，领域审核状态为
`pending`，硬件验证状态为 `not_started`。Manifest 通过平台模型校验
不等于领域内容获批或完成硬件验证。
