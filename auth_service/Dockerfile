FROM python:3.12
WORKDIR /usr/local/app

RUN mkdir auth_service

COPY requirements.txt ./auth_service
RUN pip install -r ./auth_service/requirements.txt

COPY config.py ./auth_service

COPY auth_service ./auth_service/auth_service
EXPOSE 5000

CMD ["python3", "-m", "auth_service.auth_service.app", "--env=dev"]

