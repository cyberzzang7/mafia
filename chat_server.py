import codes
import server_add as sa
import time
import pyautogui
from user import User

#!/usr/bin/env python3
"""Server for multithreaded (asynchronous) chat application."""
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
count = 0       # 사람 수 카운트
jobs = ["마피아", "마피아", "시민", "시민", "시민", "군인", "의사", "경찰"]  # 직업 배열
jobs_num = codes.jobs_random()
isGameStarted = False   # 게임 시작 여부
day_count = 1   # 날 카운트
time_day = 30  # 낮 시간
time_vote = 20  # 투표 시간
time_night = 20  # 밤 시간
life = 1        # 생명 갯수
users = []
votes = []
kill_name = ''
mafia = 'false'  # 마피아 계열 직업인지 아닌지
people_temp = 0  # 직업 배열 temp

# 마피아 게임 시작 시 + 클라이언트 연결 시


def accept_incoming_connections():
    """Sets up handling for incoming clients."""
    global isGameStarted
    while True:
        client, client_address = SERVER.accept()
        print("%s:%s has connected." % client_address)
        client.send(
            bytes("Mafia Game! Now type your name and press enter!", "utf8"))
        addresses[client] = client_address
        th1 = Thread(target=handle_client, args=(client,))
        th1.start()

# 클라이언트 접속 시 프로그램


def handle_client(client):  # Takes client socket as argument.
    """Handles a single client connection."""

    global count
    global time_day
    global time_vote
    global time_night
    global life
    global jobs_num
    global people_temp

    name = client.recv(BUFSIZ).decode("utf8")
    welcome = 'Welcome %s! If you ever want to quit, type {quit} to exit.' % name
    client.send(bytes(welcome, "utf8"))
    msg = "%s has joined the chat!" % name

    users.append(
        User(name=name, job=jobs[jobs_num[people_temp]], life=1))
    votes.append(0)
    print(users[people_temp].name)
    print(users[people_temp].job)
    people_temp += 1

    count += 1
    msg += " %d / 8 " % count
    broadcast(bytes(msg, "utf8"))
    clients[client] = name
    print(name)

    # 채팅과 게임 동시 시작 구현 by Thread
    th1 = Thread(target=Chatting, args=(client, name, ))
    th2 = Thread(target=game_started, args=(client,))
    th3 = Thread(target=autoScroll)

    th1.start()
    th2.start()
    th3.start()


# 채팅


def Chatting(client, name):
    global count
    global autoScroll
    global users
    global kill_name

    while True:
        msg = client.recv(BUFSIZ)
        if bytes("{vote}", "utf8") in msg:
            msg = (str)(msg).replace('{vote}', '')
            print(msg)
            for i in range(len(users)):
                if("b'"+users[i].name+"'" == msg):
                    votes[i] += 1
                    for i in range(len(votes)):
                        print(votes[i])
            msg += "를 투표하셨습니다."
            client.send(bytes(msg, "utf8"))
        elif bytes("{kill}", "utf8") in msg:
            msg = (str)(msg).replace('{kill}', '')
            print(msg)
            for i in range(len(users)):
                if(users[i].name == "마피아"):
                    if("b'"+users[i].name+"'" == msg):
                        print(msg)
                        kill_name = msg
                        msg += "를 죽일것입니다."
                        client.send(bytes(msg, "utf8"))
                        print(kill_name)

        elif msg != bytes("{quit}", "utf8"):
            broadcast(msg, name+": ")
        else:
            client.send(bytes("{quit}", "utf8"))
            client.close()
            del clients[client]
            msg = "%s has left the game." % name
            count -= 1
            msg += " %d / 8 " % count
            broadcast(bytes(msg, "utf8"))
            break

# 투표 수가 가장 높을 시 사망


def vote_dead():
    global votes
    max_idx = votes.index(max(votes))
    msg = "System : " + users[max_idx].name + "가 투표로 사망하였습니다."
    print(msg)
    broadcast(bytes(msg, "utf8"))


def mafia_kill(kill_name):
    msg = "System : " + kill_name + "가 마피아에의해 사망하였습니다."
    print(msg)
    broadcast(bytes(msg, "utf8"))


def broadcast(msg, prefix=""):  # prefix is for name identification.
    """Broadcasts a message to all the clients."""

    for sock in clients:
        sock.send(bytes(prefix, "utf8")+msg)

# 사람 수가 8명이 되면 마피아 게임 시작


def game_started(client):
    global count    # 사람 수
    global users    # 직업 객체 배열

    if(count == 3):
        global isGameStarted
        isGameStarted = True
        temp = 0   # 직업 랜덤 인덱스 배열 증가 숫자
        msg = "Mafia-Game is start!!\n"
        broadcast(bytes(msg, "utf8"))
        for client in clients:
            msg = "당신은 " + users[temp].job + "입니다. "
            client.send(bytes(msg, "utf8"))
            temp += 1
        timer()

# 타이머 함수


def timer():
    global isGameStarted
    global day_count
    global kill_name

    if (isGameStarted == True):
        while True:
            # 낮
            msg = "\n" + (str)(day_count) + "번째 낮입니다."
            broadcast(bytes(msg, "utf8"))
            sec = time_day
            while (sec != 0):
                if(sec == 180):
                    broadcast(bytes("\n3분 남았습니다", "utf8"))
                elif(sec == 120):
                    broadcast(bytes("\n2분 남았습니다", "utf8"))
                elif(sec == 60):
                    broadcast(bytes("\n1분 남았습니다", "utf8"))
                elif(sec == 30):
                    broadcast(bytes("\n30초 남았습니다", "utf8"))
                elif(sec == 15):
                    broadcast(bytes("\n15초 남았습니다", "utf8"))
                elif(sec <= 5):
                    msg = (str)(sec)
                    broadcast(bytes(msg, "utf8"))
                sec = sec-1
                time.sleep(1)

            # 투표시간
            msg = "\n투표시간입니다."
            broadcast(bytes(msg, "utf8"))
            sec2 = time_vote
            while (sec2 != 0):
                if(sec2 == 20):
                    broadcast(bytes("\n20초 남았습니다", "utf8"))
                elif(sec2 == 10):
                    broadcast(bytes("\n10초 남았습니다", "utf8"))
                elif(sec2 == 5):
                    broadcast(bytes("\n5초 남았습니다", "utf8"))
                sec2 = sec2-1
                time.sleep(1)
            vote_dead()

            # 밤
            msg = "\n" + (str)(day_count) + "번째 밤입니다."
            broadcast(bytes(msg, "utf8"))
            sec2 = time_night
            while (sec2 != 0):
                if(sec2 == 20):
                    broadcast(bytes("\n20초 남았습니다", "utf8"))
                elif(sec2 == 10):
                    broadcast(bytes("\n10초 남았습니다", "utf8"))
                elif(sec2 == 5):
                    broadcast(bytes("\n5초 남았습니다", "utf8"))
                sec2 = sec2-1
                time.sleep(1)
                print(kill_name)
                # if(sec2 == 0):
                # 마피아가 죽이는 함수 실행
            mafia_kill(kill_name)
            day_count += 1  # 날 증가
            if (day_count == 3):
                break

# auto scroll


def autoScroll():
    pyautogui.time.sleep(3)
    while True:
        pyautogui.scroll(-3)
        pyautogui.time.sleep(1)


clients = {}
addresses = {}

HOST = sa.HOST
PORT = sa.PORT

BUFSIZ = sa.BUFSIZ
ADDR = sa.ADDR

SERVER = socket(AF_INET, SOCK_STREAM)
SERVER.bind(ADDR)

if __name__ == "__main__":
    SERVER.listen(5)
    print("Waiting for connection...")
    ACCEPT_THREAD = Thread(target=accept_incoming_connections)
    ACCEPT_THREAD.start()
    ACCEPT_THREAD.join()
    SERVER.close()
