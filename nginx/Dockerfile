# pull official base image
FROM nginx:latest
# 도커 제공 Nginx 이미지 중 최신 버전을 사용

RUN rm /etc/nginx/conf.d/default.conf
# 도커가 기본으로 제공하는 설정값을 remove 명령어로 제거함

COPY nginx.conf /etc/nginx/conf.d
# 로컬에서 만든 conf.d를 Nginx 이미지에 복사한다.