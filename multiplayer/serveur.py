import socket
import threading
import json
import time
import ast
from importlib.metadata import pass_none

from core.Class.batiments import *
from core.Class.monster import Monster
from core.Class.player import *
import screens.jeu as jeu
from screens.game_logic import players, batiments
FORMAT = "utf-8"
HEADER = 64
PORT = 5050
DISCONNECT = "[DISCONNECT]"
clients = {}
clients_indice = {}
SERVER = 0
STOPSEARCH = False
def search_client():
    global STOPSEARCH
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.settimeout(1.0)
    s.bind(("", 5051))
    print("[WAITING] the server is waiting for client...")
    while not STOPSEARCH:
        try:
            s_data, s_addr = s.recvfrom(1024)
            print(f"[FOUND] {s_addr} as been found...")
            s.sendto("searching client...".encode(FORMAT), s_addr)
        except socket.timeout:
            pass
        except Exception as e:
            print(f"[ERROR] in search_client: {e}")
            break
        time.sleep(0.5)
    s.close()

def connect_client ():
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        ADDR = ("0.0.0.0", PORT)
        server.bind(ADDR)
    except socket.error:
        return 1
    return server

def tuple_from_str(key_str):
    if not(isinstance(key_str, str) and key_str.startswith('(') and key_str.endswith(')')):
        return key_str
    try:
        content = key_str[1:-1]
        return ast.literal_eval(f"({content})")
    except:
        return key_str

def str_to_tuple_key(dic):
    result = {}
    for k, v in dic.items():
        result[tuple_from_str(k)] = v
    return result
def pos(client):
    global clients
    for i in clients.keys():
        send_float_server(float(number_connected), clients[i])
    send_int_server(number_connected - 1, client)

monsters = []
monster_director = None
def handle_monsters(liste_monstres, addr):
    global monsters, monster_director
    if monster_director is None:
        monster_director = addr
    elif monster_director != addr:
        if len(liste_monstres) > len(monsters):
            send_liste_monstres(monsters, addr)
        else :
            send_liste_monstres(liste_monstres, monster_director)
    else:
        send_liste_monstres(monsters, addr)





def handle_client(client, addr):
    global clients
    print(f"[NEW CLIENT] {addr} connected\n")
    send_dict_server({"server": "hello client"}, client)
    if number_connected > 1:
        for sujet2 in clients.keys():
            if batiments != []:
                payload = [b.to_dict() for b in batiments]  # message = liste de Batiment
                data = json.dumps({"type": "liste_batiments", "payload": payload})
                send_client(data, clients[sujet2])
    if jeu.TAILLE_CASE is not None:
        player = Player()
        player.pos = (jeu.TAILLE_CASE / 2, jeu.TAILLE_CASE / 2)
        players.append(player)

    for sujet in clients.keys():
        payload = [p.to_dict() for p in players]
        payload[0]["pos"] = list(payload[0]["pos"])
        for j in range(len(payload[0]["path"])):
            payload[0]["path"][j] = list(payload[0]["path"][j])
        data = json.dumps({"type": "liste_joueurs", "payload": payload})
        send_client(data, clients[sujet])
    while not stop_event.is_set():
        try:
            msg_len_str = client.recv(HEADER).decode(FORMAT).strip()
            if not msg_len_str:
                break
            msg_len = int(msg_len_str)
            msg = client.recv(msg_len).decode(FORMAT)
            if msg == DISCONNECT:
                break  # ← break au lieu de connected = False
            else:
                message, type = handle_message_recieved(msg, addr)
                if type == "str" and message == "pos":
                    pos(client)

                for i in clients.keys():
                    if i != addr:
                            if type == "list":
                                send_list_server(message, clients[i])
                            elif type == "dict":
                                data = json.dumps({"type": "str", "payload": "bien reÃ§u"})
                                send_client(data, clients[i])
                                send_dict_tuple_server(message, clients[i])
                                print(f"envoyer a {clients[i]}")
                            elif type == "str":
                                send_str_server(message, clients[i])
                            elif type == "int":
                                send_int_server(message, clients[i])
                            elif type == "bool":
                                send_bool_server(message, clients[i])
                            elif type == "float":
                                send_float_server(message, clients[i])
                            elif type == "tuple":
                                send_tuple_server(message, clients[i])
                            elif type == "batiment":
                                send_batiment_server(message.to_dict(), clients[i])
                            elif type == "liste_batiments":
                                # on renvoie la même liste sous forme de dicts
                                payload = [b.to_dict() for b in message]  # message = liste de Batiment
                                data = json.dumps({"type": "liste_batiments", "payload": payload})
                                send_client(data, clients[i])
                            elif type == "liste_joueurs":
                                payload = [p.to_dict() for p in message]
                                payload[0]["pos"] = list(payload[0]["pos"])
                                for j in range (len(payload[0]["path"])):
                                    payload[0]["path"][j] = list(payload[0]["path"][j])
                                data = json.dumps({"type": "liste_joueurs", "payload": payload})
                                send_client(data, clients[i])
                            elif type == "liste_monstres":
                                payload = [b.to_dict() for b in message]  # message = liste de Batiment
                                data = json.dumps({"type": "liste_monstres", "payload": payload})
                                send_client(data, clients[i])


        except Exception as e:
            pass
    if addr in clients:
        del clients[addr]
    disconnect(client)
    if len(clients) == 0:
        stop_server()

def handle_message_recieved (msg, addr):
    try:
        data = json.loads(msg)
        msg_type = data.get("type")
        if msg_type == "list":
            liste = data["payload"]
            print(f"[LIST] {addr} : {liste}")
            return liste, msg_type

        elif msg_type == "dict":
            raw_dic = data["payload"]
            dic = str_to_tuple_key(raw_dic)
            print(f"[DICT] {addr} : {dic}")
            return dic, msg_type

        elif msg_type == "tuple":
            tup = data["payload"]
            print(f"[TUP] {addr} : {tup}")
            return tup, msg_type

        elif msg_type == "str" :
            stri = data["payload"]
            print(f"[STR] {addr} : {stri}")
            return stri, msg_type

        elif msg_type == "int" :
            ints = data["payload"]
            print(f"[INT] {addr} : {ints}")
            return ints, msg_type

        elif msg_type == "bool" :
            bools = data["payload"]
            print(f"[BOOL] {addr} : {bools}")
            return bools, msg_type

        elif msg_type == "float":
            flot = data["payload"]
            print(f"[FLOAT] {addr} : {flot}")
            return flot, msg_type

        elif msg_type == "batiment":
            b_dict = data["payload"]
            bat = Batiment.from_dict(b_dict)
            print(f"[BATIMENT] {addr} : {bat.type} niv={bat.niveau} pos=({bat.x},{bat.y})")
            return bat, msg_type

        elif msg_type == "liste_batiments":
            liste_dicts = data["payload"]  # liste de dicts
            bats = [Batiment.from_dict(d) for d in liste_dicts]
            print(f"[LISTE BATIMENTS] {addr} : {[str(b) for b in bats]}")
            return bats, "liste_batiments"
        
        elif msg_type == "liste_joueurs":
            liste_dicts = data["payload"]
            liste_dicts[0]["pos"] = tuple(liste_dicts[0]["pos"])
            for i in range (len(liste_dicts[0]["path"])):
                liste_dicts[0]["path"][i] = tuple(liste_dicts[0]["path"][i])
            plays = [Player.from_dict(d) for d in liste_dicts]
            print(f"[LISTE JOUEURS] {addr} : {[str(b) for b in plays]}")
            return plays, "liste_joueurs"
        elif msg_type == "liste_monstres":
            liste_dicts = data["payload"]  # liste de dicts
            monstre = [Monster.from_dict(d) for d in liste_dicts]
            print(f"[LISTE MONSTRE] {addr} : {[str(b) for b in monstre]}")
            handle_monsters(monstre, addr)
            return monstre, "liste_monstres"
    except json.JSONDecodeError:
        print(f"[ERROR] {addr} : {msg}")
        return ""

def disconnect (client):
    global clients, clients_indice
    print(f"[STOP] client disconnected")
    print(clients_indice[client])
    i = clients_indice[client]
    players.pop(clients_indice[client])
    for client in clients_indice:
        clients_indice[client] -= 1 if clients_indice[client] > i else 0
    for client in clients_indice:
        try:
            send_int_server(clients_indice[client], client)
        except:
            pass
    for sujet in clients.keys():
        payload = [p.to_dict() for p in players]
        payload[0]["pos"] = list(payload[0]["pos"])
        for j in range(len(payload[0]["path"])):
            payload[0]["path"][j] = list(payload[0]["path"][j])
        data = json.dumps({"type": "liste_joueurs", "payload": payload})
        send_client(data, clients[sujet])
    number_connected =-1
    client.close()

def send_client (msg, client):
    global FORMAT
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)

def send_list_server(lst, client):
    data = json.dumps({"type": "list", "payload": lst})
    send_client(data, client)

def send_dict_server(dic, client):
    data = json.dumps({"type": "dict", "payload": dic})
    send_client(data, client)

def dict_keys_to_str_server(dic):
    result = {}
    for k, v in dic.items():
        result[str(k)] = v
    return result

def send_dict_tuple_server(dict_tuple, client):
    dic = dict_keys_to_str_server(dict_tuple)
    data = json.dumps({"type": "dict", "payload": dic})
    send_client(data, client)

def send_str_server (str, client):
    data = json.dumps({"type": "str", "payload": str})
    send_client(data, client)

def send_int_server (int, client):
    data = json.dumps({"type": "int", "payload": int})
    send_client(data, client)

def send_bool_server (bool, client):
    data = json.dumps({"type": "bool", "payload": bool})
    send_client(data, client)

def send_float_server (float, client):
    data = json.dumps({"type": "float", "payload": float})
    send_client(data, client)


def send_tuple_server(tup, client):
    data = json.dumps({"type": "tuple", "payload": list(tup)})
    send_client(data, client)

def send_batiment_server(batiment, client):
    payload = batiment.to_dict()
    data = json.dumps({"type": "batiment", "payload": payload})
    send_client(data, client)

def send_liste_monstres (liste_monstres, client):
    payload = [j.to_dict() for j in liste_monstres]
    data = json.dumps({"type": "liste_monstres", "payload": payload})
    send_client(data, client)

stop_event = threading.Event()

def stop_server():
    global STOPSEARCH
    stop_event.set() # signale à tous les threads de s'arrêter
    for client in clients:
        clients[client].close()
    SERVER.close()     # débloque server.accept()
    for client in clients.values():
        client.close()
    STOPSEARCH = True

number_connected = 0

def start(server):
    global number_connected
    end = False
    broadcast_thread = threading.Thread(target=search_client, daemon=True)
    broadcast_thread.start()
    server.listen()
    print("[READY] the server is ready")
    while not end:
        try:
            client, addr = server.accept()
        except OSError:
            break
        clients[addr] = client
        clients_indice[client] = number_connected
        number_connected = len(clients)
        print(f"[ACTIVE CLIENTS] {number_connected}\n")
        client_thread = threading.Thread(target=handle_client, args=(client, addr))
        client_thread.daemon =True
        client_thread.start()
    stop_server()
    return "done"

def server_running():
    global SERVER, clients
    global STOPSEARCH
    STOPSEARCH = False
    SERVER = 0
    clients = {}
    stop_event.clear()
    print("[STARTING] the server is starting...")
    SERVER = connect_client()
    if SERVER == 1:
        print("[ERROR] already used port")
        return None
    start(SERVER)
    print("[ENDING] the server is ending...")