import socket
import threading
import json

# Archivo JSON con la asociación de artefactos
ARTEFACTOS_FILE = 'artefactos.json'

# Cargar artefactos desde el archivo JSON
with open(ARTEFACTOS_FILE) as f:
    artefactos_data = json.load(f)

# Estructura de datos para manejar los artefactos de los usuarios
usuarios_artefactos = {}

# Función para manejar la conexión de un cliente
def manejar_cliente(client_socket, client_address):
    # Obtener el nombre del cliente
    nombre_cliente = client_socket.recv(1024).decode('utf-8')
    print(f"[SERVER] Cliente {nombre_cliente} conectado desde {client_address}")

    # Enviar mensaje de bienvenida al cliente
    client_socket.send("[SERVER] ¡Bienvenid@ al chat de Granjerxs!".encode('utf-8'))

    # Preguntar por los artefactos que tiene el usuario
    client_socket.send("[SERVER] Cuéntame, ¿qué artefactos tienes?".encode('utf-8'))
    artefactos_str = client_socket.recv(1024).decode('utf-8')
    artefactos_ids = [int(artefacto_id) for artefacto_id in artefactos_str.split(',')]
    usuario_artefactos = [artefactos_data[str(artefacto_id)] for artefacto_id in artefactos_ids]
    usuarios_artefactos[nombre_cliente] = usuario_artefactos

    # Mostrar los artefactos al usuario
    client_socket.send(f"[SERVER] Tus artefactos son: {', '.join(usuario_artefactos)}\n¿Está bien? (Sí/No)".encode('utf-8'))
    respuesta = client_socket.recv(1024).decode('utf-8')
    if respuesta.lower() != 'sí':
        client_socket.send("[SERVER] Artefactos no aceptados. Desconectando...".encode('utf-8'))
        client_socket.close()
        return

    # Confirmar artefactos aceptados
    client_socket.send("[SERVER] ¡OK!".encode('utf-8'))


    try:
        while True:
            # Recibir mensaje del cliente
            mensaje = client_socket.recv(1024).decode('utf-8')
            if not mensaje:
                break

            # Procesar comandos del cliente
            if mensaje.startswith('q'):
                # Comando para desconectarse
                print(f"[SERVER] Cliente {nombre_cliente} desconectado.")
                break
            elif mensaje.startswith('p'):
                # Comando para mensaje privado
                partes = mensaje.split(' ', 2)
                destinatario = partes[1]
                mensaje_privado = partes[2]
                # Implementar envío de mensaje privado a destinatario
                # Verificar que el destinatario exista
                if destinatario in usuarios_artefactos:
                    destinatario_socket = next((sock for sock, nombre in clientes if nombre == destinatario), None)

                    if destinatario_socket:
                        # Enviar mensaje privado al destinatario
                        destinatario_socket.send(
                            f"[Mensaje privado de {nombre_cliente}] {mensaje_privado}".encode('utf-8'))
                        client_socket.send("[SERVER] Mensaje privado enviado correctamente.".encode('utf-8'))
                    else:
                        client_socket.send("[SERVER] El destinatario no está conectado.".encode('utf-8'))
                else:
                    client_socket.send("[SERVER] El destinatario no existe.".encode('utf-8'))
            # (El resto de comandos se mantiene igual)
            elif mensaje.startswith('u'):
                # Comando para mostrar usuarios conectados
                usuarios_conectados = list(usuarios_artefactos.keys())
                respuesta = f"[SERVER] Usuarios conectados: {', '.join(usuarios_conectados)}"
                client_socket.send(respuesta.encode('utf-8'))
            elif mensaje.startswith("smile"):
                print("adada")
            elif mensaje.startswith('artefactos'):
                # Comando para mostrar artefactos propios
                artefactos_usuario = usuarios_artefactos[nombre_cliente]
                respuesta = f"[SERVER] Tus artefactos: {', '.join(artefactos_usuario)}"
                client_socket.send(respuesta.encode('utf-8'))
            # Implementar el resto de comandos según el enunciado

    except Exception as e:
        print(f"Error en la conexión con {nombre_cliente}: {str(e)}")
    finally:
        # Eliminar usuario de la lista y cerrar conexión
        del usuarios_artefactos[nombre_cliente]
        print(f"[SERVER] Cliente {nombre_cliente} desconectado.")
        client_socket.close()

# Configuración del servidor
HOST = '192.168.1.15'
PORT = 80

# Crear socket del servidor
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(3)  # Permitir hasta 3 conexiones

print("[SERVER] Esperando conexiones...")
# Lista para almacenar clientes y sus nombres asociados
clientes = []
try:
    while True:
        # Esperar conexión de un cliente
        client_socket, client_address = server_socket.accept()
        # Obtener el nombre del cliente
        nombre_cliente = client_socket.recv(1024).decode('utf-8')
        # Agregar cliente y su nombre a la lista
        clientes.append((client_socket, nombre_cliente))
        print(f"[SERVER] Cliente {nombre_cliente} conectado desde {client_address}")
        # Crear un nuevo thread para manejar al cliente
        client_thread = threading.Thread(target=manejar_cliente, args=(client_socket, client_address))
        client_thread.start()

except KeyboardInterrupt:
    print("\n[SERVER] Servidor cerrado.")
finally:
    server_socket.close()