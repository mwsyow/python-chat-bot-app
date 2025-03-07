# """MULTI-STAGE 
# NOTE:
#     use python-chat-bot-app dir as context for building the image hence . refers to python-chat-bot-app dir

# BUILD IMAGE:
#     docker build -f auth_service/Dockerfile -t python-chat-bot-app/auth-service:VERSION .

# RUN CONTAINER:
#     docker run -p HOST_PORT:CONTAINER_PORT --name=CONTAINER_NAME IMAGE_NAME

# UPDATE ENV IN RUNTIME:
#     `--env-file .env` 
#     if we want to update env variables dynamically, 
#     e.g., a container's port is exposed internally on 5000 and the other on 5001.

# PERSISTING DATA:
#     `-v VOLUME_NAME:PATH`  
#     PATH refers to path of data inside the container that we want to persist, 
#     in this case `/app/auth_service/auth_service/instance`.

# LOCAL DATA SHARING:
#    `--mount type=bind,source=PATH/HOST,target=PATH/CONTAINER,PERMISSION` 
#    in this case, type=bind,source=$(pwd)/auth_service/config.py,target=/app/auth_service/config.py,readonly
#    $(pwd) refers to current workdir.
#
# Since we are using docker compose the relative path is in project dir -> $(pwd)/auth_service
# """


FROM python:3.12-slim AS builder-image

WORKDIR /app

RUN apt-get update &&\
    apt-get install -y libpq-dev gcc

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install -r ./requirements.txt


FROM python:3.12-slim AS final-image

WORKDIR /app

RUN apt-get update &&\
    apt-get install -y libpq-dev gcc &&\
    rm -rf /var/lib/apt/lists/*

RUN mkdir auth_service

COPY --from=builder-image /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONBUFFERED=1

COPY auth_service ./auth_service/auth_service
COPY config.py ./auth_service/config.py

ENTRYPOINT ["python", "-m", "auth_service.auth_service.app"]


