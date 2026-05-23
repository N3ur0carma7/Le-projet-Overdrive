import socket
import threading
import time
import json
import ast

from core.Class.batiments import *
from core.Class.monster import Monster
from core.Class.player import *

HEADER = 64
PORT = 5050
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "[DISCONNECT]"
CLIENT = None


recv_buffer = b""

def safe_tuple_from_str(key_str):
    """Convertit '(1, 2)' → (1, 2) de manière sécurisée"""
    if not (isinstance(key_str, str) and key_str.startswith('(') and key_str.endswith(')')):
        return key_str
    try:
        content = key_str[1:-1]
        return ast.literal_eval(f"({content},)")
    except:
        return key_str

def parse_dict_tuple_keys(dic):
    result = {}
    for k, v in dic.items():
        result[safe_tuple_from_str(k)] = v
    return result


def search_serv():
    TIMOUT_RESEARCH = 10
    debut = time.time()
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print("[INFO] Socket created\n")
    print("[RESEARCH] server researching")
    s.settimeout(1.0)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    s_addr = None
    while time.time() - debut < TIMOUT_RESEARCH and s_addr is None:
        try:
            s.sendto("searching...".encode(),   ("255.255.255.255", 5051))
            s_data, s_addr = s.recvfrom(1024)
            print(f"[SERVER] {s_addr} found...")
            print(f"[SERVER] {s_data.decode()} recieved\n")
        except socket.timeout:
            pass
        time.sleep(0.2)
    s.close()
    if s_addr is None :
        return -1
    else:
        return s_addr[0]

def recv_full_message(sock):
    global recv_buffer
    sock.settimeout(0.5)

    try:
        try:
            chunk = sock.recv(4096)
            if not chunk:
                return None
            recv_buffer += chunk
        except socket.timeout:
            return None

        while len(recv_buffer) >= HEADER:
            header = recv_buffer[:HEADER].decode().strip()

            try:
                msg_len = int(header)
            except:
                print("HEADER CORROMPU:", header)
                recv_buffer = recv_buffer[1:]
                continue

            if len(recv_buffer) < HEADER + msg_len:
                return None

            msg = recv_buffer[HEADER:HEADER + msg_len].decode()
            recv_buffer = recv_buffer[HEADER + msg_len:]

            return msg  # <-- juste la string JSON

        return None

    except Exception as e:
        print("Erreur recv:", e)
        return None


def handle_message_client(msg, client):
    try:
        data = json.loads(msg)
        msg_type = data.get("type")

        if msg_type == "list":
            liste = data["payload"]
            print(f"[LIST] server has send a list: {liste}")
            return liste, "list"

        elif msg_type == "dict":
            raw_obj = data["payload"]
            obj = parse_dict_tuple_keys(raw_obj)
            print(f"[DICT] server has send a ditionary: {obj}")
            return obj, "dict"

        elif msg_type == "tuple":
            tup =data["payload"]
            print(f"[TUPLE] server has send a tuple: {tup}")
            return tup, "tuple"

        elif msg_type == "str":
            stri = data["payload"]
            print(f"[STR] server has send : {stri}")
            return stri, "str"


        elif msg_type == "int" :
            ints = data["payload"]
            print(f"[INT] server has send : {ints}")
            return ints, "int"

        elif msg_type == "bool" :
            bools = data["payload"]
            print(f"[BOOL] server has send : {bools}")
            return bools, "bool"

        elif msg_type == "float":
            flot = data["payload"]
            print(f"[FLOAT] server has send : {flot}")
            return flot, "float"

        elif msg_type == "batiment":
            b_dict = data["payload"]
            bat = Batiment.from_dict(b_dict)
            print(f"[BATIMENT] server has send : {bat.type} niv={bat.niveau} pos=({bat.x},{bat.y})")
            return bat, "batiment"

        elif msg_type == "liste_batiments":
            print("ok")
            liste_dicts = data["payload"]
            bats = [Batiment.from_dict(d) for d in liste_dicts]
            print(f"[LISTE BATIMENTS] reçue : {[str(b) for b in bats]}")
            return bats, "liste_batiments"

        elif msg_type == "liste_monstres":
            print("ok")
            liste_dicts = data["payload"]
            montres = [Monster.from_dict(d) for d in liste_dicts]
            print(f"[LISTE MONSTRES] reçue : {[str(b) for b in montres]}")
            return montres, "liste_monstres"

        elif msg_type == "liste_joueurs":
            print("arriver")
            liste_dicts = data["payload"]
            print(liste_dicts)
            liste_dicts[0]["pos"] = tuple(liste_dicts[0]["pos"])
            for i in range (len(liste_dicts[0]["path"])):
                liste_dicts[0]["path"][i] = tuple(liste_dicts[0]["path"][i])
            plays = [Player.from_dict(d) for d in liste_dicts]
            print(f"[LISTE JOUEURS] reçue : {[str(b) for b in plays]}")
            return plays, "liste_joueurs"

        else:
            print(f"[UNKNOWN JSON] server: {data}")
            return None, None

    except json.JSONDecodeError:
        return msg, "text"





result = None

def receive_loop(client):
    global recv_buffer, result, is_connected
    is_connected = True
    while True:
        try:
            chunk = client.recv(4096)
            if not chunk:
                print("[DISCONNECTED] serveur déconnecté")
                is_connected = False
                recv_buffer = b""
                break
            recv_buffer += chunk

            while len(recv_buffer) >= HEADER:
                header = recv_buffer[:HEADER].decode().strip()
                try:
                    msg_len = int(header)
                except:
                    recv_buffer = recv_buffer[1:]
                    continue

                if len(recv_buffer) < HEADER + msg_len:
                    break

                msg = recv_buffer[HEADER:HEADER + msg_len].decode()
                recv_buffer = recv_buffer[HEADER + msg_len:]

                if msg == DISCONNECT_MESSAGE:
                    is_connected = False
                    client.close()
                    return

                result = handle_message_client(msg, client)

        except OSError:
            recv_buffer = b""
            break


def send_server (msg, client):
    global FORMAT
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)

def send_list_client (lst, client):
    data = json.dumps({"type": "list", "payload": lst})
    send_server(data, client)
def send_str_client (str, client):
    data = json.dumps({"type": "str", "payload": str})
    send_server(data, client)

def send_int_client (int, client):
    data = json.dumps({"type": "int", "payload": int})
    send_server(data, client)
def send_bool_client (bool, client):
    data = json.dumps({"type": "bool", "payload": bool})
    send_server(data, client)

def send_float_client (float, client):
    data = json.dumps({"type": "float", "payload": float})
    send_server(data, client)


def send_tuple_client(tup, client):
    data = json.dumps({"type": "tuple", "payload": list(tup)})
    send_server(data, client)

def send_dict_client(dic, client):
    data = json.dumps({"type": "dict", "payload": dic})
    send_server(data, client)

def dict_keys_to_str_client(dic):
    result = {}
    for k, v in dic.items():
        result[str(k)] = v
    return result

def send_dict_tuple_client(dict_tuple, client):
    dic = dict_keys_to_str_client(dict_tuple)
    data = json.dumps({"type": "dict", "payload": dic})
    send_server(data, client)


def send_batiment_client(batiment, client):
    payload = batiment.to_dict()
    data = json.dumps({"type": "batiment", "payload": payload})
    send_server(data, client)

def send_liste_batiments_client(liste_batiments, client):
    # transforme chaque Batiment en dict sérialisable
    payload = [b.to_dict() for b in liste_batiments]
    data = json.dumps({"type": "liste_batiments", "payload": payload})
    send_server(data, client)

def send_liste_joueurs_client(liste_joueurs, client):
    payload = [j.to_dict() for j in liste_joueurs]
    payload[0]["pos"] = list(payload[0]["pos"])
    for i in range (len(payload[0]["path"] )):
        payload[0]["path"][i] = list(payload[0]["path"][i])
    data = json.dumps({"type": "liste_joueurs", "payload": payload})
    send_server(data, client)


def send_liste_monstres_client(liste_monstres, client):
    payload = [b.to_dict() for b in liste_monstres]
    data = json.dumps({"type": "liste_monstres", "payload": payload})
    send_server(data, client)


def disconnect():
    global CLIENT, recv_buffer
    if CLIENT is not None:
        try:
            send_server(DISCONNECT_MESSAGE, CLIENT)
            CLIENT.close()
        except OSError:
            pass
        finally:
            CLIENT = None
            recv_buffer = b""
thread_loop = None
is_connected = False
def connection():
    global CLIENT, recv_buffer, thread_loop, is_connected
    if CLIENT is not None:
        try:
            CLIENT.close()
        except OSError:
            pass
        CLIENT = None
        recv_buffer = b""
    if thread_loop is not None and thread_loop.is_alive():
        thread_loop.join(timeout=2)

    CLIENT = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    CLIENT.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    SERVER = search_serv()
    if SERVER == -1:
        print("[NOT FOUND] server not found")
        return None
    ADDR = (SERVER, PORT)
    try:
        CLIENT.connect(ADDR)
        is_connected = True
        print(f"[SERVER] {SERVER} connected")
        thread_loop = threading.Thread(target=receive_loop, args=(CLIENT,), daemon=True)
        thread_loop.start()
    except OSError:
        print(f"[ERROR] {SERVER} connection failed")
        CLIENT = None


