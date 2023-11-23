FROM python:3.10.10-slim
RUN apt-get update && apt-get install -y libgtk2.0-dev pkg-config libxcb-cursor0 ffmpeg libsm6 libxext6 '^libxcb.*-dev' libx11-xcb-dev libglu1-mesa-dev libxrender-dev libxi-dev libxkbcommon-dev libxkbcommon-x11-dev
RUN mkdir -p /server

COPY ../server.py .
COPY ../requirements.txt .
RUN pip install opencv-python==4.5.5.64
RUN pip install -r requirements.txt
EXPOSE 1234
CMD ["python3", "server.py"]