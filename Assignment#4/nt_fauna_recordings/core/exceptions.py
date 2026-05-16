class ServiceError(Exception):
    """Base exception for service-layer errors."""


class ObservationCreateError(ServiceError):
    """Raised when an observation cannot be created."""


class AnomalyFlagError(ServiceError):
    """Raised when an anomaly cannot be flagged."""


class AnomalyResolveError(ServiceError):
    """Raised when an anomaly cannot be resolved."""