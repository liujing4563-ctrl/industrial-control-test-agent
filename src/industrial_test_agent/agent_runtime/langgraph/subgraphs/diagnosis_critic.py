from dataclasses import dataclass


@dataclass
class DiagnosisCriticSubgraph:
    def review(self, case_id: str) -> str:
        return "critique_complete"
