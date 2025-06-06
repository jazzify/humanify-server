# Humanify Server
[![CI](https://github.com/jazzify/humanify-server/actions/workflows/main.yml/badge.svg)](https://github.com/jazzify/humanify-server/actions/workflows/main.yml)
[![python](https://img.shields.io/badge/Python%3A%203.13-blue)](https://www.python.org)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![Code style: ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Checked with mypy](https://img.shields.io/badge/mypy-checked-blue)](http://mypy-lang.org/)

### Built with
- Docker + Compose
- Gunicorn
- Whitenoise
- PostgreSQL
- Docs (Open API 3.0)
- Debug Toolbar

## Development requirements
- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)
- [uv](https://docs.astral.sh/uv/) (`pip install uv`)
- [Task](https://taskfile.dev/)
- [pre-commit](https://pre-commit.com/) (`pip install pre-commit`)

## Getting started
1. Install the pre-commit hooks:
    ```sh
    pre-commit install
    ```
1. Create a `.env` file just like `.env.example` with your custom data, if you add something to your `.env` file, also and keep `.env.example` updated with dummy values for key reference.
1. Start the development server:
    ```sh
    task compose-up -- -d
    ```
1. (Optionally) run `django-tasks` worker for all queues:
    ```sh
    task manage-db_worker -- --queue-name="*" --interval=2
    ```

## App Structure and Conventions
We follow specific conventions to organize our Django apps for clarity and maintainability:
- **`urls.py` for URL Routing**: We use `urls.py` to define URL-API patterns for the app.
- **`models.py` for Database Models**: We use `models.py` to define database models.
- **`serializers.py` for Serialization**: We use `serializers.py` to define serialization logic.
- **`apis.py` instead of `views.py`**: For API endpoint definitions, we use `apis.py`. This helps differentiate API logic from traditional Django views that might render templates.
- **`services.py` for Business Logic**: All core business logic should reside in `services.py`. This file acts as a central hub for the application's primary functionalities.
- **`constants.py` for Constants**: We use `constants.py` to store constant values that are used throughout the application. This file helps in keeping values consistent and easy to maintain.
- **`data_models.py` for Data Models**: We use `data_models.py` to define data structures for our application objects.
- **`tasks.py` for Background Tasks**: We use `tasks.py` to define background tasks.
- **Specific Internal Logic**: For highly specific or internal app logic (e.g., image transformations), you can create custom files within the app's directory (e.g., `images/transformations.py`).

### Apps Conventions
- **Shared Components**: `constants`, `services`, `data_models` and `tasks` are think to be accessible by other apps. Place widely used constants and reusable service functions here.

### Apps Structure Disclaimer
We can use folders to group related files/components within an app splitting the codebase into more manageable and organized sections as the project grows and complexity increases:
```bash
# Places `services` may start like:
places/
    __init__.py
    services.py

# and become:
places/
    __init__.py
    services/
        __init__.py
        place.py
        place_image.py
```
Once this pattern is applied in any app component we highly recommend to switch to this pattern for other app components to follow a domain-like structure.

## General key conventions
- **Method Naming**: We use an `object_action[_context]` naming convention for methods (e.g., `place_retrieve_by_user()`, `user_update()`). This helps in keeping the codebase organized and easy to navigate.

## Current Apps
- **users**: The `users` app handles user-related functionalities.
- **api**: The `api` app centralize API routing. This app typically contains api versions that includes URL patterns from other apps, providing a single entry point for all API requests and making versioning or global API changes more manageable.
- **common**: The `common` app is used to house highly generic and reusable code as public services that are not specific nor related to any single application but are used across the project. This promotes DRY principles and keeps app-specific logic clean.
- **image_processing**: The `image_processing` app handle general image-related functionalities, such as processing transformations and object detection.
    - The `image_processing` app its meant to be extracted to a new app in the future as it will grow and become more complex, inner apps should use the `image_processing/api` interfaces that supports built-in types instead of accessing the app `src` functionalities.
- **places**: The `places` app allows to create and handle `Places`.
    - A `Place` is a basic virtual representations of a real place with a real-world counterpart.


## Taskfile and Docker
The tasks defined in the Taskfile are executed within a Docker container, which has a volume mounted to the host PC. This volume specifically includes the application's codebase, allowing for a seamless integration between the development environment on the host and the containerized tasks.

Here's how it works:

1. **Code Synchronization**: The mounted volume in the `docker-compose.yaml>backend-humanify` ensures that the code inside the container is the same as on the host machine. Any changes made to the code on the host are immediately reflected within the container. This is crucial for development workflows, where frequent changes to the codebase are tested and iterated upon.

1. **Docker Compose and Django Operations**: The tasks typically involve operations such as starting, stopping, or managing services using Docker Compose, as well as running commands related to Django. Since these tasks rely on the codebase, the volume ensures they operate on the latest version of the code, regardless of where the task is run.

1. **Host and Container Interaction**: While the tasks are executed in an isolated container environment, the mounted volume enables these tasks to access and manipulate the code on the host machine. This setup is particularly useful for tasks that need to interact closely with the host's file system or leverage host-specific configurations.

Run `task --list` to see a full list of available tasks with their description.

- **Common docker compose commands**
    ```bash
    # build the containers without cache
    task compose-build -- --no-cache

    # start the containers in detached mode
    task compose-up -- -d

    # stop the containers
    task compose-stop

    # down the containers
    task compose-down
    ```

- **Common manage.py commands**
    ```bash
    # run django-tasks worker for a queue
    task manage-db_worker -- --queue-name="queue_name" --interval=2

    # create a super user
    task manage-createsuperuser

    # make migrations for a specific app
    task manage-makemigrations -- <app_name>

    # migrate a specific db
    task manage-migrate -- --database=<db_name>

    # start a new app
    task manage-startapp -- <app_name>
    ```

**DISCLAIMER**: Even with this volume approach some tasks might **NOT** reflect the changes in the host machine, for example, running `task uv-add -- requests` will install the `requests` lib dependency inside the docker container only, and you would need to install it via `uv add requests` locally if you want to have editor completitions or linting for the lib. This is the actual behaviour we want, we highly encourage to develop in a containerized environment and not in the host machine since some dependencies might need custom OS dependencies that we might forget to add to the Dockerfile while working in a non-containerized environment.

The best approach to install a dependency in the host and a running container is to install it locally with `uv add <dependency_name>` and then run `task uv-sync`.

_If you add a new task that does not work with the volume approach, please add `[CONTAINER_ONLY]` tag to the task description._

## Background Tasks
We are currently using [django-tasks](https://django-tasks.readthedocs.io/en/latest/) for background tasks.

### Usage
To run the background task worker:

```bash
# Run the worker for specific queues
task manage-db_worker -- --queue-name="place_images,users"

# Run the worker for all queues
task manage-db_worker -- --queue-name="*"

# Run the worker with a specific interval (in seconds) (default is 1)
task manage-db_worker -- --queue-name="*" --interval=20
```

### Recommendations
- **Queue Names**: It's good practice to use descriptive queue names to organize tasks. For example, `image_processing`, `notifications`, `data_cleanup`.
- Consider the priority and resource consumption of tasks when assigning them to queues.


## Testing
Currently we use [pytest-django](https://pytest-django.readthedocs.io/en/latest/index.html) for testing our code.
We use [faker](https://faker.readthedocs.io/en/latest/) along with [factory_boy](https://factoryboy.readthedocs.io/en/latest/) to generate data for our testing models.

Complete [list of the default providers](https://faker.readthedocs.io/en/stable/providers.html) available in `faker`.

### Running tests:
```bash
# Run all tests
task test

# Run a specific test file
task test -- path/to/test_file_example.py

# Run a specific test
task test -- path/to/test_file_example.py::test_example
```

## API docs generation
The API docs are generated based on the code using [drf-spectacular](https://drf-spectacular.readthedocs.io/en/latest/index.html).
