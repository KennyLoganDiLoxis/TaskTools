import tkinter as tk
from tkinter import ttk
import cv2
import pyaudio
import pygetwindow as gw
import tkinter.messagebox as mb
from PIL import Image, ImageTk
import threading
import tkinter.simpledialog as sd

class FotocameraApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Fotocamera")
        self.frame = tk.Frame(self.master)
        self.frame.pack(padx=10, pady=10)

        self.label = tk.Label(self.master)
        self.label.pack()

        # Combobox per selezionare la telecamera
        self.lbl_telecamera = tk.Label(self.frame, text="Seleziona Telecamera:")
        self.lbl_telecamera.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.cmb_telecamera = ttk.Combobox(self.frame)
        self.cmb_telecamera.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.cmb_telecamera.bind("<<ComboboxSelected>>", self.imposta_telecamera)

         # Imposta il valore predefinito nella combobox
        telecamere_disponibili = self.get_telecamere_disponibili()
        if telecamere_disponibili:
            self.cmb_telecamera["values"] = telecamere_disponibili
            self.cmb_telecamera.current(0)  # Imposta la prima telecamera come predefinita


        # Combobox per selezionare il microfono
        self.lbl_microfono = tk.Label(self.frame, text="Seleziona Microfono:")
        self.lbl_microfono.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.cmb_microfono = ttk.Combobox(self.frame)
        self.cmb_microfono.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.cmb_microfono.bind("<<ComboboxSelected>>", self.imposta_microfono)

        # Slider per regolare il volume del microfono
        self.lbl_volume = tk.Label(self.frame, text="Volume Microfono:")
        self.lbl_volume.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.slider_volume = tk.Scale(self.frame, from_=0, to=100, orient="horizontal")
        self.slider_volume.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        self.slider_volume.bind("<ButtonRelease-1>", self.imposta_volume)

        # Dopo la creazione dello slider del volume del microfono, aggiungiamo il nuovo slider
        self.lbl_frequenza_frame = tk.Label(self.frame, text="Frequenza Frame (ms):")
        self.lbl_frequenza_frame.grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.slider_frequenza_frame = tk.Scale(self.frame, from_=1, to=1000, orient="horizontal", resolution=1)
        self.slider_frequenza_frame.set(100)  # Impostiamo un valore predefinito
        self.slider_frequenza_frame.grid(row=3, column=1, padx=5, pady=5, sticky="ew")
        self.slider_frequenza_frame.bind("<ButtonRelease-1>", self.imposta_frequenza_frame)

        # Aggiungiamo un metodo per gestire il cambiamento della frequenza dei frame
    # Aggiungiamo un metodo per rilasciare la sorgente video corrente
    def rilascia_sorgente_video(self):
        if hasattr(self, 'cap'):
            self.cap.release()

    # Aggiorniamo il metodo apri_controlli per rilasciare la sorgente video prima di impostare la nuova
    def apri_controlli(self):
        # Rilascia la sorgente video corrente
        self.rilascia_sorgente_video()

        # Apri una finestra di dialogo per selezionare la telecamera
        telecamere_disponibili = self.get_telecamere_disponibili()
        telecamera_selezionata = sd.askinteger("Selezione Telecamera", "Inserisci l'indice della telecamera:", parent=self.master, minvalue=0, maxvalue=len(telecamere_disponibili)-1)
        if telecamera_selezionata is None:
            mb.showinfo("Informazione", "Nessuna telecamera selezionata.")
            return

        # Imposta la telecamera selezionata
        self.cap = cv2.VideoCapture(telecamere_disponibili[telecamera_selezionata])

        # Altri controlli...

    
    def imposta_frequenza_frame(self, event):
        nuova_frequenza = self.slider_frequenza_frame.get()
        # Imposta la nuova frequenza di frame
        self.frequenza_frame = nuova_frequenza


        # Variabili per memorizzare le impostazioni
        self.telecamera_selezionata = None
        self.microfono_selezionato = None

        # Aggiorna i dispositivi disponibili
        self.aggiorna_dispositivi()

        # Avvia lo streaming video
        self.avvia_streaming()

    def aggiorna_dispositivi(self):
        # Aggiorna le fotocamere disponibili
        telecamere_disponibili = self.get_telecamere_disponibili()
        self.cmb_telecamera["values"] = telecamere_disponibili

        # Aggiorna i microfoni disponibili
        microfoni_disponibili = self.get_microfoni_disponibili()
        self.cmb_microfono["values"] = microfoni_disponibili

    def imposta_telecamera(self, event):
        self.telecamera_selezionata = self.cmb_telecamera.get()
        self.avvia_streaming()  # Riavvia lo streaming con la nuova telecamera

    def imposta_microfono(self, event):
        self.microfono_selezionato = self.cmb_microfono.get()
        self.aggiorna_dispositivi()

    def imposta_volume(self, event):
        volume = self.slider_volume.get()
        # Codice per impostare il volume del microfono

    def get_telecamere_disponibili(self):
        telecamere = []
        num_telecamere = 2  # Numero massimo di telecamere da controllare
        for i in range(num_telecamere):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                telecamere.append(f"Telecamera {i}")  # Aggiungi il nome della telecamera
                cap.release()
        return telecamere

    def get_microfoni_disponibili(self):
        p = pyaudio.PyAudio()
        num_microfoni = p.get_device_count()
        microfoni = [p.get_device_info_by_index(i).get('name') for i in range(num_microfoni)]
        p.terminate()
        return microfoni

    def avvia_streaming(self):
        # Rilascia la risorsa della telecamera corrente
        if hasattr(self, 'cap'):
            self.cap.release()
        # Acquisisci la risorsa della nuova telecamera selezionata
        self.cap = cv2.VideoCapture(self.cmb_telecamera.current())
        if not self.cap.isOpened():
            print("Impossibile aprire la telecamera")
            return
        
        # Regola la risoluzione della telecamera
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  # Imposta la larghezza del frame a 640 pixel
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)  # Imposta l'altezza del frame a 480 pixel


        # Avvia lo streaming con la nuova telecamera selezionata
        self.cap = cv2.VideoCapture(self.cmb_telecamera.current())
        self.thread = threading.Thread(target=self.mostra_frame)
        self.thread.daemon = True
        self.thread.start()

    def mostra_frame(self):
        ret, frame = self.cap.read()
        if ret:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            
            # Regola le dimensioni dell'immagine per adattarle alla finestra
            img = img.resize((640, 480), Image.ANTIALIAS)
            
            img_tk = ImageTk.PhotoImage(image=img)
            self.label.config(image=img_tk)
            self.label.image = img_tk
        self.label.after(self.frequenza_frame, self.mostra_frame)


def crea_interfaccia():
    root = tk.Tk()
    app = FotocameraApp(root)
    root.mainloop()

if __name__ == "__main__":
    crea_interfaccia()
