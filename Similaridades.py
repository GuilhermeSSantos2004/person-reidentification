import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim


TAMANHO_COMPARACAO_SSIM = (64, 64)


def similaridade_ssim(imagem_rgb_1, imagem_rgb_2):
    """
    Compara duas imagens coloridas usando o índice SSIM multicanal.

    As imagens podem possuir tamanhos diferentes. Ambas são ajustadas
    para 64 x 64 pixels antes da comparação.

    Retorno:
        Valor entre 0 e 1:
            0 = imagens totalmente diferentes;
            1 = imagens idênticas.
    """

    if imagem_rgb_1 is None or imagem_rgb_2 is None:
        raise ValueError("Uma ou ambas as imagens são inválidas.")

    if (
        imagem_rgb_1.ndim != 3
        or imagem_rgb_1.shape[2] != 3
        or imagem_rgb_2.ndim != 3
        or imagem_rgb_2.shape[2] != 3
    ):
        raise ValueError("As imagens devem possuir três canais de cor.")

    imagem_rgb_1_ajustada = cv2.resize(
        imagem_rgb_1,
        TAMANHO_COMPARACAO_SSIM,
        interpolation=cv2.INTER_AREA
    )

    imagem_rgb_2_ajustada = cv2.resize(
        imagem_rgb_2,
        TAMANHO_COMPARACAO_SSIM,
        interpolation=cv2.INTER_AREA
    )

    similaridade = ssim(
        imagem_rgb_1_ajustada,
        imagem_rgb_2_ajustada,
        channel_axis=2,
        data_range=255
    )

    similaridade = np.clip(
        similaridade,
        0.0,
        1.0
    )

    return float(similaridade)


def similaridade_hsv162(
    imagem_1,
    imagem_2,
    ordem_cores="BGR"
):
    """
    Compara duas imagens usando histogramas HSV162.

    Quantização:
        H: 18 valores, de 0 a 17;
        S:  3 valores, de 0 a 2;
        V:  3 valores, de 0 a 2.

    Retorna uma similaridade entre 0 e 1.
    """

    if imagem_1 is None or imagem_2 is None:
        raise ValueError(
            "Uma ou ambas as imagens são inválidas."
        )

    if (
        imagem_1.ndim != 3
        or imagem_1.shape[2] != 3
        or imagem_2.ndim != 3
        or imagem_2.shape[2] != 3
    ):
        raise ValueError(
            "As imagens devem possuir três canais."
        )

    ordem_cores = ordem_cores.upper()

    if ordem_cores == "BGR":
        codigo_conversao = cv2.COLOR_BGR2HSV

    elif ordem_cores == "RGB":
        codigo_conversao = cv2.COLOR_RGB2HSV

    else:
        raise ValueError(
            "ordem_cores deve ser 'BGR' ou 'RGB'."
        )

    # Converte as duas imagens para HSV
    imagem_hsv_1 = cv2.cvtColor(
        imagem_1,
        codigo_conversao
    )

    imagem_hsv_2 = cv2.cvtColor(
        imagem_2,
        codigo_conversao
    )

    # Separa os canais da primeira imagem
    h1 = imagem_hsv_1[:, :, 0].astype(np.int32)
    s1 = imagem_hsv_1[:, :, 1].astype(np.int32)
    v1 = imagem_hsv_1[:, :, 2].astype(np.int32)

    # Separa os canais da segunda imagem
    h2 = imagem_hsv_2[:, :, 0].astype(np.int32)
    s2 = imagem_hsv_2[:, :, 1].astype(np.int32)
    v2 = imagem_hsv_2[:, :, 2].astype(np.int32)

    # Quantiza H no intervalo de 0 a 17
    h1_quantizado = h1 // 10
    h2_quantizado = h2 // 10

    # Quantiza S no intervalo de 0 a 2
    s1_quantizado = (s1 * 3) // 256
    s2_quantizado = (s2 * 3) // 256

    # Quantiza V no intervalo de 0 a 2
    v1_quantizado = (v1 * 3) // 256
    v2_quantizado = (v2 * 3) // 256

    # Combina H, S e V em índices entre 0 e 161
    indice_hsv162_1 = (
        h1_quantizado * 9
        + s1_quantizado * 3
        + v1_quantizado
    )

    indice_hsv162_2 = (
        h2_quantizado * 9
        + s2_quantizado * 3
        + v2_quantizado
    )

    # Constrói os histogramas com 162 posições
    histograma_1 = np.bincount(
        indice_hsv162_1.ravel(),
        minlength=162
    ).astype(np.float32)

    histograma_2 = np.bincount(
        indice_hsv162_2.ravel(),
        minlength=162
    ).astype(np.float32)

    # Normaliza os histogramas pela quantidade de pixels
    soma_histograma_1 = histograma_1.sum()
    soma_histograma_2 = histograma_2.sum()

    if soma_histograma_1 > 0:
        histograma_1 /= soma_histograma_1

    if soma_histograma_2 > 0:
        histograma_2 /= soma_histograma_2

    # Compara os histogramas pela distância de Bhattacharyya
    distancia = cv2.compareHist(
        histograma_1,
        histograma_2,
        cv2.HISTCMP_BHATTACHARYYA
    )

    # Converte a distância em similaridade
    similaridade = 1.0 - distancia

    # Garante que o resultado permaneça entre 0 e 1
    similaridade = np.clip(
        similaridade,
        0.0,
        1.0
    )

    return float(similaridade)


def similaridade_orientacoes(
    imagem_1,
    imagem_2,
    ordem_cores="RGB",
    numero_bins=18
):
    """
    Compara duas imagens pelo histograma das orientações dos gradientes.

    Parâmetros:
        imagem_1, imagem_2:
            Imagens coloridas no formato NumPy.

        ordem_cores:
            "RGB" para imagens RGB;
            "BGR" para imagens carregadas com cv2.imread().

        numero_bins:
            Número de divisões do intervalo de 0 a 180 graus.
            Com 18 bins, cada bin representa 10 graus.

    Retorno:
        Similaridade entre 0 e 1:
            0 = histogramas totalmente diferentes;
            1 = histogramas idênticos.
    """

    if imagem_1 is None or imagem_2 is None:
        raise ValueError(
            "Uma ou ambas as imagens são inválidas."
        )

    if (
        imagem_1.ndim != 3
        or imagem_1.shape[2] != 3
        or imagem_2.ndim != 3
        or imagem_2.shape[2] != 3
    ):
        raise ValueError(
            "As imagens devem possuir três canais."
        )

    ordem_cores = ordem_cores.upper()

    if ordem_cores == "RGB":
        codigo_cinza = cv2.COLOR_RGB2GRAY

    elif ordem_cores == "BGR":
        codigo_cinza = cv2.COLOR_BGR2GRAY

    else:
        raise ValueError(
            "ordem_cores deve ser 'RGB' ou 'BGR'."
        )

    histogramas = []

    for imagem in (imagem_1, imagem_2):

        # Converte para tons de cinza
        imagem_cinza = cv2.cvtColor(
            imagem,
            codigo_cinza
        )

        # Converte para ponto flutuante
        imagem_cinza = imagem_cinza.astype(
            np.float32
        )

        # Gradiente horizontal
        gradiente_x = cv2.Sobel(
            imagem_cinza,
            cv2.CV_32F,
            1,
            0,
            ksize=3
        )

        # Gradiente vertical
        gradiente_y = cv2.Sobel(
            imagem_cinza,
            cv2.CV_32F,
            0,
            1,
            ksize=3
        )

        # Calcula magnitude e orientação
        magnitude, orientacao = cv2.cartToPolar(
            gradiente_x,
            gradiente_y,
            angleInDegrees=True
        )

        # Converte orientações de 0–360 para 0–180
        orientacao = orientacao % 180.0

        # Constrói o histograma de orientações.
        # Cada orientação é ponderada pela magnitude
        # do gradiente correspondente.
        histograma, _ = np.histogram(
            orientacao,
            bins=numero_bins,
            range=(0.0, 180.0),
            weights=magnitude
        )

        histograma = histograma.astype(
            np.float32
        )

        # Normaliza o histograma pela soma
        soma_histograma = histograma.sum()

        if soma_histograma > 0:
            histograma /= soma_histograma

        histogramas.append(histograma)

    histograma_1 = histogramas[0]
    histograma_2 = histogramas[1]

    soma_1 = histograma_1.sum()
    soma_2 = histograma_2.sum()

    # As duas imagens não possuem gradientes
    if soma_1 == 0 and soma_2 == 0:
        return 1.0

    # Somente uma imagem não possui gradientes
    if soma_1 == 0 or soma_2 == 0:
        return 0.0

    # Distância de Bhattacharyya:
    # 0 = histogramas idênticos;
    # 1 = histogramas totalmente diferentes.
    distancia = cv2.compareHist(
        histograma_1,
        histograma_2,
        cv2.HISTCMP_BHATTACHARYYA
    )

    # Converte distância em similaridade
    similaridade = 1.0 - distancia

    # Garante que o resultado esteja entre 0 e 1
    similaridade = np.clip(
        similaridade,
        0.0,
        1.0
    )

    return float(similaridade)



def similaridade_hsv_orientacao(
    imagem_1,
    imagem_2,
    ordem_cores="BGR",
    peso_cor=0.60
):
    """
    Compara duas imagens RGB combinando:

        1. Similaridade do histograma HSV162;
        2. Similaridade do histograma de orientações.

    A similaridade final é a média aritmética das duas.

    Retorno:
        Valor entre 0 e 1.
    """

    if imagem_1 is None or imagem_2 is None:
        raise ValueError(
            "Uma ou ambas as imagens são inválidas."
        )

    if not 0.0 <= peso_cor <= 1.0:
        raise ValueError("peso_cor deve estar entre 0 e 1.")

    similaridade_hsv = similaridade_hsv162(
        imagem_1,
        imagem_2,
        ordem_cores=ordem_cores
    )

    similaridade_orientacao = similaridade_orientacoes(
        imagem_1,
        imagem_2,
        ordem_cores=ordem_cores
    )

    similaridade_media = (
        peso_cor * similaridade_hsv
        + (1.0 - peso_cor) * similaridade_orientacao
    )

    return float(similaridade_media)
