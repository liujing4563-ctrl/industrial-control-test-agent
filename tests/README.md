# 测试

- `unit/`：模型、节点和组件级行为；
- `contract/`：Pydantic、JSON Schema、Manifest 和公共协议；
- `integration/`：Checkpoint 恢复与组件协作；
- `safety/`：重复副作用和无效恢复防护；
- `end_to_end/`：完整案件链路。

完整验证：

```bash
ruff check .
python -m industrial_test_agent.contracts.json_schema --check
python -m compileall src
pytest
```
