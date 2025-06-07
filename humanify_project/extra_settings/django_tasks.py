TASKS = {
    "default": {
        "BACKEND": "django_tasks.backends.database.DatabaseBackend",
        "QUEUES": ["place_images", "image_processing"],
        "ENQUEUE_ON_COMMIT": True,
    }
}
