import cv2
import speech_recognition as sr
import time
import threading
import tkinter as tk
from tkinter import messagebox

# Inicializa el reconocimiento de voz
recognizer = sr.Recognizer()
command_received = False  # Bandera para saber si se ha recibido un comando
stop_listening = None  # Controla la escucha continua

# Función para escuchar el comando de voz
def escuchar_comando(label_status):
    global command_received
    with sr.Microphone() as source:
        label_status.config(text="Di 'foto' para capturar la imagen...")  # Actualiza el mensaje en la interfaz
        try:
            audio = recognizer.listen(source)
            comando = recognizer.recognize_google(audio, language="es-ES")
            if "foto" in comando.lower():
                label_status.config(text="¡Comando 'foto' detectado! Procesando...")  # Actualiza el mensaje en la interfaz
                command_received = True  # Se ha recibido un comando
            else:
                label_status.config(text="Comando no reconocido. Inténtalo de nuevo.")
        except sr.UnknownValueError:
            label_status.config(text="No entendí el comando. Inténtalo de nuevo.")
        except sr.RequestError as e:
            label_status.config(text=f"Error de solicitud; {e}")

# Carga el clasificador para detección de sonrisas
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
smile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_smile.xml')

# Captura desde la webcam
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Función para capturar selfie
def tomar_selfie(frame):
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    filename = f"selfie_{timestamp}.jpg"
    cv2.imwrite(filename, frame)
    messagebox.showinfo("Selfie Tomada", f"Selfie guardada como {filename}")

# Función para iniciar el reconocimiento de voz en segundo plano
def iniciar_escucha(label_status):
    def reconocimiento_continuo():
        while True:
            escuchar_comando(label_status)
    threading.Thread(target=reconocimiento_continuo, daemon=True).start()

# Bucle principal para la captura de video
def main_loop(label_status):
    global command_received
    while True:
        ret, frame = cap.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        smile_detected = False  # Variable para saber si se detecta una sonrisa

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
            roi_gray = gray[y:y+h, x:x+w]
            roi_color = frame[y:y+h, x:x+w]
            smiles = smile_cascade.detectMultiScale(roi_gray, 1.8, 20)

            if len(smiles) > 0:
                smile_detected = True  # Se detectó una sonrisa
                for (sx, sy, sw, sh) in smiles:
                    cv2.rectangle(roi_color, (sx, sy), (sx+sw, sy+sh), (0, 255, 0), 2)
                    break  # Detiene el bucle después de dibujar la sonrisa

        # Solo toma la selfie si se ha detectado una sonrisa y se ha recibido un comando
        if smile_detected and command_received:
            tomar_selfie(frame)  # Toma la selfie
            label_status.config(text="¡Sonrisa detectada! Capturando selfie...")  # Actualiza el mensaje
            command_received = False  # Reinicia la bandera de comando

        cv2.imshow('Detector de Sonrisas', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# Crear la ventana principal
root = tk.Tk()
root.title("Detector de Sonrisas")

# Etiqueta para mostrar mensajes al usuario
label_status = tk.Label(root, text="Presiona 'Iniciar Reconocimiento' para comenzar", font=("Arial", 14))
label_status.pack(pady=20)

# Crear un botón para iniciar el sistema
iniciar_button = tk.Button(root, text="Iniciar Reconocimiento", command=lambda: iniciar_escucha(label_status))
iniciar_button.pack(pady=20)

# Bucle para actualizar continuamente el video
def actualizar_video():
    main_loop(label_status)

# Iniciar el bucle de la interfaz gráfica
root.after(10, actualizar_video)
root.mainloop()
