FROM python:3.13

ARG USERNAME PASSWORD
ENV TZ=Asia/Shanghai

WORKDIR /root

LABEL description="python fastapi backend port:8000"

RUN git clone https://$USERNAME:$PASSWORD@xxxx.git && \
    cd /root/fastapi && \
    bash run.sh --install

WORKDIR /root/fastapi

CMD ["fastapi", "run", "main.py"]

EXPOSE 8000

