'''
client-side application
'''
import asyncio
from aiortc import RTCPeerConnection, RTCSessionDescription, VideoStreamTrack, RTCIceCandidate
from aiortc.contrib.signaling import TcpSocketSignaling, BYE
import cv2
from multiprocessing import Process, Queue, Value
def imageParse(q, X, Y):
    '''
    process received video frame and detect the position of the circle on the frame;
    update the x and y values
    :param q: A multiprocessing Queue for receiving video frames
    :param X: A multiprocessing integer value for storing received x
    :param Y: A multiprocessing integer value for storing received y
    '''
    try:
        while True:
            frame = q.get()
            if frame is None:
                break
            mask = cv2.inRange(frame, (0, 200, 0), (100, 255, 100))
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            if contours:
                c = max(contours, key=cv2.contourArea)
                ((x, y), radius) = cv2.minEnclosingCircle(c)
                X.value = int(x)
                Y.value = int(y)
    except KeyboardInterrupt:
        pass

async def handle_frame(pc, track):
    '''
    handle received video frames, display them, and send object coordinates to server
    :param pc: RTC Peer Connection
    :param track: The video stream track
    '''
    dc = pc.createDataChannel('coords')
    X = Value('i', 0)
    Y = Value('i', 0)
    process_q = Queue()

    process_a = Process(target=imageParse, args=(process_q, X, Y))
    process_a.start()

    try:
        while True:
            frame = await track.recv()
            img = frame.to_ndarray(format="bgr24")
            cv2.imshow("Server generated stream", img)
            if cv2.waitKey(25) & 0xFF == ord('q'):
                break
            process_q.put(img)
            dc.send(str(X.value) + "," + str(Y.value))
    except Exception as e:
        print("Client Keyboard Interruption")
    finally:
        process_q.put(None)  # Send sentinel value
        process_a.join()


async def run_pc(pc, signaling):
    '''
    receive offer from the server and send messages to the server
    :param pc: RTC Peer Connection
    :param signaling: Tcp socket signaling
    '''
    await signaling.connect()

    @pc.on("track")
    async def on_track(track):
        await handle_frame(pc, track)

    @pc.on("datachannel")
    def on_datachannel(channel):
        @channel.on("message")
        def on_message(message):
            print('Message:', message)

    while True:
        obj = await signaling.receive()

        if isinstance(obj, RTCSessionDescription):
            await pc.setRemoteDescription(obj)
            if obj.type == "offer":
                await pc.setLocalDescription(await pc.createAnswer())
                await signaling.send(pc.localDescription)
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
        cv2.destroyAllWindows()
