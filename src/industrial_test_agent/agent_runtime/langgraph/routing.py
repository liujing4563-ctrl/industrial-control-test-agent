"""Routing helpers for LangGraph-style workflows."""

from typing import Optional


def choose_specialist_domain(case_stage: str, evidence_ids: int) -> str:
    if evidence_ids > 2:
        return "plc_io"
    return "mcu"


def next_stage_from_result(success: bool, interrupt: bool) -> Optional[str]:
    if interrupt:
        return None
    if success:
        return "record_observation"
    return "decide_next"
