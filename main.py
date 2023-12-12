import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
from tkinter import ttk
import csv
from mutagen.easyid3 import EasyID3
from mutagen.flac import FLAC


class Musique:
    def __init__(self, chemin_fichier):
        self.__chemin_fichier = chemin_fichier
        self.__titre, self.__artiste = self.extraire_metadata()

    def extraire_metadata(self) -> tuple:
        try:
            if self.__chemin_fichier.lower().endswith('.mp3'):
                audio = EasyID3(self.__chemin_fichier)
            elif self.__chemin_fichier.lower().endswith('.flac'):
                audio = FLAC(self.__chemin_fichier)
            else:
                return '', ''

            titre = audio.get('title', [''])[0]
            artiste = audio.get('artist', [''])[0]

        except Exception as e:
            print(f"Erreur lors de l'extraction des métadonnées de {self.__chemin_fichier}: {e}")
            titre, artiste = '', ''

        return titre, artiste

    # Getter pour le chemin_fichier
    def get_chemin_fichier(self):
        return self.__chemin_fichier

    # Getter pour le titre
    def get_titre(self):
        return self.__titre

    # Getter pour l'artiste
    def get_artiste(self):
        return self.__artiste

    # Setter pour le titre
    def set_titre(self, nouveau_titre):
        self.__titre = nouveau_titre

    # Setter pour l'artiste
    def set_artiste(self, nouvel_artiste):
        self.__artiste = nouvel_artiste


class Playlist:
    def __init__(self, nom):
        self.__nom = nom
        self.__musiques = []

    # Getter pour le nom
    def get_nom(self):
        return self.__nom

    # Getter pour les musiques
    def get_musiques(self):
        return self.__musiques

    def ajouter_musique(self, musique: Musique):
        self.__musiques.append(musique)

    def afficher_contenu(self):
        return "\n".join([f"{musique.get_artiste()} - {musique.get_titre()}" for musique in self.__musiques])

    # Setter pour le nom
    def set_nom(self, nouveau_nom):
        self.__nom = nouveau_nom


class GestionnaireBibliothequeMusicale(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("DeesMusic")
        self.geometry("800x600")

        self.liste_de_musique = []
        self.playlists = {}
        self.selected_playlist = tk.StringVar()

        self.menu_bar = tk.Menu(self)

        self.menu_fichier = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_fichier.add_command(label="Ajouter des fichiers musicaux", command=self.ajouter_musique)
        self.menu_fichier.add_command(label="Exporter en CSV", command=self.exporter_csv)
        self.menu_fichier.add_separator()
        self.menu_fichier.add_command(label="Quitter", command=self.destroy)
        self.menu_bar.add_cascade(label="Fichier", menu=self.menu_fichier)

        self.menu_playlist = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_playlist.add_command(label="Créer une playlist", command=self.creer_playlist)
        self.menu_playlist.add_command(label="Ajouter à la playlist", command=self.ajouter_a_playlist)
        self.menu_playlist.add_command(label="Afficher la playlist", command=self.afficher_playlist)
        self.menu_playlist.add_separator()
        self.menu_playlist.add_command(label="Supprimer la playlist", command=self.supprimer_playlist)
        self.menu_bar.add_cascade(label="Playlist", menu=self.menu_playlist)

        self.config(menu=self.menu_bar)

        self.frame = ttk.Frame(self, style="TFrame")
        self.frame.pack(padx=20, pady=20)

        self.liste_box = tk.Listbox(self.frame, bd=0, selectbackground="#FFD700", height=20, width=50)
        self.liste_box.pack(pady=10)

        self.playlist_combobox = ttk.Combobox(self.frame, textvariable=self.selected_playlist, state="readonly")
        self.playlist_combobox.pack(pady=10)

        self.maj_liste_box()

        # Ajout de la liaison de raccourci clavier Ctrl+S pour l'exportation en CSV
        self.bind("<Control-s>", lambda event: self.exporter_csv())

    def ajouter_musique(self) -> None:
        """
        Ajoute des fichiers musicaux à la bibliothèque.

        PRE : Aucune.
        POST : La liste_de_musique est mise à jour avec les fichiers sélectionnés.
        RAISE : Aucune exception n'est levée en cas de succès.
        """
        fichiers = filedialog.askopenfilenames(
            title="Sélectionnez des fichiers musicaux",
            filetypes=[("Fichiers audio", "*.mp3;*.wav;*.flac")],
        )
        if fichiers:
            musiques = [Musique(fichier) for fichier in fichiers]
            self.liste_de_musique.extend(musiques)
            self.maj_liste_box()

    def creer_playlist(self) -> None:
        """
        Crée une nouvelle playlist.

        PRE : Le nom de la playlist ne doit pas être vide.
        POST : Une nouvelle playlist est ajoutée à l'attribut playlists.
        RAISE : ValueError est levé si le nom de la playlist est vide.
        """
        nom_playlist = simpledialog.askstring("Créer une playlist", "Entrez le nom de la playlist:")
        if nom_playlist:
            self.playlists[nom_playlist] = Playlist(nom_playlist)
            self.maj_liste_combobox()

    def ajouter_a_playlist(self) -> None:
        """
        Ajoute des fichiers à une playlist existante.

        PRE : La playlist sélectionnée doit exister dans l'attribut playlists.
                Les fichiers sélectionnés doivent être au format MP3, WAV ou FLAC.
        POST : La playlist est mise à jour avec les nouveaux fichiers.
        RAISE : KeyError est levé si la playlist sélectionnée n'existe pas.
                ValueError est levé si des fichiers invalides sont sélectionnés.
        """
        selected_playlist = self.selected_playlist.get()
        try:
            if selected_playlist in self.playlists:
                selected_files = filedialog.askopenfilenames(
                    title=f"Sélectionnez des fichiers pour {selected_playlist}",
                    filetypes=[("Fichiers audio", "*.mp3;*.wav;*.flac")],
                )
                if selected_files:
                    musiques = [Musique(fichier) for fichier in selected_files]
                    self.playlists[selected_playlist].get_musiques().extend(musiques)
                    self.maj_liste_box()
            else:
                raise KeyError(f"La playlist sélectionnée '{selected_playlist}' n'existe pas.")
        except KeyError as e:
            messagebox.showerror("Erreur", str(e))

    def afficher_playlist(self) -> None:
        """
        Affiche le contenu d'une playlist.

        PRE : La playlist sélectionnée doit exister dans l'attribut playlists.
        POST : Une boîte de dialogue affiche le contenu de la playlist.
        RAISE : KeyError est levé si la playlist sélectionnée n'existe pas.
        """
        selected_playlist = self.selected_playlist.get()
        if selected_playlist in self.playlists:
            playlist_content = self.playlists[selected_playlist].afficher_contenu()
            messagebox.showinfo(f"Contenu de {selected_playlist}", playlist_content)
        else:
            messagebox.showwarning("Playlist non trouvée", f"La playlist '{selected_playlist}' n'existe pas.")

    def maj_liste_box(self) -> None:
        self.liste_box.delete(0, tk.END)

        # Ajouter les fichiers de la liste principale
        for musique in self.liste_de_musique:
            self.liste_box.insert(tk.END, f"{musique.get_artiste()} - {musique.get_titre()}")

        # Ajouter les fichiers de toutes les playlists
        for playlist in self.playlists.values():
            for musique in playlist.get_musiques():
                self.liste_box.insert(tk.END, f"{musique.get_artiste()} - {musique.get_titre()} (Playlist: {playlist.get_nom()})")

    def maj_liste_combobox(self) -> None:
        playlists = list(self.playlists.keys())
        self.playlist_combobox["values"] = playlists
        if playlists:
            self.selected_playlist.set(playlists[0])
        else:
            self.selected_playlist.set("")

    def extraire_metadata(self, chemin_fichier: str) -> tuple:
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

    def supprimer_musique(self) -> None:
        selected_indices = self.liste_box.curselection()
        if selected_indices:
            for index in sorted(selected_indices, reverse=True):
                del self.liste_de_musique[index]
            self.maj_liste_box()

    def vider_liste_de_lecture(self) -> None:
        self.liste_de_musique = []
        self.maj_liste_box()

    def supprimer_playlist(self) -> None:
        """
        Supprime une playlist.

        PRE : La playlist sélectionnée doit exister dans l'attribut playlists.
        POST : La playlist est supprimée de l'attribut playlists.
        RAISE : KeyError est levé si la playlist sélectionnée n'existe pas.
        """
        selected_playlist = self.selected_playlist.get()
        try:
            if selected_playlist in self.playlists:
                del self.playlists[selected_playlist]
                self.maj_liste_combobox()
            else:
                raise KeyError(f"La playlist sélectionnée '{selected_playlist}' n'existe pas.")
        except KeyError as e:
            messagebox.showerror("Erreur", str(e))

    def exporter_csv(self) -> None:
        nom_fichier = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("Fichiers CSV", "*.csv")],
        )
        if nom_fichier:
            with open(nom_fichier, mode='w', newline='', encoding='utf-8') as fichier_csv:
                writer = csv.writer(fichier_csv)
                writer.writerow(["Artiste", "Titre", "Playlist"])

                # Ajouter les fichiers de la liste principale
                for musique in self.liste_de_musique:
                    writer.writerow([musique.get_artiste(), musique.get_titre(), ""])

                # Ajouter les fichiers de toutes les playlists
                for playlist in self.playlists.values():
                    for musique in playlist.get_musiques():
                        writer.writerow([musique.get_artiste(), musique.get_titre(), playlist.get_nom()])


if __name__ == "__main__":
    app = GestionnaireBibliothequeMusicale()
    app.mainloop()
