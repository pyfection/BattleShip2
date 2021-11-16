import uuid
import requests

BASE_URL = 'https://jpsmjav8dc.execute-api.eu-central-1.amazonaws.com/prod'


def connect(userid, username, ships):
    url = f'{BASE_URL}/connect?userid={userid}&username={username}&ships={ships}'
    print("Connecting to", url)
    return requests.get(url=url)


def disconnect(userid):
    url = f'{BASE_URL}/disconnect?userid={userid}'
    return requests.get(url=url)


def check_turn(userid):
    url = f'{BASE_URL}/check-turn?userid={userid}'
    return requests.get(url=url)


def test1():  # One user connecting and disconnecting
    user1id = str(uuid.uuid4())
    req = connect(user1id, 'Tester', 5)
    print("Connection:", req.json())
    req = disconnect(user1id)
    print("Disconnection:", req.json())


def test2():  # Two users connecting and checking turns
    user1id = str(uuid.uuid4())
    user2id = str(uuid.uuid4())

    req = connect(user1id, 'Host', 5)
    print("Connection:", req.json())
    req = connect(user2id, 'Guest', 5)
    print("Connection:", req.json())

    req = check_turn(user1id)
    print("Check Turn:", req.json())

    req = disconnect(user1id)
    print("Disconnection:", req.json())
    req = disconnect(user2id)
    print("Disconnection:", req.json())


if __name__ == '__main__':
    # test1()
    test2()
