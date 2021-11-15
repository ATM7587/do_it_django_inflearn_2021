# pull official base image
FROM python:3.9-slim-buster

# set work directory
# 프로젝트의 작업폴더를 지정함
WORKDIR /usr/src/app

# set environment variable
ENV PYTHONDONTWRITEBYTECODE 1
# .pvc인 파일을 생성하지 않도록 함
ENV PYTHONUNBUFFERED 1
# 버퍼링 없이 파이썬 로그를 출력함

COPY . /usr/src/app/

# install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
