##Nimble Robotics Challenge

This application uses webRTC to facilitate the communication
between server and client to achieve real-time video streaming.  
Requirements
- Python 3.10.10 running on macOS

Libraries used: 
- cv2
- aiortc
- opencv
- asyncio
- av  

The server can be invoked using:  
`python3 server.py`

The client can be invoked using:  
`python3 client.py`

To run the test suite, use:  
`pytest test_behaviors.py`  