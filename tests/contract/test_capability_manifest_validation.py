from pathlib import Path

import pytest
import yaml

from industrial_test_agent.skills.models import (
    CapabilityPackManifest,
    HardwareValidationStatus,
)


EXPECTED_DOMAIN_VALUES = {
    "plc_start_feedback": {
        "supported_devices": ["通用 PLC I/O 模块"],
        "required_mcp_tools": [
            "plc.read_signal",
            "plc.write_test_signal",
            "plc.read_interlock",
            "plc.wait_feedback",
            "plc.reset_test_environment",
        ],
        "evidence_requirements": [
            "互锁状态快照",
            "启动信号输出记录",
            "反馈信号时序",
            "复位确认",
        ],
        "risk_level": "medium",
        "permissions": ["read", "test_only_write"],
        "success_criteria": [
            "所有互锁条件满足",
            "电机启动反馈在规定时间内收到",
            "测试环境可正常复位",
        ],
        "termination_criteria": [
            "互锁条件不满足且不可修复",
            "反馈超时",
            "测试步骤全部完成",
        ],
        "regression_requirements": [
            "变更后重新运行全部 PLC I/O 测试",
        ],
    },
    "mcu_uart": {
        "supported_devices": ["MCU 通用开发板 (UART)"],
        "required_mcp_tools": [
            "mcu.read_heartbeat",
            "mcu.send_uart_frame",
            "mcu.read_uart_response",
            "mcu.read_gpio",
            "mcu.scan_i2c",
        ],
        "evidence_requirements": [
            "UART 帧日志",
            "心跳超时记录",
            "GPIO 状态快照",
        ],
        "risk_level": "low",
        "permissions": ["read", "test_only_write"],
        "success_criteria": [
            "心跳响应正常",
            "UART 帧收发一致",
            "波特率匹配无误",
        ],
        "termination_criteria": [
            "所有 UART 帧测试完成",
            "心跳超时不可恢复",
            "GPIO 状态异常不可恢复",
        ],
        "regression_requirements": [
            "变更后重新运行全部 UART 测试",
        ],
    },
}


@pytest.mark.parametrize("pack_id", sorted(EXPECTED_DOMAIN_VALUES))
def test_capability_pack_manifest_is_valid_and_unapproved(
    pack_id: str,
) -> None:
    path = Path("capability_packs") / pack_id / "manifest.yaml"
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    manifest = CapabilityPackManifest.model_validate(payload)

    assert manifest.pack_id == pack_id
    assert manifest.status == "draft"
    assert manifest.review.domain_review_status == "pending"
    assert (
        manifest.review.hardware_validation_status
        is HardwareValidationStatus.NOT_STARTED
    )
    expected = EXPECTED_DOMAIN_VALUES[pack_id]
    assert manifest.metadata.supported_devices == expected[
        "supported_devices"
    ]
    assert manifest.metadata.required_mcp_tools == expected[
        "required_mcp_tools"
    ]
    assert manifest.metadata.evidence_requirements == expected[
        "evidence_requirements"
    ]
    assert manifest.safety.risk_level == expected["risk_level"]
    assert manifest.safety.permissions == expected["permissions"]
    assert manifest.metadata.success_criteria == expected[
        "success_criteria"
    ]
    assert manifest.metadata.termination_criteria == expected[
        "termination_criteria"
    ]
    assert manifest.metadata.regression_requirements == expected[
        "regression_requirements"
    ]
