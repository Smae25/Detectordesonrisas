import time
import threading
import tkinter as tk
from tkinter import messagebox
import cv2
import speech_recognition as sr


# Inicializa el reconocimiento de voz
recognizer = sr.Recognizer()
command_received = False  # Bandera para saber si se ha recibido un comando

# Función para escuchar el comando de voz
def escuchar_comando():
    """
    Escucha comandos de voz 
    y los procesa utilizando la biblioteca speech_recognition.
    Utiliza la variable global command_received 
    para indicar si se ha recibido un comando.
    """
    global command_received

    with sr.Microphone() as source:
        print("Di 'foto' para capturar la imagen")
        audio = recognizer.listen(source)

        try:
            comando = recognizer.recognize_google(audio, language="es-ES")
            print(f"Escuché: {comando}")
            if "foto" in comando.lower():
                command_received = True  # Se ha recibido un comando
        except sr.UnknownValueError:
            print("No entendí el comando.")
        except sr.RequestError as e:
            print(f"No se pudo solicitar resultados; {e}")

# Carga el clasificador para detección de sonrisas
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
smile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_smile.xml')

# Captura desde la webcam
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Función para capturar selfie
def tomar_selfie(frame):
    """
    Toma una selfie utilizando el frame actual
    y la guarda en un archivo con un nombre único basado en la fecha y hora actuales.
    Parámetros:
    frame: El frame actual de la webcam que se utilizará para tomar la selfie.
    """
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    filename = f"selfie_{timestamp}.jpg"
    cv2.imwrite(filename, frame)
    print(f"Selfie guardada como {filename}")
    messagebox.showinfo("Selfie Tomada", f"Selfie guardada como {filename}")

# Hilo para escuchar el comando de voz
def comando_de_voz():
    """
    Bucle infinito que escucha comandos de voz
     y los procesa utilizando la función escuchar_comando.
    """
    while True:
        escuchar_comando()

# Función para iniciar el video y el reconocimiento de voz
def iniciar():
    """
    Inicia el reconocimiento de voz y el bucle principal del programa 
    que detecta caras y sonrisas en la webcam y toma selfies cuando se detecta una sonrisa 
    y se ha recibido un comando de voz.
    """
    threading.Thread(target=comando_de_voz, daemon=True).start()
    main_loop()

# Bucle principal para la captura de video
def main_loop():
    """
    Bucle principal del programa 
    que detecta caras y sonrisas en la webcam y toma
    selfies cuando se detecta una sonrisa y se ha recibido un comando de voz. 
    """
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
            command_received = False  # Reinicia la bandera de comando

        cv2.imshow('Detector de Sonrisas', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# Crear la ventana principal
root = tk.Tk()
root.title("Detector de Sonrisas")

# Crear un botón para iniciar el sistema
iniciar_button = tk.Button(
    root,
    text="Presiona 'Iniciar Reconocimiento' para comenzar",
    command=iniciar)
iniciar_button.pack(pady=20)

# Iniciar el bucle de la interfaz gráfica
root.mainloop()