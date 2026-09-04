from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

BASE = Path(__file__).resolve().parent
DESTINO = BASE / "entrega" / "Relatorio_CP4.pdf"

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="TituloCP", parent=styles["Title"], alignment=TA_CENTER,
                          fontName="Helvetica-Bold", fontSize=18, leading=22,
                          textColor=colors.HexColor("#17324D"), spaceAfter=16))
styles.add(ParagraphStyle(name="SecaoCP", parent=styles["Heading2"], fontSize=12,
                          leading=15, textColor=colors.HexColor("#17324D"), spaceBefore=10,
                          spaceAfter=6))
styles.add(ParagraphStyle(name="CorpoCP", parent=styles["BodyText"], fontSize=9.5,
                          leading=13, spaceAfter=7))
styles.add(ParagraphStyle(name="RodapeCP", parent=styles["BodyText"], fontSize=8,
                          leading=10, textColor=colors.HexColor("#4F6475")))

doc = SimpleDocTemplate(str(DESTINO), pagesize=A4, rightMargin=1.7*cm,
                        leftMargin=1.7*cm, topMargin=1.5*cm, bottomMargin=1.5*cm,
                        title="Relatorio CP4 - Reidentificacao de Pessoas")
story = [
    Paragraph("Checkpoint 4 - Reidentificacao de Pessoas", styles["TituloCP"]),
    Paragraph("Visao Computacional Aplicada | Analise dos videos 1 e 2", styles["CorpoCP"]),
    Paragraph("Integrante: Guilherme Santos", styles["CorpoCP"]),
    Paragraph("1. Objetivo", styles["SecaoCP"]),
    Paragraph("Adaptar o detector YOLO11 para localizar pessoas em cada quadro e reidentificar a pessoa de interesse em duas gravacoes feitas com perspectivas diferentes. Foram avaliadas similaridade de cor, orientacao de gradientes e a combinacao ponderada das duas medidas.", styles["CorpoCP"]),
    Paragraph("2. Metodologia", styles["SecaoCP"]),
    Paragraph("O YOLO11n detectou somente a classe pessoa, com confianca minima de 0,25. Para cada caixa detectada, o recorte foi comparado com a imagem de referencia. A cor foi representada por histograma HSV com 162 posicoes; a orientacao, por histograma de gradientes com 18 intervalos; e a medida combinada utilizou 60% de cor e 40% de orientacao. Foram testados limiares de similaridade de 0,25 a 0,75, em passos de 0,05.", styles["CorpoCP"]),
    Paragraph("3. Resultados", styles["SecaoCP"]),
]

dados = [
    ["Video", "Metodo", "Limiar", "Quadros aceitos", "Cobertura", "Margem media"],
    ["1", "Cor", "0,25", "475 / 482", "98,5%", "0,131"],
    ["1", "Orientacao", "0,25", "475 / 482", "98,5%", "0,109"],
    ["1", "Combinada", "0,25", "475 / 482", "98,5%", "0,118"],
    ["2", "Cor", "0,25", "440 / 440", "100,0%", "0,077"],
    ["2", "Orientacao", "0,25", "440 / 440", "100,0%", "0,060"],
    ["2", "Combinada", "0,25", "440 / 440", "100,0%", "0,068"],
]
tabela = Table(dados, colWidths=[1.25*cm, 2.45*cm, 1.45*cm, 3.0*cm, 2.0*cm, 2.55*cm], repeatRows=1)
tabela.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#17324D")),
    ("TEXTCOLOR", (0,0), (-1,0), colors.white),
    ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
    ("FONTNAME", (0,1), (-1,-1), "Helvetica"),
    ("FONTSIZE", (0,0), (-1,-1), 8),
    ("ALIGN", (0,0), (-1,-1), "CENTER"),
    ("GRID", (0,0), (-1,-1), 0.4, colors.HexColor("#AAB7C4")),
    ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#EEF3F7")]),
    ("TOPPADDING", (0,0), (-1,-1), 6), ("BOTTOMPADDING", (0,0), (-1,-1), 6),
]))
story += [tabela, Spacer(1, 8),
    Paragraph("A margem media indica quanto a melhor pessoa se separou da segunda melhor candidata. Nos dois videos, a comparacao por cor apresentou a maior margem e foi escolhida para os videos finais. A cobertura de 98,5% no video 1 corresponde aos quadros em que o YOLO encontrou uma pessoa; nos quadros iniciais, o alvo ainda nao estava visivel. No video 2, houve deteccao e reidentificacao em todos os 440 quadros.", styles["CorpoCP"]),
    Paragraph("4. Analise do desempenho", styles["SecaoCP"]),
    Paragraph("O metodo de cor foi o mais discriminativo porque as roupas das pessoas possuem distribuicoes cromaticas distintas: camiseta amarela no primeiro video e camiseta cinza escura no segundo. A orientacao isolada tambem manteve boa continuidade, mas apresentou menor separacao entre candidatos, pois contornos de corpos e roupas podem ser semelhantes. A combinacao reduziu parte da vantagem da cor nestas cenas, embora seja uma opcao mais robusta quando pessoas usam cores parecidas.", styles["CorpoCP"]),
    Paragraph("As principais limitacoes sao variacoes de iluminacao, oclusoes, mudanca brusca de escala e roupas visualmente semelhantes. A metodologia nao usa reconhecimento facial nem um modelo profundo especifico de reidentificacao; portanto, identifica a aparencia fornecida como referencia, e nao a identidade civil da pessoa.", styles["CorpoCP"]),
    Paragraph("5. Conclusao", styles["SecaoCP"]),
    Paragraph("A solucao cumpriu o objetivo nos dois cenarios. A configuracao final utilizou YOLO11n com confianca minima de 0,25, similaridade de cor HSV162 e limiar de 0,25. Os videos de saida exibem somente a caixa da pessoa mais semelhante a referencia e informam o valor calculado em cada quadro.", styles["CorpoCP"]),
    Spacer(1, 8),
    Paragraph("Arquivos de apoio: resultados_testes.csv contem as 66 combinacoes avaliadas (3 metodos x 11 limiares x 2 videos).", styles["RodapeCP"]),
]

doc.build(story)
print(DESTINO)
