"""Evidence Store domain errors."""


class EvidenceConflictError(ValueError):
    """Raised when an idempotency key maps to conflicting Evidence content."""
