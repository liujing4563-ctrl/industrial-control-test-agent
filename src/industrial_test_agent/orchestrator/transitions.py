from enum import Enum


class CasePhase(str, Enum):
    intake = "intake"
    planning = "planning"
    execution = "execution"
    diagnosis = "diagnosis"
    approval = "approval"
    regression = "regression"
    completed = "completed"
    escalated = "escalated"
