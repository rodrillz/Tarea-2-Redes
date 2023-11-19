import socket
import threading

host = '127.0.0.1'
port = 12345
client_name = "Hardcorito"

# Función para manejar la recepción de mensajes del servidor
def recibir_mensajes(client_socket):
    while True:
        try:
            mensaje = client_socket.recv(1024).decode()
            print(mensaje)
        except:
            # En caso de error, cerrar la conexión y salir
            print("¡Error al recibir mensajes!")
            client_socket.close()
            break

# Crear un socket para el cliente
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Conectar al servidor
client_socket.connect((host, port))

# Enviar username al server
client_socket.send(client_name.encode())

# Manejar el mensaje de bienvenida
mensaje_bienvenida = client_socket.recv(1024).decode()
print(mensaje_bienvenida)

# Iniciar un hilo para manejar la recepción de mensajes del servidor
hilo_recepcion = threading.Thread(target=recibir_mensajes, args=(client_socket,))
hilo_recepcion.start()

# Obtener la lista de artefactos del usuario
artefactos_input = input()
# Enviar la lista de artefactos al servidor
client_socket.send(artefactos_input.encode())

# Recibir y mostrar la respuesta del servidor
respuesta_servidor = client_socket.recv(1024).decode()
print(respuesta_servidor)

# Enviar mensajes al servidor
while True:
    mensaje = input()
    client_socket.send(mensaje.encode())