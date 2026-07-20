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
- owner
- approver
- supported_devices
- supported_domains
- required_mcp_tools
- risk_level
- permissions
- evidence_requirements
- fault_model
- success_criteria
- termination_criteria
- regression_requirements
- admission_state

## 生命周期

- 草案（Draft）
- 已验证（Validated）
- 已批准（Approved）
- 已弃用（Deprecated）
