FROM python:latest

ARG USERNAME PASSWORD

ENV TZ=Asia/Shanghai 
ENV HOME="/root/devops"

WORKDIR /root

LABEL description="python fastapi backend port:8000"

RUN git clone http://192.168.31.30/facsert/devops.git && \
    cd $HOME && \
    python -m pip install -r requirements.txt -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com

WORKDIR $HOME

CMD ["fastapi", "run", "main.py"]

EXPOSE 8000

