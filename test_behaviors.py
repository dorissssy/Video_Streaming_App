import pytest
from client import imageParse
from multiprocessing import Queue, Value

# Test for imageParse function
def test_imageParse():
    q = Queue()
    X = Value('i', 0)
    Y = Value('i', 0)

    # Insert a sentinel value to immediately break the loop
    q.put(None)
    imageParse(q, X, Y)

    # Since no frame is processed, the values should remain at 0
    assert X.value == 0
    assert Y.value == 0
from server import BouncingBall, compute_errors

def test_imageParse_sentinel():
    q = Queue()
    X = Value('i', 0)
    Y = Value('i', 0)

    q.put(None)  # Only inserting the sentinel value
    imageParse(q, X, Y)

    assert X.value == 0
    assert Y.value == 0


# Test for BouncingBall's initialization and next_frame function
def test_BouncingBall():
    ball = BouncingBall()
    frame, x, y = ball.next_frame()

    # Check if the ball position has changed after one frame
    assert x == ball.width // 2 + ball.speed[0]
    assert y == ball.height // 2 + ball.speed[1]

# Test for computeErrors function using a mock function to capture printed values
def test_computeErrors(capsys):
    x1, y1, x2, y2 = 10, 10, 20, 20
    compute_errors(x1, y1, x2, y2)
    captured = capsys.readouterr()

    # Check if the printed error is as expected
    assert "Error: 14.142135623730951" in captured.out

def test_BouncingBall_movement():
    ball = BouncingBall(width=800, height=600, speed=(10, 10))

    # Simulate a hit on the right wall
    ball.x = 790
    ball.next_frame()
    assert ball.x == 780  # It should move left now

    # Simulate movement in the center
    ball.x = 400
    ball.next_frame()
    assert ball.x == 390
