# MCP 集成

## 关键链路

智能体（Agent）
→ 动作意图（ActionIntent）
→ 策略校验（Policy）
→ 执行器（Runner）
→ MCP 网关
→ 测试服务
→ 协议驱动
→ 设备

## MCP 不承担

- 硬实时控制
- 设备安全与急停
- 协议时序保证
- 底层驱动错误恢复

## MCP 注册信息

- server_id
- version
- transport
- tools
- resources
- input_schema
- output_schema
- permissions
- network_scope
- timeout_seconds
- max_calls
- environment_type
