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

- capability_pack_id
- name
- version
- domain
- owner
- approver
- status
- risk_level
- description
- supported_devices
- required_mcp_tools
- permissions
- evidence_requirements
- success_criteria
- termination_criteria
- regression_requirements

Manifest 字段统一使用 `snake_case`。可执行格式由
`industrial_test_agent.skills.models.CapabilityPackManifest` 定义，未声明字段会被拒绝。该模型只约束平台结构，不替领域成员决定信号、互锁、波特率、引脚、故障判据或恢复方法。

仓库中的 JSON Schema 由 Pydantic 模型生成：

```bash
python -m industrial_test_agent.contracts.json_schema
python -m industrial_test_agent.contracts.json_schema --check
```

## 生命周期

- 草案（`draft`）
- 已验证（`validated`）
- 已批准（`approved`）
- 已弃用（`deprecated`）
