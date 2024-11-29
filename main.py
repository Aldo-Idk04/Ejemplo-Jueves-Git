import tkinter as tk
from PIL import Image, ImageTk
import cv2
import numpy as np
from tkinter import messagebox
import os
import pyzbar.pyzbar as pyzbar
import qrcode
from tkinter import filedialog

class QRScannerApp:
    def __init__(self, master):
        self.master = master
        master.title("QR Scanner")
        master.geometry("800x600")

        self.scan_button = tk.Button(master, text="Escanear QR", command=self.start_scan)
        self.scan_button.pack(pady=20)

        self.info_button = tk.Button(master, text="Ver Información", state="disabled")
        self.info_button.pack(pady=20)

        self.detected_label = tk.Label(master, text="", wraplength=700, justify=tk.LEFT)
        self.detected_label.pack(pady=20)

        self.video_frame = tk.Frame(master)
        self.video_frame.pack(fill=tk.BOTH, expand=True)

        self.video_label = tk.Label(self.video_frame)
        self.video_label.pack(fill=tk.BOTH, expand=True)

        self.register_button = tk.Button(master, text="Registrar", command=self.open_registration_window)
        self.register_button.pack(pady=20)

        # Agregar botón para cargar QR desde archivo
        self.load_qr_button = tk.Button(master, text="Cargar QR desde archivo", command=self.load_qr_from_file)
        self.load_qr_button.pack(pady=20)
        master.after(100, self.update_info_button_state)

    def start_scan(self):
        self.scan_button.config(state="disabled")
        self.info_button.config(state="normal")
        self.open_camera()

    def open_camera(self):
        self.camera_window = tk.Toplevel(self.master)
        self.camera_window.title("Cámara")
        self.camera_window.geometry("640x480")

        self.cap = cv2.VideoCapture(0)
        
        self.video_label = tk.Label(self.camera_window)
        self.video_label.pack(fill=tk.BOTH, expand=True)

        self.update_camera()

    def update_camera(self):
        ret, frame = self.cap.read()
        
        if ret:
            cv2_im = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(cv2_im)
            photo = ImageTk.PhotoImage(img)
            
            self.video_label.config(image=photo)
            self.video_label.image = photo
            
            self.master.after(10, self.update_camera)

    def detect_qr(self):
        ret, frame = self.cap.read()
    
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
        for contour in contours:
            area = cv2.contourArea(contour)
            x, y, w, h = cv2.boundingRect(contour)
        
            if area > frame.shape[0] * frame.shape[1] // 4:
                roi = frame[y:y+h, x:x+w]
            
                gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
                blur = cv2.GaussianBlur(gray_roi, (5, 5), 0)
                _, thresh_otsu = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
                qr_code = cv2.QRCodeDetector().detectAndDecodeSingle(thresh_otsu)
            
                if qr_code[0]:
                    data = qr_code[0][0].decode("utf-8")
                
                    print(f"Datos completos: {data}")  # Imprime los datos completos para verificación
                
                    # Extraer información del código QR
                    nombre, edad, oficio, genero = self.parse_qr_data(data)
                
                    print(f"Nombre: {nombre}")
                    print(f"Edad: {edad}")
                    print(f"Oficio: {oficio}")
                    print(f"Género: {genero}")  # Imprime cada campo individual
                
                    info = f"Información extraída:\n"
                    info += f"Nombre: {nombre}\n"
                    info += f"Edad: {edad}\n"
                    info += f"Oficio: {oficio}\n"
                    info += f"Género: {genero}"
                
                    self.detected_label.config(text=info)
                
                    # Cerrar la ventana de cámara
                    self.cap.release()
                    self.camera_window.destroy()
                
                    # Habilitar el botón de información
                    self.info_button.config(state="normal")
                
                    # Mostrar mensaje de éxito
                    messagebox.showinfo("Éxito", f"Información registrada con éxito.")
                
                    break
    
    def __init__(self, master):
        self.master = master
        master.title("QR Scanner")
        master.geometry("800x600")

        self.scan_button = tk.Button(master, text="Escanear QR", command=self.start_scan)
        self.scan_button.pack(pady=20)

        self.info_button = tk.Button(master, text="Ver Información", state="disabled", command=self.show_info)
        self.info_button.pack(pady=20)

        self.detected_label = tk.Label(master, text="", wraplength=700, justify=tk.LEFT)
        self.detected_label.pack(pady=20)

        self.video_frame = tk.Frame(master)
        self.video_frame.pack(fill=tk.BOTH, expand=True)

        self.video_label = tk.Label(self.video_frame)
        self.video_label.pack(fill=tk.BOTH, expand=True)

        self.register_button = tk.Button(master, text="Registrar", command=self.open_registration_window)
        self.register_button.pack(pady=20)

        self.load_qr_button = tk.Button(master, text="Cargar QR desde archivo", command=self.load_qr_from_file)
        self.load_qr_button.pack(pady=20)

        self.info = ""

    def start_scan(self):
        self.scan_button.config(state="disabled")
        self.info_button.config(state="normal")
        self.open_camera()

    def open_camera(self):
        self.camera_window = tk.Toplevel(self.master)
        self.camera_window.title("Cámara")
        self.camera_window.geometry("640x480")

        self.cap = cv2.VideoCapture(0)
        
        self.video_label = tk.Label(self.camera_window)
        self.video_label.pack(fill=tk.BOTH, expand=True)

        self.update_camera()

    def update_camera(self):
        ret, frame = self.cap.read()
        
        if ret:
            cv2_im = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(cv2_im)
            photo = ImageTk.PhotoImage(img)
            
            self.video_label.config(image=photo)
            self.video_label.image = photo
            
            self.master.after(10, self.update_camera)

            self.detect_qr(frame)

    def detect_qr(self):
        ret, frame = self.cap.read()
    
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
        for contour in contours:
            area = cv2.contourArea(contour)
            x, y, w, h = cv2.boundingRect(contour)
        
            if area > frame.shape[0] * frame.shape[1] // 4:
                roi = frame[y:y+h, x:x+w]
            
                gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
                blur = cv2.GaussianBlur(gray_roi, (5, 5), 0)
                _, thresh_otsu = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
                qr_code = cv2.QRCodeDetector().detectAndDecodeSingle(thresh_otsu)
            
                if qr_code[0]:
                    data = qr_code[0][0].decode("utf-8")
                
                    print(f"Datos completos: {data}")  # Imprime los datos completos para verificación
                
                    # Extraer información del código QR
                    nombre, edad, oficio, genero = self.parse_qr_data(data)
                
                    print(f"Nombre: {nombre}")
                    print(f"Edad: {edad}")
                    print(f"Oficio: {oficio}")
                    print(f"Género: {genero}")  # Imprime cada campo individual
                
                    self.info = f"Información extraída:\n"
                    self.info += f"Nombre: {nombre}\n"
                    self.info += f"Edad: {edad}\n"
                    self.info += f"Oficio: {oficio}\n"
                    self.info += f"Género: {genero}"
                
                    self.detected_label.config(text=self.info)
                
                    # Cerrar la ventana de cámara
                    self.cap.release()
                    self.camera_window.destroy()
                
                    # Habilitar el botón de información
                    self.info_button.config(state="normal")
                
                    # Mostrar mensaje de éxito
                    messagebox.showinfo("Éxito", f"Información registrada con éxito.")
                
                    break
    
        if not qr_code[0]:
            self.master.after(50, lambda: self.detect_qr())


    def show_info(self):
        messagebox.showinfo("Información", self.info)

    def open_registration_window(self):
        self.registration_window = tk.Toplevel(self.master)
        self.registration_window.title("Registro")
        self.registration_window.geometry("400x300")

        tk.Label(self.registration_window, text="Nombre").grid(row=0, column=0, sticky=tk.E)
        self.name_entry = tk.Entry(self.registration_window)
        self.name_entry.grid(row=0, column=1)

        tk.Label(self.registration_window, text="Edad").grid(row=1, column=0, sticky=tk.E)
        self.age_entry = tk.Entry(self.registration_window)
        self.age_entry.grid(row=1, column=1)

        tk.Label(self.registration_window, text="Oficio").grid(row=2, column=0, sticky=tk.E)
        self.job_entry = tk.Entry(self.registration_window)
        self.job_entry.grid(row=2, column=1)

        tk.Label(self.registration_window, text="Género").grid(row=3, column=0, sticky=tk.E)
        self.gender_entry = tk.Entry(self.registration_window)
        self.gender_entry.grid(row=3, column=1)

        tk.Button(self.registration_window, text="Registrar", command=self.register_data).grid(row=4, column=1)

        tk.Button(self.registration_window, text="Volver", command=self.registration_window.destroy).grid(row=4, column=0)

    def register_data(self):
        nombre = self.name_entry.get()
        edad = self.age_entry.get()
        oficio = self.job_entry.get()
        genero = self.gender_entry.get()

        # Generar código QR con la información registrada
        qr_code = qrcode.QRCode(
            version=1,
            box_size=10,
            border=5
        )
        qr_code.add_data(f"Nombre: {nombre}, Edad: {edad}, Oficio: {oficio}, Género: {genero}")
        qr_code.make(fit=True)
        
        img = qr_code.make_image(fill_color="black", back_color="white")
        img.save("registered_info.png")

        # Cerrar la ventana de registro
        self.registration_window.destroy()

    def parse_qr_data(self, data):
        parts = data.split(',')
        return parts[0][7:].strip(), parts[1][7:].strip(), parts[2][7:].strip(), parts[3][7:].strip()

    def load_qr_from_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", ".png")])
        if not file_path:
            messagebox.showinfo("Error", "No se seleccionó ninguna imagen.")
            return

        # Mostrar mensaje de que el archivo se recibió
        messagebox.showinfo("Éxito", f"Archivo recibido: {os.path.basename(file_path)}")

        # Leer el QR del archivo
        qr_code = pyzbar.decode(Image.open(file_path))

        if qr_code:
            data = qr_code[0].data.decode('utf-8')
        
            print(f"Datos completos: {data}")  # Imprime los datos completos para verificación
        
            # Extraer información del código QR
            nombre, edad, oficio, genero = self.parse_qr_data(data)
        
            print(f"Nombre: {nombre}")
            print(f"Edad: {edad}")
            print(f"Oficio: {oficio}")
            print(f"Género: {genero}")  # Imprime cada campo individual
        
            self.info = f"Información extraída:\n"
            self.info += f"Nombre: {nombre}\n"
            self.info += f"Edad: {edad}\n"
            self.info += f"Oficio: {oficio}\n"
            self.info += f"Género: {genero}"
        
            # No actualizamos la etiqueta detected_label aquí
        else:
            messagebox.showerror("Error", "No se pudo leer el código QR.")

    def open_registration_window(self):
        self.registration_window = tk.Toplevel(self.master)
        self.registration_window.title("Registro")
        self.registration_window.geometry("400x300")

        tk.Label(self.registration_window, text="Nombre").grid(row=0, column=0, sticky=tk.E)
        self.name_entry = tk.Entry(self.registration_window)
        self.name_entry.grid(row=0, column=1)

        tk.Label(self.registration_window, text="Edad").grid(row=1, column=0, sticky=tk.E)
        self.age_entry = tk.Entry(self.registration_window)
        self.age_entry.grid(row=1, column=1)

        tk.Label(self.registration_window, text="Oficio").grid(row=2, column=0, sticky=tk.E)
        self.job_entry = tk.Entry(self.registration_window)
        self.job_entry.grid(row=2, column=1)

        tk.Label(self.registration_window, text="Género").grid(row=3, column=0, sticky=tk.E)
        self.gender_entry = tk.Entry(self.registration_window)
        self.gender_entry.grid(row=3, column=1)

        tk.Button(self.registration_window, text="Registrar", command=self.register_data).grid(row=4, column=1)

        tk.Button(self.registration_window, text="Volver", command=self.registration_window.destroy).grid(row=4, column=0)

    def register_data(self):
        nombre = self.name_entry.get()
        edad = self.age_entry.get()
        oficio = self.job_entry.get()
        genero = self.gender_entry.get()

        # Generar código QR con la información registrada
        qr_code = qrcode.QRCode(
            version=1,
            box_size=10,
            border=5
        )
        qr_code.add_data(f"Nombre: {nombre}, Edad: {edad}, Oficio: {oficio}, Género: {genero}")
        qr_code.make(fit=True)
        
        img = qr_code.make_image(fill_color="black", back_color="white")
        img.save("registered_info.png")

        # Cerrar la ventana de registro
        self.registration_window.destroy()

    def parse_qr_data(self, data):
        parts = data.split(',')
        nombre = parts[0].split(':')[1].strip()
        edad = parts[1].split(':')[1].strip()
        oficio = parts[2].split(':')[1].strip()
        genero = parts[3].split(':')[1].strip()
    
        return nombre, edad, oficio, genero

    def load_qr_from_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", ".png")])
        if not file_path:
            messagebox.showinfo("Error", "No se seleccionó ninguna imagen.")
            return

        # Mostrar mensaje de que el archivo se recibió
        messagebox.showinfo("Éxito", f"Archivo recibido: {os.path.basename(file_path)}")

        # Leer el QR del archivo
        qr_code = pyzbar.decode(Image.open(file_path))

        if qr_code:
            data = qr_code[0].data.decode('utf-8')
        
            print(f"Datos completos: {data}")  # Imprime los datos completos para verificación
        
            # Extraer información del código QR
            nombre, edad, oficio, genero = self.parse_qr_data(data)
        
            print(f"Nombre: {nombre}")
            print(f"Edad: {edad}")
            print(f"Oficio: {oficio}")
            print(f"Género: {genero}")  # Imprime cada campo individual
        
            info = f"Información extraída:\n"
            info += f"Nombre: {nombre}\n"
            info += f"Edad: {edad}\n"
            info += f"Oficio: {oficio}\n"
            info += f"Género: {genero}"
        
            self.info = info
        else:
            messagebox.showerror("Error", "No se pudo leer el código QR.")

    def update_info_button_state(self):
        if self.info_button['state'] == 'normal':
            self.info_button['state'] = 'disabled'
        elif self.info_button['state'] == 'disabled':
            self.info_button['state'] = 'normal'

if __name__ == "__main__":
    root = tk.Tk()
    app = QRScannerApp(root)
    root.mainloop()
