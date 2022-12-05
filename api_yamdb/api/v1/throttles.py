from rest_framework.throttling import AnonRateThrottle


class NoGuessRateThrottle(AnonRateThrottle):
    scope = 'no_guess'
