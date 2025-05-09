from os import getenv

from agno.docker.app.fastapi import FastApi
from agno.docker.resource.image import DockerImage
from agno.docker.resources import DockerResources

from workspace.settings import ws_settings

#
# -*- Resources for the Development Environment
#

# -*- Dev image
dev_image = DockerImage(
    name=f"{ws_settings.image_repo}/{ws_settings.image_name}",
    tag=ws_settings.dev_env,
    enabled=ws_settings.build_images,
    path=str(ws_settings.ws_root),
    # Do not push images after building
    push_image=ws_settings.push_images,
)

# -*- Container environment для облачной базы данных Neon DB
container_env = {
    "RUNTIME_ENV": "dev",
    # Get the OpenAI API key from the local environment
    "OPENAI_API_KEY": getenv("OPENAI_API_KEY"),
    # Enable monitoring
    "AGNO_MONITOR": "True",
    "AGNO_API_KEY": getenv("AGNO_API_KEY"),
    
    # Параметры подключения к Neon DB
    "DATABASE_URL": getenv("DATABASE_URL", "postgresql://neondb_owner:npg_ZbR1VKhOzv8t@ep-silent-morning-a29aajlm-pooler.eu-central-1.aws.neon.tech/neondb?sslmode=require"),
    "DATABASE_URL_ASYNC": getenv("DATABASE_URL_ASYNC", "postgresql+asyncpg://neondb_owner:npg_ZbR1VKhOzv8t@ep-silent-morning-a29aajlm-pooler.eu-central-1.aws.neon.tech/neondb?sslmode=require"),
    "DATABASE_URL_UNPOOLED": getenv("DATABASE_URL_UNPOOLED", "postgresql://neondb_owner:npg_ZbR1VKhOzv8t@ep-silent-morning-a29aajlm.eu-central-1.aws.neon.tech/neondb?sslmode=require"),
    
    # Включаем асинхронные соединения 
    "USE_ASYNC_DRIVER": "True",
    
    # Поскольку мы теперь не управляем БД локально, не нужно ждать или мигрировать
    "WAIT_FOR_DB": "False",
    "MIGRATE_DB": "False",
}

# -*- FastApi running on port 8000:8000
dev_fastapi = FastApi(
    name=f"{ws_settings.ws_name}-api",
    image=dev_image,
    command="uvicorn api.main:app --reload",
    port_number=8000,
    debug_mode=True,
    mount_workspace=True,
    env_vars=container_env,
    use_cache=True,
    # Read secrets from secrets/dev_api_secrets.yml
    secrets_file=ws_settings.ws_root.joinpath("workspace/secrets/dev_api_secrets.yml"),
    # Убираем зависимость от локальной БД
    # depends_on=[dev_db],
)

# -*- Dev DockerResources
dev_docker_resources = DockerResources(
    env=ws_settings.dev_env,
    network=ws_settings.ws_name,
    # Убираем локальную БД из списка приложений
    apps=[dev_fastapi],
)
