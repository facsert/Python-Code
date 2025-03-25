FROM python:3.13

ARG USERNAME PASSWORD

ENV TZ=Asia/Shanghai 
ENV HOME="/root/fastapi"

WORKDIR /root

LABEL description="python fastapi backend port:8000"

RUN git clone https://$USERNAME:$PASSWORD@xxxx.git && \
    cd $HOME && \
    bash run.sh --install

WORKDIR $HOME

CMD ["fastapi", "run", "main.py"]

EXPOSE 8000

