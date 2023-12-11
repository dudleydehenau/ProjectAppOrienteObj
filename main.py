import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
from tkinter import ttk
import csv
from mutagen.easyid3 import EasyID3
from mutagen.flac import FLAC

class GestionnaireBibliothequeMusicale:
    def __init__(self, root):
        self.root = root
        self.root.title("DeesMusic")
        self.root.geometry("800x600")

        self.liste_de_musique = []
        self.playlists = {}
        self.selected_playlist = tk.StringVar()

        self.menu_bar = tk.Menu(root)

        self.menu_fichier = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_fichier.add_command(label="Ajouter des fichiers musicaux", command=self.ajouter_musique)
        self.menu_fichier.add_command(label="Exporter en CSV", command=self.exporter_csv)
        self.menu_fichier.add_separator()
        self.menu_fichier.add_command(label="Quitter", command=root.destroy)
        self.menu_bar.add_cascade(label="Fichier", menu=self.menu_fichier)

        self.menu_playlist = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_playlist.add_command(label="Créer une playlist", command=self.creer_playlist)
        self.menu_playlist.add_command(label="Ajouter à la playlist", command=self.ajouter_a_playlist)
        self.menu_playlist.add_command(label="Afficher la playlist", command=self.afficher_playlist)
        self.menu_playlist.add_separator()
        self.menu_playlist.add_command(label="Supprimer la playlist", command=self.supprimer_playlist)
        self.menu_bar.add_cascade(label="Playlist", menu=self.menu_playlist)

        root.config(menu=self.menu_bar)

        self.frame = ttk.Frame(root, style="TFrame")
        self.frame.pack(padx=20, pady=20)

        self.liste_box = tk.Listbox(self.frame, bd=0, selectbackground="#FFD700", height=20, width=50)
        self.liste_box.pack(pady=10)

        self.playlist_combobox = ttk.Combobox(self.frame, textvariable=self.selected_playlist, state="readonly")
        self.playlist_combobox.pack(pady=10)

        self.maj_liste_box()

        # Ajout de la liaison de raccourci clavier Ctrl+S pour l'exportation en CSV
        root.bind("<Control-s>", lambda event: self.exporter_csv())

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
            self.maj_liste_box()

    def afficher_playlist(self):
        selected_playlist = self.selected_playlist.get()
        if selected_playlist in self.playlists:
            playlist_content = "\n".join(self.playlists[selected_playlist])
            messagebox.showinfo(f"Contenu de {selected_playlist}", playlist_content)
        else:
            messagebox.showwarning("Playlist non trouvée", f"La playlist '{selected_playlist}' n'existe pas.")

    def maj_liste_box(self):
        self.liste_box.delete(0, tk.END)
        
        # Ajouter les fichiers de la liste principale
        for musique in self.liste_de_musique:
            titre, artiste = self.extraire_metadata(musique)
            self.liste_box.insert(tk.END, f"{artiste} - {titre}")

        # Ajouter les fichiers de toutes les playlists
        for playlist, musiques in self.playlists.items():
            for musique in musiques:
                titre, artiste = self.extraire_metadata(musique)
                self.liste_box.insert(tk.END, f"{artiste} - {titre} (Playlist: {playlist})")

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

    def supprimer_musique(self):
        selected_indices = self.liste_box.curselection()
        if selected_indices:
            for index in sorted(selected_indices, reverse=True):
                del self.liste_de_musique[index]
            self.maj_liste_box()

    def vider_liste_de_lecture(self):
        self.liste_de_musique = []
        self.maj_liste_box()

    def supprimer_playlist(self):
        selected_playlist = self.selected_playlist.get()
        if selected_playlist in self.playlists:
            del self.playlists[selected_playlist]
            self.maj_liste_combobox()

    def exporter_csv(self):
        nom_fichier = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("Fichiers CSV", "*.csv")])
        if nom_fichier:
            with open(nom_fichier, mode='w', newline='', encoding='utf-8') as fichier_csv:
                writer = csv.writer(fichier_csv)
                writer.writerow(["Artiste", "Titre", "Playlist"])
                
                # Ajouter les fichiers de la liste principale
                for musique in self.liste_de_musique:
                    titre, artiste = self.extraire_metadata(musique)
                    writer.writerow([artiste, titre, ""])
                    
                # Ajouter les fichiers de toutes les playlists
                for playlist, musiques in self.playlists.items():
                    for musique in musiques:
                        titre, artiste = self.extraire_metadata(musique)
                        writer.writerow([artiste, titre, playlist])


if __name__ == "__main__":
    root = tk.Tk()
    app = GestionnaireBibliothequeMusicale(root)
    root.mainloop()
