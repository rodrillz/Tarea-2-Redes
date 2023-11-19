import socket
import threading
import json

host = '127.0.0.1'
port = 12345
# Lista de clientes conectados
clientes = []
nombres_clientes = {}
sockets = {} 


with open('artefactos.json', 'r') as f:
    artefactos_dict = json.load(f)

# Diccionario para almacenar los artefactos de cada cliente
artefactos_clientes = {}

def comandos(cliente_socket, comando, addr):
    global clientes
    global nombres_clientes
    global sockets

    if comando.startswith(f":p"):    # Comando para mensaje privado
        _, destinatario, mensaje = comando.split(" ", 2)
        destinatario_socket = sockets[destinatario]
        destinatario_socket.send(f"[MENSAJE PRIVADO de {nombres_clientes[sockets[destinatario]]}]: {mensaje}\n".encode())

    elif comando.startswith(":u"):  # Comando para mostrar los identificadores de usuarios conectados
        lista_usuarios = [str(clientes.index(cliente)) for cliente in clientes]
        cliente_socket.send(f"[SERVER] Usuarios conectados: {', '.join(lista_usuarios)}\n".encode())

    elif comando.startswith(":smile"): # Comando para carita feliz
        mensaje_para_todos(f"{nombres_clientes[addr]}: :)".encode())

    elif comando.startswith(":angry"): # Comando para carita enojada
        mensaje_para_todos(f"{nombres_clientes[addr]}: >:(".encode())

    elif comando.startswith(":combito"): # Comando para combito
        mensaje_para_todos(f"{nombres_clientes[addr]}: Q(’- ’Q)".encode())

    elif comando.startswith(":larva"): # Comando para larva
        mensaje_para_todos(f"{nombres_clientes[addr]}: (:o)OOOooo".encode())

    elif comando.startswith(":artefactos"): # Comando para mostrar los artefactos del cliente
        cliente_socket.send(f"[SERVER] Tus artefactos son: {', '.join(artefactos_clientes[cliente_socket])}\n".encode())

    elif comando.startswith(":artefacto"): # Comando para mostrar a que artefacto corresponde el número
        _, artefacto_id = comando.split(" ", 1)
        nombre_artefacto = artefactos_dict.get(artefacto_id, "Artefacto Desconocido")
        cliente_socket.send(f"[SERVER] Artefacto {artefacto_id}: {nombre_artefacto}\n".encode())

    elif comando.startswith(":offer"): # Comando para ofrecer intercambio
        _, destinatario, mi_artefacto, su_artefacto = comando.split(" ", 3)
        destinatario_socket = clientes[int(destinatario)]
        destinatario_socket.send(f"[OFERTA] {addr} quiere intercambiar {artefactos_dict[mi_artefacto]} por {artefactos_dict[su_artefacto]}. ¿Aceptas? Responde con :accept o :reject\n".encode())

    elif comando.startswith(":accept"): # Comando para aceptar intercambio
        # Implementar
        pass

    elif comando.startswith(":reject"): # Comando para rechazar intercambio
        # Implementar
        pass
    
    else:
        cliente_socket.send("[SERVER] Comando no reconocido. Inténtalo de nuevo.\n".encode())


# Función para manejar el intercambio de artefactos entre dos clientes
def intercambiar_artefactos(cliente_origen, cliente_destino, artefacto_origen, artefacto_destino):
    if (
        artefacto_origen in artefactos_clientes[cliente_origen] and
        artefacto_destino in artefactos_clientes[cliente_destino]
    ):
        # Realizar el intercambio
        artefactos_clientes[cliente_origen].remove(artefacto_origen)
        artefactos_clientes[cliente_destino].remove(artefacto_destino)
        artefactos_clientes[cliente_origen].append(artefacto_destino)
        artefactos_clientes[cliente_destino].append(artefacto_origen)

        return True
    else:
        return False

# Función para notificar a todos los clientes excepto al remitente
def mensaje_para_todos(mensaje):
    global clientes
    for cliente in clientes:
        try:
            cliente.send(mensaje)
        except:
            # En caso de error, desconectar al cliente y notificar a los demás
            clientes.remove(cliente)
            cliente.close()

# Función para manejar la conexión de un nuevo cliente
def manejar_mensajes(client_socket, addr):
    global nombres_clientes

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
            break
        else:
            client_socket.send("[SERVER] ¡Entendido! Comenzemos de nuevo.\n".encode())

    clientes.append(client_socket)

    # Notificar a los clientes existentes sobre la nueva conexión
    mensaje_para_todos(f"[SERVER] Cliente {nombres_clientes[addr]} se ha conectado.\n".encode())

    while True:
        try:
            # Recibir mensajes del cliente
            mensaje = client_socket.recv(1024).decode().strip()
            if not mensaje:
                break

            if mensaje.startswith(":"):
                comandos(client_socket, mensaje, addr)
            else:
                # Notificar a todos los clientes sobre el mensaje (excepto al remitente)
                mensaje_para_todos(f"{nombres_clientes[addr]}: {mensaje}\n".encode())
        except:
            # En caso de error, desconectar al cliente y notificar a los demás
            clientes.remove(client_socket)
            del nombres_clientes[addr]
            client_socket.close()
            addr = str(addr)
            mensaje_para_todos(f"[SERVER] Cliente {nombres_clientes[addr]} se ha desconectado.\n".encode())
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
    nombres_clientes[client_socket] = client_name
    sockets[client_name] = client_socket

    cliente_thread = threading.Thread(target = manejar_mensajes, args=(client_socket, addr))
    cliente_thread.start()