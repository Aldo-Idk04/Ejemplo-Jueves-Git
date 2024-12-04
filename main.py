import tkinter as tk
from tkinter import ttk  # Importamos ttk
from PIL import Image, ImageTk
import cv2
import numpy as np
from tkinter import messagebox
import os
import glob
import pyzbar.pyzbar as pyzbar
import qrcode
from tkinter import filedialog
import json
from datetime import date

def save_qr_info(info):
    today = date.today()
    year_folder = str(today.year)
    month_folder = today.strftime("%m")
    day_file = today.strftime("%d") + ".json"

    # Obtener el directorio del script actual
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Construir el path completo para el archivo JSON
    full_path = os.path.join(script_dir, "Fechas", year_folder, month_folder, day_file)

    print(f"Intentando guardar en: {full_path}")  # Línea de depuración

    # Crear las carpetas si no existen
    try:
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
    except PermissionError:
        directory = filedialog.askdirectory(title="Seleccione un directorio para guardar")
        if directory:
            base_path = directory

    # Verificar si el archivo existe y leer su contenido
    try:
        with open(full_path, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        # Si no existe el archivo, crear una lista vacía
        data = []

    # Agregar la nueva información al archivo
    data.append({"info": info})

    # Guardar la información actualizada
    try:
        with open(full_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        messagebox.showinfo("Éxito", f"Información guardada en {full_path}")
        print(f"Archivo creado: {full_path}")  # Imprime un mensaje de confirmación
    except PermissionError:
        messagebox.showerror("Error", "No tienes permisos para escribir en este directorio.")
        print(f"No se pudo crear el archivo en {full_path}")  # Línea de depuración

class QRScannerApp:
    def __init__(self, master):
        self.master = master
        master.title("QR Scanner")
        master.geometry("800x600")

        self.scan_button = tk.Button(master, text="Escanear QR", command=self.start_scan)
        self.scan_button.pack(pady=20)

        self.info_button = tk.Button(master, text="Ver Información", command=self.show_information_menu)
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
        self.cap = None
        self.date_data = {}
    
    def show_years(self, menu_window):
        years_folder = os.path.join("Fechas")
        
        if not os.path.exists(years_folder):
            messagebox.showerror("Error", "No se encontraron registros.")
            return

        # Buscar todos los años disponibles
        years = set()
        for path in glob.glob(os.path.join(years_folder, "**"), recursive=True):
            if os.path.isdir(path):
                relative_path = os.path.relpath(path, years_folder)
                if relative_path != ".":
                    years.add(relative_path.split(os.sep)[0])

        if not years:
            messagebox.showerror("Error", "No se encontraron años registrados.")
            return

        # Mostrar años disponibles
        tk.Label(menu_window, text="Años Disponibles:", font=("Arial", 12, "bold")).pack(pady=10)
        for year in sorted(years):
            year_button = tk.Button(menu_window, text=year, command=lambda y=year: self.show_year_details(y))
            year_button.pack(pady=5)
    
    def show_information_menu(self):
        menu_window = tk.Toplevel(self.master)
        menu_window.title("Menú de Consulta")

        years_folder = os.path.join("Fechas")
    
        if not os.path.exists(years_folder):
            messagebox.showerror("Error", "No se encontraron registros.")
            return

        # Buscar todos los años disponibles
        years = set()
        for path in glob.glob(os.path.join(years_folder, "**"), recursive=True):
            if os.path.isdir(path):
                relative_path = os.path.relpath(path, years_folder)
                if relative_path != ".":
                    years.add(relative_path.split(os.sep)[0])

        if not years:
            messagebox.showerror("Error", "No se encontraron años registrados.")
            return

        # Mostrar años disponibles
        tk.Label(menu_window, text="Años Disponibles:", font=("Arial", 12, "bold")).pack(pady=10)
        for year in sorted(years):
            year_button = tk.Button(menu_window, text=year, command=lambda y=year: self.show_year_details(y))
            year_button.pack(pady=5)

    def show_year_details(self, year):
        menu_window = tk.Toplevel(self.master)
        menu_window.title(f"Detalles del año {year}")

        months_folder = os.path.join("Fechas", year)
        months = set()
        for path in glob.glob(os.path.join(months_folder, "**"), recursive=True):
            if os.path.isdir(path):
                relative_path = os.path.relpath(path, months_folder)
                if relative_path != ".":
                    months.add(relative_path.split(os.sep)[0])

        if not months:
            messagebox.showerror("Error", f"No se encontraron meses registrados para {year}.")
            return

        # Mostrar resumen por mes
        for month in sorted(months):
            month_frame = tk.Frame(menu_window)
            month_frame.pack(fill=tk.X, pady=10)

            # Etiqueta con el mes
            tk.Label(month_frame, text=f"{month}", font=("Arial", 10, "bold")).pack(side=tk.TOP)

            days_folder = os.path.join(months_folder, month)
            days = [f for f in os.listdir(days_folder) if f.endswith(".json")]

            if not days:
                messagebox.showerror("Error", f"No se encontraron días registrados para {month} de {year}.")
                continue

            # Mostrar botones para cada día
            day_buttons_frame = tk.Frame(month_frame)
            day_buttons_frame.pack()

            for day_file in days:
                day_button = tk.Button(day_buttons_frame, text=day_file[:-5], command=lambda d=os.path.join(year, month, day_file): self.show_day_details(d))
                day_button.pack(side=tk.LEFT, padx=5)

    def show_day_details(self, dia_cadena):
        # Construye el path de la carpeta del mes
        month_folder = os.path.join("Fechas", dia_cadena[:4], dia_cadena[5:7])
    
        if not os.path.isdir(month_folder):
            messagebox.showerror("Error", f"No se encontró la carpeta del mes para el día {dia_cadena}.")
            return

        # Busca el archivo que coincide con el día
        day_file = next((f for f in os.listdir(month_folder) if f.endswith(".json") and f.startswith(dia_cadena[8:])), None)

        if day_file is None:
            messagebox.showerror("Error", f"No se encontró el archivo JSON para el día {dia_cadena}.")
            return

        # Construye el path completo del archivo JSON del día
        file_path = os.path.join(month_folder, day_file)

        # Lee el archivo JSON
        with open(file_path, 'r') as f:
            data = json.load(f)

        # Contabiliza los géneros
        gender_counts = {"femenino": 0, "masculino": 0}
        total_records = 0

        for record in data:
            info_text = record["info"]
            lines = info_text.split('\n')
            gender_line = next(line for line in lines if line.startswith('Género:'))
            gender = gender_line.split(': ')[1].strip().lower()
            
            if gender in gender_counts:
                gender_counts[gender] += 1
            total_records += 1

        # Muestra el resumen por género
        self.display_gender_breakdown({
            "total_records": total_records,
            "femenino": gender_counts["femenino"],
            "masculino": gender_counts["masculino"]
        }, dia_cadena)

    def display_gender_breakdown(self, counts, dia_cadena):
        breakdown_window = tk.Toplevel(self.master)
        breakdown_window.title(f"Resumen por Género del día {dia_cadena}")

        # Mostrar resumen por género
        tk.Label(breakdown_window, text=f"Femenino: {counts['femenino']} ({counts['femenino'] * 100 / counts['total_records']}%)").grid(row=0, column=0, padx=20, pady=10)
        tk.Label(breakdown_window, text=f"Masculino: {counts['masculino']} ({counts['masculino'] * 100 / counts['total_records']}%)").grid(row=0, column=1, padx=20, pady=10)
        # Crear frames para las listas
        mujeres_frame = tk.Frame(breakdown_window)
        hombres_frame = tk.Frame(breakdown_window)
    
        mujeres_frame.grid(row=1, column=0, padx=20, pady=10)
        hombres_frame.grid(row=1, column=1, padx=20, pady=10)

        # Mostrar lista de mujeres
        tk.Label(mujeres_frame, text="Mujeres", font=("Arial", 12, "bold")).pack()
        mujeres_listbox = tk.Listbox(mujeres_frame, width=40)
        mujeres_listbox.pack(fill=tk.BOTH, expand=True)
    
        # Mostrar lista de hombres
        tk.Label(hombres_frame, text="Hombres", font=("Arial", 12, "bold")).pack()
        hombres_listbox = tk.Listbox(hombres_frame, width=40)
        hombres_listbox.pack(fill=tk.BOTH, expand=True)

        # Llenar las listas con los datos
        self.fill_lists(counts, mujeres_listbox, hombres_listbox, dia_cadena)

    def fill_lists(self, counts, mujeres_listbox, hombres_listbox, dia_cadena):
        # Construye el path de la carpeta del mes
        month_folder = os.path.join("Fechas", dia_cadena[:4], dia_cadena[5:7])
    
        day_file = next((f for f in os.listdir(month_folder) if f.endswith(".json") and f.startswith(dia_cadena[8:])), None)
        if not day_file:
            messagebox.showerror("Error", f"No se encontró el archivo JSON para el día {dia_cadena}.")
            return

        full_path = os.path.join(month_folder, day_file)
        with open(full_path, 'r') as f:
            data = json.load(f)
            
            for record in data:
                info_text = record["info"]
                lines = info_text.split('\n')
                
                name = self.extract_info(lines, 'Nombre:')
                job = self.extract_info(lines, 'Oficio:')
                age = self.extract_info(lines, 'Edad:')
                gender_line = next((line for line in lines if line.startswith('Género:')), None)
                gender = gender_line.split(': ')[1].strip().lower() if gender_line else ''

                if gender == "femenino":
                    mujeres_listbox.insert(tk.END, f"{name} - {job}, {age} años")
                elif gender == "masculino":
                    hombres_listbox.insert(tk.END, f"{name} - {job}, {age} años")

    def extract_info(self, lines, field):
        matching_line = next((line for line in lines if line.startswith(field)), None)
        return matching_line.split(': ')[1].strip() if matching_line else ''


    def show_gender_details(self, counts):
        gender_window = tk.Toplevel(self.master)
        gender_window.title("Detalles por Género")

        for gender in ["femenino", "masculino"]:
            if counts[gender]:
                with open(os.path.join("fechas", counts["total_records"][:-2], "dia", f"{counts['total_records'][:-2]}_{gender}.json"), 'r') as f:
                    data = json.load(f)
                    for record in data:
                        name = record["info"].split("\n")[0].split(": ")[1].strip()
                        job = record["info"].split("\n")[2].split(": ")[1].strip()
                        age = record["info"].split("\n")[3].split(": ")[1].strip()
                        tk.Label(gender_window, text=f"Nombre: {name}\nOficio: {job}\nEdad: {age}").pack(pady=5)

    def show_information_menu(self):
        menu_window = tk.Toplevel(self.master)
        menu_window.title("Menú de Consulta")

        # Botón para mostrar años
        tk.Button(menu_window, text="Consultar Años", command=lambda: self.show_years(menu_window)).pack(pady=10)

        # Botón para volver atrás
        tk.Button(menu_window, text="Volver", command=menu_window.destroy).pack(pady=10)

    def start_scan(self):
        self.scan_button.config(state="disabled")
        self.info_button.config(state="disabled")
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
            
            self.detect_qr(frame)

            self.master.after(10, self.update_camera)

    def detect_qr(self, frame):
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
                
                    # Guardar la información en un archivo JSON
                    save_qr_info(self.info)
                
                    # Cerrar la ventana de cámara
                    self.cap.release()
                    self.camera_window.destroy()
                
                    # Habilitar el botón de información
                    self.info_button.config(state="normal")
                
                    # Mostrar mensaje de éxito
                    messagebox.showinfo("��xito", f"Información registrada con éxito.")
                
                    break

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

        # Crear la carpeta "Usuarios" si no existe
        usuarios_folder = "Usuarios"
        if not os.path.exists(usuarios_folder):
            os.makedirs(usuarios_folder)

        # Obtener el número del próximo usuario
        next_user_number = len(os.listdir(usuarios_folder)) + 1

        # Generar código QR con la información registrada
        qr_code = qrcode.QRCode(
            version=1,
            box_size=10,
            border=5
        )
        qr_code.add_data(f"Nombre: {nombre}, Edad: {edad}, Oficio: {oficio}, Género: {genero}")
        qr_code.make(fit=True)
    
        img = qr_code.make_image(fill_color="black", back_color="white")
        filename = f"{usuarios_folder}/usuario_{next_user_number}.png"
        img.save(filename)

        # Mostrar mensaje de éxito
        messagebox.showinfo("Éxito", f"Información registrada con éxito. El QR code se ha guardado como {filename}")

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
        
            self.info = f"Información extraída:\n"
            self.info += f"Nombre: {nombre}\n"
            self.info += f"Edad: {edad}\n"
            self.info += f"Oficio: {oficio}\n"
            self.info += f"Género: {genero}"
        
            # Guardar la información en un archivo JSON
            save_qr_info(self.info)

            # Actualizar la etiqueta detected_label
            self.detected_label.config(text=self.info)

            # Habilitar el botón de información
            self.info_button.config(state="normal")
        else:
            messagebox.showerror("Error", "No se pudo leer el código QR.")

if __name__ == "__main__":
    root = tk.Tk()
    app = QRScannerApp(root)
    root.mainloop()
