'''
server side application
'''
import cv2
import numpy as np
import asyncio
from aiortc import RTCPeerConnection, RTCSessionDescription, VideoStreamTrack, RTCIceCandidate
from aiortc.contrib.signaling import TcpSocketSignaling, BYE
from av import VideoFrame

class BouncingBall:
    """
    Represents a bouncing ball class
    accepts width, height of the frame, radius of the ball, and speed of the bouncing ball as parameter
    next_frame(): Generates the next frame of the bouncing ball.
    """

    def __init__(self, width=800, height=600, radius=10, speed=(4, 4)):
        self.width = width
        self.height = height
        self.x, self.y = width // 2, height // 2
        self.radius = radius
        self.speed = speed

    def next_frame(self):
        frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)

        if not (self.radius < self.x < self.width - self.radius):
            self.speed = (-self.speed[0], self.speed[1])
        if not (self.radius < self.y < self.height - self.radius):
            self.speed = (self.speed[0], -self.speed[1])

        self.x += self.speed[0]
        self.y += self.speed[1]

        cv2.circle(frame, (self.x, self.y), self.radius, (0, 255, 0), -1)
        return frame, self.x, self.y
class BouncingBallTrack(VideoStreamTrack):
    '''
    creates a bouncing ball track that is of typpe VideoStreamTrack
    '''
    def __init__(self):
        super().__init__()  # Don't forget to call super's init
        self.ball = BouncingBall()
        self.running = True
    async def recv(self):
        pts, time_base = await self.next_timestamp()

        frame, x, y= self.ball.next_frame()
        video_frame = VideoFrame.from_ndarray(frame, format="bgr24")
        video_frame.pts = pts
        video_frame.time_base = time_base

        return video_frame

def compute_errors(x1, y1, x2, y2):
    '''
    computes the error between the actual coordinates and the receiived coordinates
    and prints them out
    :param x1: actual x
    :param y1: actual y
    :param x2: received x
    :param y2: received y
    '''
    error = ((x1 - x2)**2 + (y1 - y2)**2)**(1/2)
    print("Actual:", (x1, y1))
    print("Received:", (x2, y2))
    print("Error:", error)

async def run_pc(pc, signaling):
    '''
    Initializes the server and creates a datachannel to receive messages from the client;
    creates an offer and send to the client
    :param pc: RTC Peer Connection
    :param signaling: Tcp socket signaling
    '''
    print("Server Initialized")

    track = BouncingBallTrack()
    await signaling.connect()
    pc.createDataChannel('c')

    @pc.on("datachannel")
    def on_datachannel(channel):
        @channel.on("message")
        async def on_message(message):
            coordinates = message.split(",")
            compute_errors(track.ball.x, track.ball.y, int(coordinates[0]), int(coordinates[1]))

    pc.addTrack(track)
    offer = await pc.createOffer()
    await pc.setLocalDescription(offer)
    await signaling.send(offer)
    while True:
        obj = await signaling.receive()

        if isinstance(obj, RTCSessionDescription):
            await pc.setRemoteDescription(obj)
        elif isinstance(obj, RTCIceCandidate):
            await pc.addIceCandidate(obj)
        else:
            print("Shutting down")
            break
if __name__ == "__main__":
    pc = RTCPeerConnection()
    signaling = TcpSocketSignaling('0.0.0.0', 1234)
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(run_pc(pc, signaling))
    except KeyboardInterrupt:
        pass
    finally:
        loop.run_until_complete(signaling.close())
        loop.run_until_complete(pc.close())