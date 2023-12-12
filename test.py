import unittest
from unittest.mock import patch
from io import StringIO
import os
import tempfile
import tkinter as tk

from main import GestionnaireBibliothequeMusicale, Musique, Playlist


class TestGestionnaireBibliothequeMusicale(unittest.TestCase):

    def setUp(self):
        self.app = GestionnaireBibliothequeMusicale()

    def test_ajouter_musique(self):
        # Utiliser un fichier temporaire pour simuler la sélection de fichiers
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
            temp_file_path = temp_file.name

        with patch("tkinter.filedialog.askopenfilenames", return_value=[temp_file_path]):
            initial_length = len(self.app.liste_de_musique)
            self.app.ajouter_musique()
            self.assertEqual(len(self.app.liste_de_musique), initial_length + 1)

        # Nettoyer le fichier temporaire
        os.remove(temp_file_path)

    def test_creer_playlist(self):
        with patch("tkinter.simpledialog.askstring", return_value="NouvellePlaylist"):
            initial_length = len(self.app.playlists)
            self.app.creer_playlist()
            self.assertEqual(len(self.app.playlists), initial_length + 1)

    def test_exporter_csv(self):
        # Utiliser un fichier temporaire pour simuler la sélection de l'emplacement de sauvegarde
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as temp_file:
            temp_file_path = temp_file.name

        with patch("tkinter.filedialog.asksaveasfilename", return_value=temp_file_path):
            # Vérifier si le fichier CSV est créé
            self.app.exporter_csv()
            self.assertTrue(os.path.exists(temp_file_path))

            # Vérifier le contenu du fichier CSV
            with open(temp_file_path, "r", encoding="utf-8") as file:
                lines = file.readlines()
                # Vérifier que chaque en-tête est présent dans le fichier
                self.assertIn("Artiste", lines[0])
                self.assertIn("Titre", lines[0])
                self.assertIn("Playlist", lines[0])

                # Vérifier que chaque ligne suivante commence par des guillemets et contient au moins un caractère
                for line in lines[1:]:
                    self.assertTrue(line.startswith('"'))
                    self.assertTrue(len(line) > 1)

        # Nettoyer le fichier temporaire
        os.remove(temp_file_path)


    def test_supprimer_playlist(self):
        # Créer une playlist pour le test
        self.app.playlists["TestPlaylist"] = Playlist("TestPlaylist")
        
        # Sélectionner la playlist créée
        self.app.selected_playlist.set("TestPlaylist")
        
        initial_length = len(self.app.playlists)
        
        # Supprimer la playlist
        self.app.supprimer_playlist()
        
        # Vérifier que la playlist a été supprimée
        self.assertEqual(len(self.app.playlists), initial_length - 1)
        self.assertNotIn("TestPlaylist", self.app.playlists)

    def tearDown(self):
        self.app.destroy()


if __name__ == "__main__":
    unittest.main()
