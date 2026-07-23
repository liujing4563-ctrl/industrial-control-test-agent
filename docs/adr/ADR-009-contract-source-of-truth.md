# ADR-009：可执行契约唯一来源

## 状态（Status）

Accepted

该状态仅表示平台契约决策已接受，不表示 PLC 或 MCU 领域内容已经审核。

## 背景（Context）

仓库曾同时存在 Python 模型、手写 JSON Schema、旧 Runtime 字段和
Capability Pack YAML。字段命名和接口返回类型发生漂移后，Runtime、
Checkpoint 与文档无法共同证明同一份数据契约。

## 决策（Decision）

- Pydantic 模型是唯一可执行契约来源。
- 核心领域模型不依赖 LangGraph、MCP、具体 Runner 或 Agent 框架。
- Runner、Policy、Evidence Store、Checkpointer 和 Runtime 通过公开协议
  使用这些模型。
- Capability Pack Manifest 使用 Pydantic 模型加载和校验。
- 未声明字段默认拒绝。

## 规范命名（Canonical Naming）

Python、JSON 和 YAML 的新数据统一使用 `snake_case`。新数据不同时输出
旧字段名。当前仓库实际产生过的旧 M1 数据只通过明确迁移入口读取。

## Schema 生成（Schema Generation）

`src/industrial_test_agent/schemas/registry.py` 注册需要发布的模型。
执行以下命令生成稳定的仓库 Schema：

```bash
python -m industrial_test_agent.schemas.generate
```

CI 使用 `--check` 检查模型与 `schemas/` 是否漂移。生成结果不包含时间、
网络数据或本机路径，重复生成必须无变化。

## Runtime 兼容（Runtime Compatibility）

当前活动 Runtime 是确定性 `GraphRunner`，并未正式接入 LangGraph。
Runtime 继续保持 Runner 异常标准化、失败重规划、Evidence 幂等写入和
重复副作用保护。未来编排器只能作为适配层复用本 ADR 定义的契约。

## Checkpoint 迁移（Checkpoint Migration）

新 Checkpoint Envelope 版本为 `2.0`，包含 graph_state、
evidence_snapshot 和 metadata。读取器只对仓库实际存在的 M1 `1.0`
Envelope 和短期旧格式执行受控迁移；未知版本、未知字段和不一致引用继续
被拒绝。

## Manifest 校验（Manifest Validation）

Capability Pack Manifest 统一包含 schema_version、pack_id、
entrypoints、ownership、review、safety 和 metadata。模型只确认平台结构
与审核状态，不批准信号、互锁、地址、引脚、波特率、故障判据、恢复方法
或领域标准答案。

## 影响（Consequences）

- 模型修改必须同步重新生成 Schema 并通过契约测试。
- 接口实现共享同一组领域类型，减少重复转换。
- Manifest 的结构错误可以在加载阶段发现。
- 旧格式兼容范围有限，新增迁移必须有明确版本和测试。
- Evidence 顶层冻结不代表嵌套对象深度不可变；存储隔离仍由 Evidence
  Store 负责。

## 已拒绝的替代方案（Rejected Alternatives）

- 继续手工维护 JSON Schema：无法可靠防止字段漂移。
- 同时长期输出新旧字段名：会形成两个事实来源。
- 让 Runtime 或 LangGraph 定义自己的状态模型：会破坏领域层独立性。
- 通过宽松 `extra` 接受未知旧数据：会掩盖损坏或不受支持的格式。
