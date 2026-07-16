from django.conf import settings

DEFAULT_CACHE_PREFIX = "feature_flags"
DEFAULT_CACHE_TTL = 300


def get_cache_prefix() -> str:
    return str(getattr(settings, "FEATURE_FLAGS_CACHE_PREFIX", DEFAULT_CACHE_PREFIX))


def get_cache_ttl() -> int:
    return int(getattr(settings, "FEATURE_FLAGS_CACHE_TTL", DEFAULT_CACHE_TTL))
