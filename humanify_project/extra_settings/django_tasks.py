TASKS = {
    "default": {
        "BACKEND": "django_tasks.backends.database.DatabaseBackend",
        "QUEUES": ["place_images"],
        "ENQUEUE_ON_COMMIT": True,
    }
}
