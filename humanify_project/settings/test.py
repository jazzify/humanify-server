from humanify_project.settings.base import *  # noqa F403

TESTING = True
DEBUG = True

# Define a separate media root for tests
TEST_MEDIA_ROOT = BASE_DIR / "test_media"  # noqa F405

# Override MEDIA_ROOT for tests
MEDIA_ROOT = TEST_MEDIA_ROOT

# Ensure the default file storage uses the test media root during tests
STORAGES = {  # noqa F405
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
        "OPTIONS": {
            "location": MEDIA_ROOT,
            "base_url": "/test_media/",
        },
    },
    "staticfiles": {  # noqa F405
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}
