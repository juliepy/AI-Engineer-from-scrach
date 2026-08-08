# 固件交叉编译工具链镜像（只负责编出目标架构产物，不在镜像里「跑固件」）
FROM debian:bookworm-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        gcc-aarch64-linux-gnu \
        binutils-aarch64-linux-gnu \
        file \
        git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /src
COPY hello.c scripts/build_in_container.sh /tmp/demo/
RUN mkdir -p /src/scripts \
    && cp /tmp/demo/hello.c /src/hello.c \
    && cp /tmp/demo/build_in_container.sh /src/scripts/build_in_container.sh \
    && chmod +x /src/scripts/build_in_container.sh \
    && rm -rf /tmp/demo

CMD ["bash", "/src/scripts/build_in_container.sh"]
