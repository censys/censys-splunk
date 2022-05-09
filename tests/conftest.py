import os
from typing import List
import pytest


@pytest.fixture(scope="session")
def docker_compose_files(request) -> List[str]:
    """
    Get an absolute path to the  `docker-compose.yml` file. Override this
    fixture in your tests if you need a custom location.

    Returns:
        string: the path of the `docker-compose.yml` file

    """
    docker_compose_path = os.path.join(
        str(request.config.invocation_dir), "docker-compose.test.yml"
    )
    # LOGGER.info("docker-compose path: %s", docker_compose_path)

    return [docker_compose_path]
