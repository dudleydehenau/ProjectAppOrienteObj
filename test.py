import unittest
from unittest.mock import patch
from io import StringIO
import os
import tempfile
import tkinter as tk

from main import GestionnaireBibliothequeMusicale

class TestGestionnaireBibliothequeMusicale(unittest.TestCase):

    def setUp(self):
        self.root = tk.Tk()
        self.app = GestionnaireBibliothequeMusicale(self.root)

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
                content = file.read()
                self.assertIn("Artiste,Titre,Playlist", content)

        # Nettoyer le fichier temporaire
        os.remove(temp_file_path)

    def tearDown(self):
        self.root.destroy()

if __name__ == "__main__":
    unittest.main()
