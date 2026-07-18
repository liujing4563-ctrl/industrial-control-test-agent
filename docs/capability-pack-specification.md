# Capability Pack Specification

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

- Draft
- Validated
- Approved
- Deprecated
