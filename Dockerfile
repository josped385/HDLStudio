FROM python:3.13-slim-bookworm AS hdlstudio

LABEL maintainer="josped385"

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    iverilog \
    gtkwave \
    graphviz \
    verilator \
    qt6-base-dev \
    libqt6svg6 \
    libxcb-cursor0 \
    libegl1 \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/hdlstudio

COPY . .

RUN mkdir -p tools/iverilog/bin tools/gtkwave/bin tools/graphviz/Graphviz-15.0.0-win64/bin && \
    ln -sf /usr/bin/iverilog tools/iverilog/bin/iverilog.exe && \
    ln -sf /usr/bin/vvp tools/iverilog/bin/vvp.exe && \
    ln -sf /usr/bin/gtkwave tools/gtkwave/bin/gtkwave.exe && \
    ln -sf /usr/bin/dot tools/graphviz/Graphviz-15.0.0-win64/bin/dot.exe

RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["python", "/opt/hdlstudio/main.py"]
