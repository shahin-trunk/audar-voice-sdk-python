"""Default constants for the Audar SDK."""

SDK_VERSION = "0.1.0"
USER_AGENT = f"audar-python/{SDK_VERSION}"

DEFAULT_TTS_BASE_URL = "https://txt2sph.audarai.com"
DEFAULT_STT_BASE_URL = "https://sph2txt.audarai.com"
DEFAULT_SIDON_BASE_URL = "https://sph2sphe.audarai.com"
DEFAULT_BACKEND_BASE_URL = "https://argent.audarai.com"

DEFAULT_TIMEOUT = 60.0
DEFAULT_CONNECT_TIMEOUT = 10.0
DEFAULT_MAX_RETRIES = 2

AUDAR_API_KEY_ENV = "AUDAR_API_KEY"
