"""CP4 - Reidentificacao de uma pessoa em videos com cameras diferentes."""
from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np
from ultralytics import YOLO

from Similaridades import similaridade_hsv162, similaridade_orientacoes


@dataclass
class Candidato:
    caixa: tuple[int, int, int, int]
    confianca: float
    cor: float
    orientacao: float

    @property
    def combinada(self) -> float:
        return 0.60 * self.cor + 0.40 * self.orientacao


def pontuar(recorte: np.ndarray, referencia: np.ndarray) -> tuple[float, float]:
    """Calcula as duas caracteristicas com a ordem BGR usada pelo OpenCV."""
    return (
        similaridade_hsv162(recorte, referencia, ordem_cores="BGR"),
        similaridade_orientacoes(recorte, referencia, ordem_cores="BGR"),
    )


def detectar_video(modelo: YOLO, video: Path, referencia: np.ndarray, conf: float):
    captura = cv2.VideoCapture(str(video))
    quadros: list[tuple[np.ndarray, list[Candidato]]] = []
    while True:
        ok, frame = captura.read()
        if not ok:
            break
        resultado = modelo.predict(frame, conf=conf, classes=[0], verbose=False)[0]
        candidatos: list[Candidato] = []
        if resultado.boxes is not None:
            caixas = resultado.boxes.xyxy.cpu().numpy().astype(int)
            confs = resultado.boxes.conf.cpu().numpy()
            h, w = frame.shape[:2]
            for caixa, confianca in zip(caixas, confs):
                x1, y1, x2, y2 = caixa.tolist()
                x1, y1 = max(0, x1), max(0, y1)
                x2, y2 = min(w, x2), min(h, y2)
                if x2 <= x1 or y2 <= y1:
                    continue
                cor, orientacao = pontuar(frame[y1:y2, x1:x2], referencia)
                candidatos.append(Candidato((x1, y1, x2, y2), float(confianca), cor, orientacao))
        quadros.append((frame, candidatos))
    captura.release()
    return quadros


def valor(c: Candidato, metodo: str) -> float:
    return c.cor if metodo == "cor" else c.orientacao if metodo == "orientacao" else c.combinada


def avaliar(quadros, metodo: str, limiar: float) -> dict:
    aceitos, detectados, margens, saltos = 0, 0, [], []
    centro_anterior = None
    for _, candidatos in quadros:
        if not candidatos:
            continue
        detectados += 1
        ordenados = sorted(candidatos, key=lambda c: valor(c, metodo), reverse=True)
        melhor = ordenados[0]
        score = valor(melhor, metodo)
        segundo = valor(ordenados[1], metodo) if len(ordenados) > 1 else max(0.0, score - 0.15)
        margens.append(score - segundo)
        if score >= limiar:
            aceitos += 1
            x1, y1, x2, y2 = melhor.caixa
            centro = ((x1 + x2) / 2, (y1 + y2) / 2)
            if centro_anterior is not None:
                saltos.append(np.hypot(centro[0] - centro_anterior[0], centro[1] - centro_anterior[1]))
            centro_anterior = centro
    cobertura = aceitos / max(1, len(quadros))
    margem = float(np.mean(margens)) if margens else 0.0
    salto = float(np.median(saltos)) if saltos else 999.0
    qualidade = cobertura + 0.8 * margem - 0.00025 * salto
    return {"metodo": metodo, "limiar": limiar, "aceitos": aceitos,
            "frames": len(quadros), "detectados": detectados,
            "cobertura": cobertura, "margem_media": margem,
            "salto_mediano": salto, "qualidade": qualidade}


def escolher_configuracao(quadros):
    resultados = []
    for metodo in ("cor", "orientacao", "combinada"):
        for limiar in np.arange(0.25, 0.76, 0.05):
            resultados.append(avaliar(quadros, metodo, round(float(limiar), 2)))
    viaveis = [r for r in resultados if r["cobertura"] >= 0.35]
    return max(viaveis or resultados, key=lambda r: r["qualidade"]), resultados


def gravar(video_entrada: Path, saida: Path, quadros, config: dict):
    cap = cv2.VideoCapture(str(video_entrada))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    cap.release()
    h, w = quadros[0][0].shape[:2]
    writer = cv2.VideoWriter(str(saida), cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))
    for frame, candidatos in quadros:
        exibicao = frame.copy()
        if candidatos:
            melhor = max(candidatos, key=lambda c: valor(c, config["metodo"]))
            score = valor(melhor, config["metodo"])
            if score >= config["limiar"]:
                x1, y1, x2, y2 = melhor.caixa
                cv2.rectangle(exibicao, (x1, y1), (x2, y2), (0, 0, 255), 3)
                texto = f"Pessoa reidentificada | {config['metodo']} {score:.3f}"
                cv2.putText(exibicao, texto, (x1, max(28, y1 - 10)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 0), 2, cv2.LINE_AA)
        writer.write(exibicao)
    writer.release()


def processar(base: Path, saida: Path, conf: float):
    saida.mkdir(parents=True, exist_ok=True)
    modelo_local = base / "yolo11n.pt"
    # Se o peso nao estiver na pasta, o Ultralytics baixa o YOLO11n
    # automaticamente na primeira execucao.
    modelo = YOLO(str(modelo_local) if modelo_local.exists() else "yolo11n.pt")
    resumo, todos = [], []
    for indice in (1, 2):
        video = base / f"video{indice}.mp4"
        ref = cv2.imread(str(base / f"pessoa-foco_video{indice}.png"))
        if ref is None:
            raise FileNotFoundError(f"Imagem de referencia ausente para video {indice}")
        quadros = detectar_video(modelo, video, ref, conf)
        melhor, resultados = escolher_configuracao(quadros)
        destino = saida / f"video{indice}_reidentificado.mp4"
        gravar(video, destino, quadros, melhor)
        melhor = {"video": video.name, "saida": destino.name, **melhor}
        resumo.append(melhor)
        todos.extend({"video": video.name, **r} for r in resultados)
        print(f"{video.name}: {melhor['metodo']}, limiar={melhor['limiar']:.2f}, "
              f"cobertura={melhor['cobertura']:.1%}")
    with open(saida / "resultados_testes.csv", "w", newline="", encoding="utf-8") as arq:
        escritor = csv.DictWriter(arq, fieldnames=list(todos[0].keys()))
        escritor.writeheader(); escritor.writerows(todos)
    return resumo


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--saida", type=Path, default=Path(__file__).resolve().parent / "entrega")
    parser.add_argument("--confianca", type=float, default=0.25)
    args = parser.parse_args()
    processar(args.base, args.saida, args.confianca)


if __name__ == "__main__":
    main()
