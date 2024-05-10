import socket
from _thread import *
import sys
import pickle

server = "127.0.0.1"
port = 5555

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server, port))
except socket.error as e:
    str(e)

s.listen()
print("Waiting for a connection, Server Started")

def read_pos(str):
    str = str.split(",")
    return (int(str[0]), int(str[1]), str[2], int(str[3]), int(str[4]), float(str[5]), int(str[6]), int(str[7]))

def make_pos(tup):
    return str(tup[0]) + "," + str(tup[1]) + "," + tup[2] + "," + str(tup[3]) + "," + str(tup[4]) + "," + str(tup[5]) + "," + str(tup[6]) + "," + str(tup[7])
    
class Game:
    def __init__(self, id):
        self.pos = [(96, 800-96, "right", 0, 0, 0.0, 0, 0),(96, 800-96, "right", 0, 0, 0.0, 0, 0)]
        self.id = id

games = {}
idCounts = 0

def threaded_client(conn, player, gameId):
    global idCounts
    game = games[gameId]
    conn.send(str.encode(make_pos(game.pos[player])))
    reply = ""
    while True:
        try:
            data = read_pos(conn.recv(2048).decode())
            game.pos[player] = data
            if not data:
                print("Disconnected")
                break
            else:
                if player == 1:
                    reply = game.pos[0]
                else:
                    reply = game.pos[1]

                print("Received: ", data)
                print("Sending: ", reply)

            conn.sendall(str.encode(make_pos(reply)))
        except:
            break

    print("Lost connection")

    try:
        del games[gameId]
        print("Closing Game", gameId)
    except:
        pass

    idCounts -= 1
    conn.close()

while True:
    conn, addr = s.accept()
    print("Connected to:", addr)

    idCounts += 1
    currentPlayer = 0

    gameId = (idCounts - 1) // 2

    if idCounts % 2 == 1:
        games[gameId] = Game(gameId)
        print("Creating a new game...")
    else:       
        currentPlayer = 1

    start_new_thread(threaded_client, (conn, currentPlayer, gameId ))
    currentPlayer += 1