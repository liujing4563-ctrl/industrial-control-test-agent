# MCP Integration

## 关键链路

Agent
→ ActionIntent
→ Policy
→ Runner
→ MCP Gateway
→ Test Service
→ Protocol Driver
→ Device

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
