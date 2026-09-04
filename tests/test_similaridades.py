import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from Similaridades import (  # noqa: E402
    similaridade_hsv162,
    similaridade_hsv_orientacao,
    similaridade_orientacoes,
    similaridade_ssim,
)


class TestSimilaridades(unittest.TestCase):
    def setUp(self):
        self.imagem = np.zeros((80, 40, 3), dtype=np.uint8)
        self.imagem[:, :] = (20, 220, 80)
        self.diferente = np.zeros((80, 40, 3), dtype=np.uint8)
        self.diferente[:, :] = (220, 20, 180)

    def test_imagens_identicas_tem_similaridade_maxima(self):
        self.assertAlmostEqual(similaridade_ssim(self.imagem, self.imagem), 1.0, places=6)
        self.assertAlmostEqual(similaridade_hsv162(self.imagem, self.imagem), 1.0, places=6)
        self.assertAlmostEqual(similaridade_orientacoes(self.imagem, self.imagem, "BGR"), 1.0, places=6)

    def test_resultados_permanecem_entre_zero_e_um(self):
        valores = [
            similaridade_ssim(self.imagem, self.diferente),
            similaridade_hsv162(self.imagem, self.diferente),
            similaridade_orientacoes(self.imagem, self.diferente, "BGR"),
            similaridade_hsv_orientacao(self.imagem, self.diferente),
        ]
        for valor in valores:
            self.assertGreaterEqual(valor, 0.0)
            self.assertLessEqual(valor, 1.0)

    def test_cor_diferente_reduz_similaridade_hsv(self):
        self.assertLess(similaridade_hsv162(self.imagem, self.diferente), 0.5)

    def test_entrada_invalida_gera_erro(self):
        with self.assertRaises(ValueError):
            similaridade_hsv162(None, self.imagem)
        with self.assertRaises(ValueError):
            similaridade_hsv_orientacao(self.imagem, self.imagem, peso_cor=1.5)


if __name__ == "__main__":
    unittest.main()
