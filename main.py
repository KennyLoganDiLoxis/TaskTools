import tkinter as tk
from tkinter import filedialog
import customtkinter 
from customtkinter import CTkComboBox
from CTkMessagebox import CTkMessagebox
import requests
import pymysql
import datetime
from PIL import Image, ImageTk
import os
import io
from io import BytesIO
import psutil
import numpy as np
from bs4 import BeautifulSoup
import geolocalizzazione
from interfaccia_multimediale import FotocameraApp 

def center_window(window, offset_x=0, offset_y=0, relative_to=None):
    """
    Questa funzione centra una finestra sullo schermo, con opzionali offset e posizionamento relativo.

    Args:
        window (tk.Tk): La finestra da centrare.
        offset_x (int): Spostamento orizzontale opzionale dal centro (valore predefinito 0).
        offset_y (int): Spostamento verticale opzionale dal centro (valore predefinito 0).
        relative_to (tk.Tk): Finestra di riferimento opzionale per il posizionamento relativo (valore predefinito None).

    """

    try:
        # Ottieni le dimensioni dello schermo
        screen_width = tk.winfo_screenwidth()
        screen_height = tk.winfo_screenheight()

        # Ottieni le dimensioni della finestra
        window_width = window.winfo_width()
        window_height = window.winfo_height()

        # Calcola la posizione x e y per centrare il contenuto della finestra
        x = int((screen_width - window_width) / 2) + offset_x
        y = int((screen_height - window_height) / 2) + offset_y

        # Se specificato, posiziona la finestra relativamente a un'altra finestra
        if relative_to:
            x += relative_to.winfo_x()
            y += relative_to.winfo_y()

        # Sposta la finestra in modo che il suo centro coincida con la posizione calcolata
        window.geometry(f"+{x}+{y}")

    except Exception as e:
        print(f"Errore durante il centraggio della finestra: {e}")

def get_ip_info():
    try:
        user_ip_info=geolocalizzazione.user_info
        return user_ip_info
    except Exception as e:
        print("Errore durante la richiesta delle informazioni sull'indirizzo IP:", e)
        return None
def get_flag_url(country_code, flag_folder):
    # Costruire il percorso del file della bandiera
    flag_filename = f"{country_code.lower()}.png"
    flag_path = os.path.join(flag_folder, flag_filename)

    # Verificare se il file della bandiera esiste
    if os.path.isfile(flag_path):
        # Caricare e restituire l'immagine della bandiera
        return Image.open(flag_path)
    
    # Se il file della bandiera non esiste nella cartella w640,
    # restituisci None
    return None

# Funzione per la connessione al database MySQL
def connect_to_database():
    try:
        # Modifica questi valori con le credenziali del tuo database MySQL
        conn = pymysql.connect(
            host="localhost",
            user="",
            password="",
            database="",
            port=,
            charset=''
        )
        print("Connessione al database MySQL riuscita!")
        return conn, None  # Restituisce la connessione e nessun errore
    except pymysql.Error as err:
        print(f"Connessione al database MySQL fallita! Errore: {err}")
        return None, err
#variabile globale di appoggio che cambia valore all'accesso dell'utente
accesso_utente = False

#variabile globale per l'id_utente
id_utente = None

# Creazione della finestra principale
root = tk.Tk()
customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("blue")

# Impostazione delle dimensioni della finestra principale
root.geometry("1920x1080")
# Impostazione dello sfondo della finestra principale a blu scuro34/
root.configure(bg="#1e1e3f")
#center_window(root)
# Colore di sfondo e testo per il frame degli utenti online
users_bg_color = "#1e1e3f"
users_fg_color = "gray85"

# Colore di sfondo e testo per il frame di stato
status_bg_color = "#0033FF"
status_fg_color = "gray85"

#creazione del frame del menu
menu_frame = tk.Frame(root, bg=status_bg_color)   
menu_frame.pack(side=tk.TOP, fill=tk.X)

# Creazione del frame di stato
status_frame = tk.Frame(root, bg=status_bg_color)
status_frame.pack(side=tk.BOTTOM, fill=tk.X)

# Impostazione dell'altezza disponibile per il frame degli utenti online
users_frame_height = menu_frame.winfo_height() - status_frame.winfo_height()
# Creazione del frame per gli utenti online
users_frame = tk.Frame(root, bg=users_bg_color, bd=1, relief=tk.SOLID)

# decommenta la seguente linea se vuoi che il menu appaia all'avvio dell'applicazione:
users_frame.place(x=0, y=50, width=300,height=1009)

# Funzione per aprire o chiudere il frame del menu
def apriChiudi_menu():
    global users_frame
    if users_frame.winfo_ismapped():  # Verifica se il frame è visibile
        users_frame.place_forget()  # Se è visibile, lo nasconde
        print ("Chiude il menu")
    else:
        users_frame.place(x=0, y=50, width=300,height=10009)
        print ("Apre il menu")

# Funzione per ottenere il numero di utenti registrati e online
def get_user_counts():
    conn, error = connect_to_database()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM utenti")
                num_registered_users = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM utenti_online")
                num_online_users = cursor.fetchone()[0]

            conn.close()
            return num_registered_users, num_online_users
        except pymysql.Error as err:
            print(f"Errore durante l'ottenimento del conteggio degli utenti: {err}")
            return 0, 0
    else:
        return 0, 0
    
# Funzione per aggiornare le etichette degli utenti registrati e online
def update_user_labels():
    num_registered_users, num_online_users = get_user_counts()
    users_label.config(text=f"Utenti registrati: {num_registered_users}")
    online_label.config(text=f"Utenti online: {num_online_users}")
    root.after(10000, update_user_labels)  # Aggiorna le etichette ogni 10 secondi

def get_user_access_control(email,password):
    conn, error = connect_to_database()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM utenti WHERE email = %s AND password = %s", (email, password))
                account_ok = cursor.fetchone()[0]

            conn.close()
            return account_ok
        except pymysql.Error as err:
            print(f"Errore durante l'ottenimento del conteggio degli utenti: {error}")
            return 0
    else:
        return 0
    

def get_user_data(email, password):
    global id_utente  # Dichiaro che sto usando la variabile globale

    conn, error = connect_to_database()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM utenti WHERE email = %s AND password = %s limit 1", (email, password))
                account_ok = cursor.fetchone()
                if account_ok:  # Se trova un utente corrispondente
                    id_utente = account_ok[0]  # Imposta l'id_utente globale
                else:
                    id_utente = None  # Nessun utente trovato, imposto id_utente a None

            conn.close()
            return account_ok
        except pymysql.Error as err:
            print(f"Errore durante l'ottenimento dei dati dell'utente: {error}")
            return None
    else:
        return None
    

# Aggiungi un utente nella tabella online
def aggiungi_user_online(id_utente):
    conn, error = connect_to_database()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute(f"INSERT INTO utenti_online (id_utente) VALUES ({id_utente})")
                conn.commit()
                print (f"\nTabella utenti online aggiornata correttamente con il tuo accesso (ID: {id_utente})\n")
            conn.close()
        except pymysql.Error as err:
            print(f"Errore durante l'aggiunta dell'utente online: {error}")
    else:
        print(f"Errore durante la connessione al database: {error}")

# Funzione per rimuovere un utente dagli online
def togli_user_online(id_utente):
    conn, error = connect_to_database()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute(f"DELETE FROM utenti_online WHERE id_utente = {id_utente}")
                conn.commit()
                print (f"\nTabella utenti online aggiornata correttamente con la tua uscita (ID: {id_utente})\n")
            conn.close()

            # rimuovi il pulsante Profilo se l'utente viene rimosso dall'utente online
            
            menu_btn_profilo.place_forget()
            # Etichetta per il pulsante del PANNELLO "MENU" -> "ACCEDI"
            menu_btn_accedi = customtkinter.CTkButton(users_frame, width=300, height=30, text="ACCEDI", command=accedi)
            menu_btn_accedi.place(x=0, y=30)
            # inserisci il pulsante Iscriviti
            menu_btn_iscriviti.place(x=0, y=64)
            
        except pymysql.Error as err:
            print(f"Errore durante la rimozione dell'utente online: {error}")
    else:
        print(f"Errore durante la connessione al database: {error}")

# Funzione per rimuovere i record più vecchi di 20 minuti dalla tabella utenti_online
def delete_old_records(conn):
    try:
        with conn.cursor() as cursor:
            # Calcola la data e l'ora attuali meno 20 minuti
            twenty_minutes_ago = datetime.datetime.now() - datetime.timedelta(minutes=20)
            # Esegui la query per cancellare i record più vecchi di twenty_minutes_ago
            cursor.execute("DELETE FROM utenti_online WHERE timestamp < %s", (twenty_minutes_ago,))
            # Conferma le modifiche al database
            conn.commit()

        print("Record più vecchi di 20 minuti cancellati correttamente.")
    except pymysql.Error as err:
        print(f"Errore durante la cancellazione dei record: {err}")

def accedi():
    # Funzione per controllare l'accesso al database con le credenziali inserite
    def ctrl_db_access():
        # Inserisci qui la logica per controllare l'accesso al database con le credenziali inserite
        
        email = email_entry.get()
        password = password_entry.get()
        
        #print (f"Email: {email}, Password: {password}\nQuery: SELECT COUNT(*) FROM utenti WHERE email = '{email}' AND password = '{password}'")   
        accesso = get_user_access_control(email,password)
        if accesso == 1:
            # Aggiungi l'utente online
            aggiungi_user_online(accesso)
            get_user_data(email,password)
            global accesso_utente 
            accesso_utente = True
            menu_btn_iscriviti.place_forget()
            menu_btn_profilo.place(x=0, y=64)
            # Restituisci True se l'accesso è consentito, altrimenti False
            return accesso  # Placeholder
        else:
            return accesso

    # Creazione della finestra di login
    login_window = tk.Toplevel(root)
    login_window.geometry("400x200")
    login_window.configure(bg="#1e1e3f")
    login_window.title("Login")
    center_window(login_window)

    # Etichetta e campo di inserimento per l'email
    email_label = tk.Label(login_window, text="E-mail", bg="#1e1e3f", fg="gray85")
    email_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
    email_entry = customtkinter.CTkEntry(login_window)
    email_entry.grid(row=0, column=1, padx=10, pady=10)

    # Etichetta e campo di inserimento per la password
    password_label = tk.Label(login_window, text="Password", bg="#1e1e3f", fg="gray85")
    password_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")
    password_entry = customtkinter.CTkEntry(login_window, show="*")
    password_entry.grid(row=1, column=1, padx=10, pady=10)

    # Funzione per verificare le credenziali e cambiare il testo del pulsante ACCEDI se necessario
    def check_credentials():
        id_Utente = ctrl_db_access() 
        #print (f"\nID Utente: {id_Utente}\n")
        if id_Utente> 0:
            menu_btn_accedi.configure(text=f"ESCI (ID:00AFK-{id_Utente})", command=lambda: togli_user_online(id_Utente))
            login_window.destroy()  # Chiudi la finestra di login se l'accesso è riuscito
        else:
            # Inserisci qui le azioni da eseguire in caso di accesso fallito
            login_window.destroy()  # Chiudi la finestra di login
            pass

    # Pulsante "invia" per controllare le credenziali
    send_button = customtkinter.CTkButton(login_window, text="Invia", command=check_credentials)
    send_button.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

def iscriviti():
    # Funzione per controllare se la password rispetta i criteri richiesti
    def check_password(password):
        # Lunghezza minima della password
        if len(password) < 8:
            return False
        # Conteggio dei numeri nella password
        num_count = sum(1 for char in password if char.isdigit())
        # Conteggio dei caratteri speciali nella password
        special_char_count = sum(1 for char in password if char in "*@#!+?")
        # Controllo dei criteri richiesti
        if num_count < 3 or special_char_count < 1:
            return False
        return True

    # Funzione per controllare se la password è uguale alla ripetizione
    def check_password_match(password, repeat_password):
        return password == repeat_password

    # Funzione per gestire l'iscrizione
    def submit_registration():
        # Recupero dei valori inseriti dall'utente
        nome = nome_entry.get()
        cognome = cognome_entry.get()
        email = email_entry.get()
        password = password_entry.get()
        repeat_password = repeat_password_entry.get()
        admin_default = 0
        #print (f"\nParametri di inserimento nella tabella utenti:\n{nome, cognome, email, password, admin_default}")
        # Controllo della validità della password
        if not check_password(password):
            #messagebox.showerror("Errore", "La password non rispetta i criteri richiesti.")
            CTkMessagebox(title="Errore", message="Errore: La password non rispetta i criteri richiesti\nLa password deve contenere uno dei seguenti caratteri speciali: * @ # ! + ?", icon="cancel")
            return

        # Controllo che le password coincidano
        if not check_password_match(password, repeat_password):
            #messagebox.showerror("Errore", "Le password non corrispondono.")
            CTkMessagebox(title="Errore", message="Errore: Il campo 'password' e 'ripeti password' non corrispondono", icon="cancel")
            return

        # Qui puoi eseguire l'azione per registrare l'utente nel database
        # Rimuove i record più vecchi di 20 minuti nella tabella Online
        conn, error = connect_to_database()
        if conn:
            try:
                with conn.cursor() as cursor:
                    #print (f"\nLa query: INSERT INTO utenti (nome, cognome, email, password, data_iscrizione, admin) VALUES ({nome}, {cognome}, {email}, {password},NOW(), {admin_default})\n")
                    cursor.execute(f"INSERT INTO utenti (nome, cognome, email, password, data_iscrizione, admin) VALUES ('{nome}', '{cognome}', '{email}', '{password}', NOW(), '{admin_default}')")
                    conn.commit()
                    #print (f"\nTabella utenti aggiornata correttamente con la tua iscrizione ({nome, cognome, email, password, admin_default})\n")
                conn.close()
            except pymysql.Error as error:
                print(f"Errore durante l'iscrizione dell'utente: {error}")
        else:
            print(f"Errore durante la connessione al database: {error}")
        # Opzionalmente, puoi chiudere la finestra di iscrizione
        finestra_iscrizione.destroy()

    # Creazione della finestra di iscrizione
    finestra_iscrizione = tk.Toplevel(root)
    finestra_iscrizione.title("Iscriviti")
    # Impostazione delle dimensioni della finestra principale
    finestra_iscrizione.geometry("512x250")
    # Impostazione dello sfondo della finestra principale a blu scuro
    finestra_iscrizione.configure(bg="#1e1e3f")
    center_window(finestra_iscrizione)

    # Creazione dei campi di input
    tk.Label(finestra_iscrizione, text="Nome:", bg="#1e1e3f", fg="gray85").grid(row=0, column=0, padx=10, pady=5)
    nome_entry = customtkinter.CTkEntry(finestra_iscrizione)
    nome_entry.grid(row=0, column=1, padx=10, pady=5)

    tk.Label(finestra_iscrizione, text="Cognome:", bg="#1e1e3f", fg="gray85").grid(row=1, column=0, padx=10, pady=5)
    cognome_entry = customtkinter.CTkEntry(finestra_iscrizione)
    cognome_entry.grid(row=1, column=1, padx=10, pady=5)

    tk.Label(finestra_iscrizione, text="Email:", bg="#1e1e3f", fg="gray85").grid(row=2, column=0, padx=10, pady=5)
    email_entry = customtkinter.CTkEntry(finestra_iscrizione)
    email_entry.grid(row=2, column=1, padx=10, pady=5)

    tk.Label(finestra_iscrizione, text="Password:", bg="#1e1e3f", fg="gray85").grid(row=3, column=0, padx=10, pady=5)
    password_entry = customtkinter.CTkEntry(finestra_iscrizione, show="*")
    password_entry.grid(row=3, column=1, padx=10, pady=5)

    tk.Label(finestra_iscrizione, text="Ripeti Password:", bg="#1e1e3f", fg="gray85").grid(row=4, column=0, padx=10, pady=5)
    repeat_password_entry = customtkinter.CTkEntry(finestra_iscrizione, show="*")
    repeat_password_entry.grid(row=4, column=1, padx=10, pady=5)

    # Bottone per inviare il modulo di iscrizione
    submit_button = customtkinter.CTkButton(finestra_iscrizione, text="Iscriviti", command=submit_registration)
    submit_button.grid(row=5, column=0, columnspan=2, padx=10, pady=10)

    # Imposta il focus sul campo Nome all'apertura della finestra
    nome_entry.focus_set()

    # Blocca l'interazione con la finestra principale fino alla chiusura di questa finestra di iscrizione
    finestra_iscrizione.transient(root)
    finestra_iscrizione.grab_set()
    root.wait_window(finestra_iscrizione)


# Funzione per caricare un'immagine da file system
def caricamento_immagine():
    # Apre una finestra di dialogo per la selezione dell'immagine
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.jpeg;*.png")])
    if file_path:
        try:
            # Apri l'immagine selezionata
            image = Image.open(file_path)
            # Controlla se l'immagine supera i 4MB
            if os.path.getsize(file_path) > 4 * 1024 * 1024:
                #messagebox.showerror("Errore", "L'immagine non può superare i 4MB.")
                CTkMessagebox(title="Errore", message="L'immagine non può superare i 4MB.", icon="cancel")
                return
            # Controlla se l'immagine è in formato .jpg o .png
            if not file_path.lower().endswith(('.jpg', '.jpeg', '.png')):
                #messagebox.showerror("Errore", "L'immagine deve essere in formato .jpg o .png.")
                CTkMessagebox(title="Errore", message="L'immagine deve essere in formato .jpg o .png.", icon="cancel")
                return
            
            # Ridimensiona l'immagine per adattarla al riquadro 256x256
            image.thumbnail((256, 256))
            
            # Converti l'immagine in formato Tkinter PhotoImage
            photo = ImageTk.PhotoImage(image)

            # Creiamo un buffer in memoria per salvare l'immagine in formato PNG
            buffer = io.BytesIO()
            image.save(buffer, format="PNG")

            # Ora l'immagine è salvata nel buffer in formato PNG
            # Convertiamo l'immagine nel formato dei byte
            byte_immagine = buffer.getvalue()


            # Visualizza l'immagine nella label
            lbl_immagine_profilo.config(image=photo)
            lbl_immagine_profilo.image = photo  # Conserva il riferimento all'immagine per evitare la garbage collection
            # Salva l'immagine nel database
            conn, error = connect_to_database()
            if conn:
                try:
                    with conn.cursor() as cursor:
                        # Codice per salvare l'immagine nel database
                        # Sostituisci 'immagine' con la variabile contenente i dati dell'immagine
                        # Sostituisci 'utente_id' con l'ID dell'utente corrente
                        cursor.execute("UPDATE utenti SET img_profilo = %s WHERE id = %s", (byte_immagine, '3'))
                    conn.commit()
                    print("Immagine del profilo aggiornata nel database.")
                except pymysql.Error as error:
                    print(f"Errore durante il salvataggio dell'immagine nel database: {error}")
                finally:
                    conn.close()
        except Exception as e:
             #messagebox.showerror("Errore", f"Errore durante il caricamento dell'immagine: {e}")
             CTkMessagebox(title="Errore", message=f"Errore durante il caricamento dell'immagine: {e}", icon="cancel")
             print (f"Errore durante il caricamento dell'immagine: {e}")


def apri_finestra_profilo(id):

    global id_utente
    id_utente = id

    def caricamento_immagine_profilo():
        conn, error = connect_to_database()
        if conn:
            try:
                with conn.cursor() as cursor:
                    # Eseguire la query per ottenere i dati dell'immagine del profilo
                    cursor.execute("SELECT img_profilo FROM utenti WHERE id = %s", (id_utente,))
                    img_data = cursor.fetchone()[0]

                    if img_data:
                        # Convertire i dati dell'immagine in un oggetto immagine Tkinter
                        img = Image.open(io.BytesIO(img_data))
                        img = img.resize((256, 256))
                        photo = ImageTk.PhotoImage(img)

                        # Aggiornare l'etichetta dell'immagine del profilo
                        lbl_immagine_profilo.config(image=photo)
                        lbl_immagine_profilo.image = photo  # Conservare il riferimento all'immagine per evitare la garbage collection
                        
                       
                    else:
                        # Caricare l'immagine generica se non ci sono dati dell'immagine nel profilo
                        img_generico = Image.open("profile_generic_image.png")
                        img_generico = img_generico.resize((256, 256), resample=Image.LANCZOS)
                        photo_generico = ImageTk.PhotoImage(img_generico)
                        lbl_immagine_profilo.config(image=photo_generico)
                        lbl_immagine_profilo.image = photo_generico  # Conservare il riferimento all'immagine per evitare la garbage collection
            except pymysql.Error as error:
                print(f"Errore durante il caricamento dell'immagine del profilo: {error}")
            finally:
                conn.close()


    # Funzione per gestire l'invio dei dati del profilo
    def invia_dati_profilo():
        # Recupera i valori inseriti nei campi del profilo
        nome = entry_nome.get()
        cognome = entry_cognome.get()
        gps = lbl_img_stato.cget("text")  # Assumo che lbl_img_stato mostri le informazioni GPS
        nazione_origine = lbl_stato.cget("text")  # Assumo che lbl_stato mostri la nazionalità di origine
        descrizione=textbox_area_descrizione.get("0.0", "end")
        conn, e = connect_to_database()
        # Eseguire l'aggiornamento nel database
        # (Assicurati di avere una connessione al database e di eseguire il comando SQL corretto)
        if conn:
            try:
                # Eseguire la query SQL per aggiornare i dati dell'utente nel database
                # (sostituisci 'conn' con l'oggetto della connessione al tuo database)
                cursor = conn.cursor()
                query_update_profilo=f"UPDATE utenti SET nome = '{nome}', cognome = '{cognome}', descrizione = '{descrizione}', nazione_origine = '{nazione_origine}' WHERE id = {id_utente}"
                #print (f"\nQuery update profilo: {query_update_profilo} ")
                cursor.execute(query_update_profilo)
                conn.commit()
                cursor.close()
                #messagebox.showinfo("Successo", "")
                CTkMessagebox(title="Successo", message="I dati del profilo sono stati aggiornati con successo.")
            except pymysql.Error as e:
                CTkMessagebox(title="Errore",  message=f"Si è verificato un errore durante l'aggiornamento dei dati del profilo: {str(e)}")
                #print (f"Problema Mysql durante la modifica del profilo: {str(e)}")

    # Creazione della finestra del profilo
    finestra_profilo = tk.Toplevel(root)
    finestra_profilo.title("Profilo Utente")
    finestra_profilo.geometry("562x638")
    finestra_profilo.configure(bg="#1e1e3f")
    center_window(finestra_profilo)
    finestra_profilo.resizable(False, False)

    # Frame sinistro per l'immagine del profilo
    frame_sinistro = tk.Frame(finestra_profilo, width=290, height=290, bg="#1e1e3f")
    frame_sinistro.grid(row=0, column=0)

    # Immagine del profilo
    global lbl_immagine_profilo
    lbl_immagine_profilo = tk.Label(frame_sinistro)
    lbl_immagine_profilo.grid(row=0, column=0, padx=10, pady=10)
    lbl_immagine_profilo.bind("<Button-1>", lambda event: caricamento_immagine_profilo())

    # Caricare l'immagine del profilo
    caricamento_immagine_profilo()
    #menu_btn_accedi = customtkinter.CTkButton(users_frame, width=300, height=30, text="ACCEDI", command=accedi)
    #menu_btn_accedi.place(x=0, y=30)
    def avvia_interfaccia_multimediale():
        top = tk.Toplevel()
        app = FotocameraApp(top)
    bottone_avvio_webcam = customtkinter.CTkButton(frame_sinistro, text="Avvia Interfaccia Multimediale", command=avvia_interfaccia_multimediale)
    bottone_avvio_webcam.grid(row=1, column=0, padx=10, pady=10)

    # Frame destro per le etichette e i campi di nome, cognome, stato di provenienza
    frame_destro = tk.Frame(finestra_profilo, width=290, height=290, bg="#1e1e3f")
    frame_destro.grid(row=0, column=1)

    # Definizione dei campi e delle etichette per il profilo
    lbl_nome = tk.Label(frame_destro, text="Nome:", bg="#1e1e3f", fg="white")
    lbl_nome.grid(row=0, column=0, padx=10, pady=5, sticky="w")
    entry_nome = customtkinter.CTkEntry(frame_destro, placeholder_text="Il tuo nome")
    entry_nome.grid(row=0, column=1, padx=10, pady=5)

    lbl_cognome = tk.Label(frame_destro, text="Cognome:", bg="#1e1e3f", fg="white")
    lbl_cognome.grid(row=1, column=0, padx=10, pady=5, sticky="w")
    entry_cognome = customtkinter.CTkEntry(frame_destro, placeholder_text="Il tuo cognome")
    entry_cognome.grid(row=1, column=1, padx=10, pady=5)

    lbl_stato = tk.Label(frame_destro, text="Nazionalità di origine:", bg="#1e1e3f", fg="white")
    lbl_stato.grid(row=2, column=0, padx=10, pady=5, sticky="w")

    lbl_img_stato = tk.Label(frame_destro, text="GPS:", bg="#1e1e3f", fg="white")
    lbl_img_stato.grid(row=3, column=0, padx=10, pady=5, sticky="w")

    # Label per visualizzare l'immagine della bandiera
    flag_label = tk.Label(frame_destro, bg="#1e1e3f")
    flag_label.grid(row=3, column=1, padx=10, pady=5, sticky="w")

    # Funzione per ottenere il nome dello stato dall'indirizzo IP e visualizzare la bandiera corrispondente
    def visualizza_stato_e_bandiera():
        ip_info = get_ip_info()
        if ip_info:
            country_name = ip_info.get('country_name')
            country_code = ip_info.get('country_code')
            if country_name:
                # Visualizza il nome dello stato nel profilo
                lbl_stato.config(text=f"GPS: {country_name}")
                flag = get_flag_url(country_code, 'w640')
                
                if flag:
                    flag = flag.resize((100, 50))
                    flag_photo = ImageTk.PhotoImage(flag)
                    flag_label.config(image=flag_photo)
                    flag_label.image = flag_photo
                else:
                    print("Nessuna bandiera trovata per lo stato specificato.")
            else:
                print("Nome dello stato non disponibile.")
        else:
            print("Informazioni sull'indirizzo IP non disponibili.")

    # Aggiungi un pulsante per visualizzare lo stato e la bandiera
    #btn_stato = customtkinter.CTkButton(frame_destro, text="Mostra stato e bandiera", command=visualizza_stato_e_bandiera)
    #btn_stato.grid(row=4, column=0, columnspan=2, pady=10)
    visualizza_stato_e_bandiera()

    # Esegui la funzione per mostrare l'immagine della bandiera
    
    # Creazione di una combobox con i nomi degli stati
    conn, error = connect_to_database()
    if conn:
        try:
            with conn.cursor() as cursor:
                # Query SQL per selezionare i nomi degli stati dalla tabella "stati"
                cursor.execute("SELECT nome_stati, sigla_iso_3166_1_alpha_3_stati FROM stati")

                # Recupera tutti i risultati della query
                risultati = cursor.fetchall()

                # Ottieni SOLO I NOMI degli stati dalla lista di tuple
                nomi_stati = [row[0] for row in risultati]
                # Creazione della combobox
                combo_stati = customtkinter.CTkComboBox(master=frame_destro,
                                                        values=nomi_stati)
                combo_stati.grid(row=2, column=1, padx=10, pady=5)
                #combo_stati.set(country)
        except pymysql.Error as error:
            print(f"Errore durante l'esecuzione della query: {error}")
        finally:
            conn.close()

    # Aggiungi altri campi e etichette per gli altri dati del profilo

    # Frame basso per l'area di testo e il pulsante Invia
    frame_basso = tk.Frame(finestra_profilo, width=580, height=300, bg="#1e1e3f")
    frame_basso.grid(row=1, column=0, columnspan=2)

    # Creazione dell'area di testo personalizzata
    textbox_area_descrizione = customtkinter.CTkTextbox(frame_basso, width=560, height=280)
    textbox_area_descrizione.pack(fill='x', expand=True)  # Riempie l'intero frame basso

    # Bottone per inviare i dati del profilo
    btn_invia = customtkinter.CTkButton(frame_basso, text="Salva Modifiche", command=invia_dati_profilo)
    btn_invia.pack(fill='x', expand=True)

# Etichette per gli utenti registrati e online
users_label = tk.Label(status_frame, text="Utenti registrati: 0", bg=status_bg_color, fg=status_fg_color)
users_label.pack(side=tk.LEFT)
online_label = tk.Label(users_frame, text="Utenti online: 0", bg=users_bg_color, fg=users_fg_color)
online_label.pack(fill=tk.X)

# Rimuove i record più vecchi di 20 minuti nella tabella Online
conn, error = connect_to_database()
if conn:
    delete_old_records(conn)
    conn.close()

# Connessione al database per aggiornare le etichette
update_user_labels()

# Etichetta per il primo pulsante del menu "MENU"
menu_file_first = customtkinter.CTkButton(menu_frame, text="MENU", command=apriChiudi_menu)
menu_file_first.pack(padx=10, pady=10, side=tk.LEFT)

# Etichetta per il pulsante del PANNELLO "MENU" -> "ACCEDI"
menu_btn_accedi = customtkinter.CTkButton(users_frame, width=300, height=30, text="ACCEDI", command=accedi)
menu_btn_accedi.place(x=0, y=30)

# il pulsante Iscriviti e Profilo dovranno apparire solo se l'utente ha effettuato l'accesso

# Etichetta per il pulsante del PANNELLO "MENU" -> "ISCRIVITI"
menu_btn_iscriviti = customtkinter.CTkButton(users_frame, width=300, height=30, text="ISCRIVITI", command=iscriviti)
menu_btn_iscriviti.place(x=0, y=64)

# Etichetta per il pulsante del PANNELLO "MENU" -> "PROFILO"
menu_btn_profilo = customtkinter.CTkButton(users_frame, width=300, height=30, text="PROFILO", command=lambda:apri_finestra_profilo(id_utente))
menu_btn_profilo.place(x=0, y=98)

# nasconde il pulsante Profilo
menu_btn_profilo.place_forget()

# Etichetta per la connessione al database
conn_label = tk.Label(status_frame, text="Connessione al database MySQL riuscita correttamente!", padx=5, bg=status_bg_color, fg=status_fg_color)
conn_label.pack(side=tk.LEFT)

root.title("TaskTools")
center_window(root)
root.mainloop()
