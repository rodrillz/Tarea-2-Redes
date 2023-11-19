import socket
import threading
import json

host = '127.0.0.1'
port = 12345

clientes = []
socket2nombre = {}
nombre2socket = {} 
acepta = {}

with open('artefactos.json', 'r') as f:
    artefactos_dict = json.load(f)

# Diccionario para almacenar los artefactos de cada cliente
artefactosxcliente = {}

def desconectar(client_socket):
    global clientes
    global socket2nombre
    global nombre2socket
    global acepta

    mensaje_para_todos(f"[SERVER] Cliente {socket2nombre[client_socket]} se ha desconectado.\n".encode())
    clientes.remove(client_socket)
    del nombre2socket[socket2nombre[client_socket]]
    del socket2nombre[client_socket]
    del acepta[client_socket]
    client_socket.close()

def comandos(client_socket, comando):
    global clientes
    global socket2nombre
    global nombre2socket
    global artefactosxcliente
    global acepta

    if comando.startswith(f":p"):    # Comando para mensaje privado
        _, destinatario, mensaje = comando.split(" ", 2)
        if destinatario not in socket2nombre.keys():
            client_socket.send(f"[SERVER] El cliente que intentas contactar no está conectado o no existe.\n".encode())
            return  
        dest_socket = nombre2socket[destinatario]
        dest_socket.send(f"[MENSAJE PRIVADO de {socket2nombre[nombre2socket[destinatario]]}]: {mensaje}\n".encode())

    elif comando.startswith(":u"):  # Comando para mostrar los nombres de usuarios conectados
        client_socket.send(f"[SERVER] Usuarios conectados: {list(nombre2socket.keys())}\n".encode())
    
    elif comando.startswith(":q"):  # Comando para desconectarse
        desconectar(client_socket)

    elif comando.startswith(":smile"): # Comando para carita feliz
        mensaje_para_todos(f"{socket2nombre[client_socket]}: :)".encode())

    elif comando.startswith(":angry"): # Comando para carita enojada
        mensaje_para_todos(f"{socket2nombre[client_socket]}: >:(".encode())

    elif comando.startswith(":combito"): # Comando para combito
        mensaje_para_todos(f"{socket2nombre[client_socket]}: Q(’- ’Q)".encode())

    elif comando.startswith(":larva"): # Comando para larva
        mensaje_para_todos(f"{socket2nombre[client_socket]}: (:o)OOOooo".encode())

    elif comando.startswith(":artefactos"): # Comando para mostrar los artefactos del cliente
        client_socket.send(f"[SERVER] Tus artefactos son: {', '.join(artefactosxcliente[client_socket])}\n".encode())

    elif comando.startswith(":artefacto"): # Comando para mostrar a que artefacto corresponde el número
        _, artefacto_id = comando.split(" ", 1)
        nombre_artefacto = artefactos_dict.get(artefacto_id, "Artefacto Desconocido")
        client_socket.send(f"[SERVER] Artefacto {artefacto_id}: {nombre_artefacto}\n".encode())

    elif comando.startswith(":offer"): # Comando para ofrecer intercambio
        _, destinatario, mi_artefacto, su_artefacto = comando.split(" ", 3)
        if destinatario in list(nombre2socket.keys()):
            if ((mi_artefacto in artefactosxcliente[client_socket]) and (su_artefacto in artefactosxcliente[nombre2socket[destinatario]])):
                client_socket.send("[SERVER] Se ha enviado la solicitud de intercambio, esperando respuesta...\n".encode())
                dest_socket = nombre2socket[destinatario]
                dest_socket.send(f"[OFERTA] {socket2nombre[client_socket]} quiere intercambiar {artefactos_dict[mi_artefacto]} por {artefactos_dict[su_artefacto]}. ¿Aceptas? Responde con :accept o :reject\n".encode())
                intercambiar_artefactos(client_socket, dest_socket, mi_artefacto, su_artefacto)
            else:
                client_socket.send("[SERVER] Uno de los artefactos que ingresaste no está disponible para intercambiar.\n".encode())
        else:
            client_socket.send("[SERVER] El cliente con el que intentas intercambiar no existe o no está conectado.\n".encode())

    elif comando.startswith(":accept"): # Comando para aceptar intercambio
        acepta[client_socket] = "acepta"

    elif comando.startswith(":reject"): # Comando para rechazar intercambio
        acepta[client_socket] = "rechaza"
    
    else:
        client_socket.send("[SERVER] Comando no reconocido. Inténtalo de nuevo.\n".encode())


# Función para manejar el intercambio de artefactos entre dos clientes
def intercambiar_artefactos(cliente_origen, cliente_destino, artefacto_origen, artefacto_destino):
    global acepta
    global artefactosxcliente

    while True:
        if acepta[cliente_destino] == "acepta":
            # Realizar el intercambio
            artefactosxcliente[cliente_origen].remove(artefacto_origen)
            artefactosxcliente[cliente_destino].remove(artefacto_destino)
            artefactosxcliente[cliente_origen].append(artefacto_destino)
            artefactosxcliente[cliente_destino].append(artefacto_origen)

            cliente_origen.send("[SERVER] ¡Intercambio realizado!\n".encode())
            cliente_destino.send("[SERVER] ¡Intercambio realizado!\n".encode())
            break
        elif acepta[cliente_destino] == "rechaza":
            cliente_origen.send("[SERVER] Intercambio denegado.\n".encode())
            cliente_destino.send("[SERVER] Intercambio denegado.\n".encode())
            break
    acepta[cliente_destino] = "noinfo"


# Función para notificar a todos los clientes
def mensaje_para_todos(mensaje):
    global clientes

    for cliente in clientes:
        try:
            cliente.send(mensaje)
        except:
            # En caso de error, desconectar al cliente y notificar a los demás
            desconectar(client_socket)

# Función para manejar la conexión de un nuevo cliente
def manejar_mensajes(client_socket, addr):
    global socket2nombre

    # Mensaje de bienvenida
    client_socket.send("¡Bienvenid@ al chat de Granjerxs!\n".encode())

    while True:
        # Obtener los nombres de los artefactos asociados a los números
        while True:
            client_socket.send("[SERVER] Cuéntame, ¿qué artefactos tienes?\n".encode())
            
             # Recibir la lista de números de artefactos
            artefactos_numeros = client_socket.recv(1024).decode().strip().split(',')
            if len(artefactos_numeros) > 6:
                client_socket.send("[SERVER] El máximo de artefactos por usuario es 6!\n".encode())
            if len(artefactos_numeros) == 0:
                client_socket.send("[SERVER] Es necesario que ingreses al menos 1 artefacto.\n".encode())  
            else:    
                artefactos_nombres = [artefactos_dict.get(artefacto, "Artefacto Desconocido") for artefacto in artefactos_numeros]
                break
        
        # Mostrar los nombres de los artefactos al cliente
        mensaje_arte = "[SERVER] Tus artefactos son: {}\n".format(", ".join(artefactos_nombres))
        client_socket.send(mensaje_arte.encode())

        # Confirmar con el cliente si la lista de artefactos es correcta
        client_socket.send("[SERVER] ¿Está bien? (Si/No)\n".encode())
        respuesta = client_socket.recv(1024).decode().strip().lower()

        if respuesta.lower() == "si":
            client_socket.send("[SERVER] ¡OK!\n".encode())
            artefactosxcliente[client_socket] = artefactos_numeros
            break
        else:
            client_socket.send("[SERVER] ¡Entendido! Comenzemos de nuevo.\n".encode())

    clientes.append(client_socket)

    # Notificar a los clientes existentes sobre la nueva conexión
    mensaje_para_todos(f"[SERVER] Cliente {socket2nombre[client_socket]} se ha conectado.\n".encode())

    while True:
        try:
            if client_socket in clientes:
                # Recibir mensajes del cliente
                mensaje = client_socket.recv(1024).decode().strip()
                if not mensaje:
                    break

                if mensaje.startswith(":"):
                    comandos(client_socket, mensaje)
                else:
                    # Notificar a todos los clientes sobre el mensaje (excepto al remitente)
                    mensaje_para_todos(f"{socket2nombre[client_socket]}: {mensaje}\n".encode())
        except:
            desconectar(client_socket)
            break

    clientes.append(client_socket)

# Crear un socket TCP
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Vincular el socket a una dirección y puerto
server_socket.bind((host, port))

server_socket.listen(5)
print("Servidor esperando conexiones...")

while True:
    client_socket, addr = server_socket.accept()
        
    client_name = client_socket.recv(1024).decode().strip()
    socket2nombre[client_socket] = client_name
    nombre2socket[client_name] = client_socket
    acepta[client_socket] = "noinfo"

    cliente_thread = threading.Thread(target = manejar_mensajes, args=(client_socket, addr))
    cliente_thread.start()