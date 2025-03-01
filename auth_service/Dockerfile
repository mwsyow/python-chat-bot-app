#MULTI-STAGE 
#use python-chat-bot-app dir as context for building the image
#hence . refers to python-chat-bot-app dir
#docker build -f auth_service/Dockerfile -t python-chat-bot-app/auth-service:VERSION .
#docker run -p HOST_PORT:CONTAINER_PORT --name=CONTAINER_NAME IMAGE_NAME
#add --env-file .env if we want to update env variables dynamically, e.g., a container's port is exposed internally on 5000 and the other on 5001.



FROM python:3.12-slim AS builder-image

WORKDIR /app

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY ./auth_service/requirements.txt .
RUN pip install -r ./requirements.txt


FROM python:3.12-slim AS final-image

WORKDIR /app

RUN mkdir auth_service

COPY --from=builder-image /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY .env ./auth_service/config.py ./auth_service
COPY ./auth_service/auth_service ./auth_service/auth_service

ENTRYPOINT ["python", "-m", "auth_service.auth_service.app"]
CMD ["--env=dev"]

