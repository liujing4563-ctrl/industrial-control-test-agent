from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from industrial_test_agent.skills.models import CapabilityPackManifest


MANIFESTS = [
    Path("capability_packs/mcu_uart/manifest.yaml"),
    Path("capability_packs/plc_start_feedback/manifest.yaml"),
]


@pytest.mark.parametrize("manifest_path", MANIFESTS)
def test_existing_capability_pack_manifest_is_valid(
    manifest_path: Path,
) -> None:
    payload = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    manifest = CapabilityPackManifest.model_validate(payload)

    assert manifest.capability_pack_id == manifest_path.parent.name
    assert manifest.status == "draft"


def test_manifest_rejects_undeclared_platform_fields() -> None:
    payload = yaml.safe_load(MANIFESTS[0].read_text(encoding="utf-8"))
    payload["unknown_platform_field"] = True

    with pytest.raises(ValidationError):
        CapabilityPackManifest.model_validate(payload)
