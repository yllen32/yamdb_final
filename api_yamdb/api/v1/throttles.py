from rest_framework.throttling import AnonRateThrottle


class NoGuessRateThrottle(AnonRateThrottle):
    """Чтоб не подобрали секретный код."""
    scope = 'no_guess'
