import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
from tkinter import ttk
from mutagen.easyid3 import EasyID3
from mutagen.flac import FLAC

class GestionnaireBibliothequeMusicale:
    def __init__(self, root):
        self.root = root
        self.root.title("DeesMusic")
        self.root.geometry("800x600")  # Ajustez la taille selon vos besoins

        self.liste_de_musique = []
        self.playlists = {}
        self.selected_playlist = tk.StringVar()

        # Créer une barre de menu
        self.menu_bar = tk.Menu(root)

        # Menu "Fichier"
        self.menu_fichier = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_fichier.add_command(label="Ajouter des fichiers musicaux", command=self.ajouter_musique)
        self.menu_fichier.add_command(label="Quitter", command=root.destroy)
        self.menu_bar.add_cascade(label="Fichier", menu=self.menu_fichier)

        # Menu "Playlist"
        self.menu_playlist = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_playlist.add_command(label="Créer une playlist", command=self.creer_playlist)
        self.menu_playlist.add_command(label="Ajouter à la playlist", command=self.ajouter_a_playlist)
        self.menu_playlist.add_command(label="Afficher la playlist", command=self.afficher_playlist)
        self.menu_bar.add_cascade(label="Playlist", menu=self.menu_playlist)

        root.config(menu=self.menu_bar)

        # Créer des widgets
        self.frame = ttk.Frame(root, style="TFrame")
        self.frame.pack(padx=20, pady=20)

        # Ajustez les dimensions du Listbox
        self.liste_box = tk.Listbox(self.frame, bd=0, selectbackground="#FFD700", height=20, width=50)
        self.liste_box.pack(pady=10)

        self.playlist_combobox = ttk.Combobox(self.frame, textvariable=self.selected_playlist, state="readonly")
        self.playlist_combobox.pack(pady=10)

        self.maj_liste_box()

    def ajouter_musique(self):
        fichiers = filedialog.askopenfilenames(title="Sélectionnez des fichiers musicaux", filetypes=[("Fichiers audio", "*.mp3;*.wav;*.flac")])
        if fichiers:
            self.liste_de_musique.extend(fichiers)
            self.maj_liste_box()

    def creer_playlist(self):
        nom_playlist = simpledialog.askstring("Créer une playlist", "Entrez le nom de la playlist:")
        if nom_playlist:
            self.playlists[nom_playlist] = []
            self.maj_liste_combobox()

    def ajouter_a_playlist(self):
        selected_playlist = self.selected_playlist.get()
        if selected_playlist in self.playlists:
            selected_files = filedialog.askopenfilenames(title=f"Sélectionnez des fichiers pour {selected_playlist}",
                                                          filetypes=[("Fichiers audio", "*.mp3;*.wav;*.flac")])
            self.playlists[selected_playlist].extend(selected_files)

    def afficher_playlist(self):
        selected_playlist = self.selected_playlist.get()
        if selected_playlist in self.playlists:
            playlist_content = "\n".join(self.playlists[selected_playlist])
            messagebox.showinfo(f"Contenu de {selected_playlist}", playlist_content)
        else:
            messagebox.showwarning("Playlist non trouvée", f"La playlist '{selected_playlist}' n'existe pas.")

    def maj_liste_box(self):
        self.liste_box.delete(0, tk.END)
        for musique in self.liste_de_musique:
            titre, artiste = self.extraire_metadata(musique)
            self.liste_box.insert(tk.END, f"{artiste} - {titre}")

    def maj_liste_combobox(self):
        playlists = list(self.playlists.keys())
        self.playlist_combobox["values"] = playlists
        if playlists:
            self.selected_playlist.set(playlists[0])
        else:
            self.selected_playlist.set("")

    def extraire_metadata(self, chemin_fichier):
        try:
            if chemin_fichier.lower().endswith('.mp3'):
                audio = EasyID3(chemin_fichier)
                titre = audio.get('title', [''])[0]
                artiste = audio.get('artist', [''])[0]
            elif chemin_fichier.lower().endswith('.flac'):
                audio = FLAC(chemin_fichier)
                titre = audio.get('title', [''])[0]
                artiste = audio.get('artist', [''])[0]
            else:
                titre, artiste = '', ''
        except Exception as e:
            print(f"Erreur lors de l'extraction des métadonnées de {chemin_fichier}: {e}")
            titre, artiste = '', ''
        return titre, artiste

if __name__ == "__main__":
    root = tk.Tk()
    app = GestionnaireBibliothequeMusicale(root)
    root.mainloop()
