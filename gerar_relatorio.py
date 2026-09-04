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
                          leading=14, textColor=colors.HexColor("#17324D"), spaceBefore=7,
                          spaceAfter=4))
styles.add(ParagraphStyle(name="CorpoCP", parent=styles["BodyText"], fontSize=8.8,
                          leading=11.5, spaceAfter=5))
styles.add(ParagraphStyle(name="RodapeCP", parent=styles["BodyText"], fontSize=8,
                          leading=10, textColor=colors.HexColor("#4F6475")))

doc = SimpleDocTemplate(str(DESTINO), pagesize=A4, rightMargin=1.7*cm,
                        leftMargin=1.7*cm, topMargin=1.5*cm, bottomMargin=1.5*cm,
                        title="Relatorio CP4 - Reidentificacao de Pessoas")
story = [
    Paragraph("Checkpoint 4 - Reidentificacao de Pessoas", styles["TituloCP"]),
    Paragraph("Visao Computacional Aplicada | Analise dos videos 1 e 2", styles["CorpoCP"]),
    Paragraph("Integrantes do grupo", styles["SecaoCP"]),
    Table([
        ["Enricco Rossi de Souza Carvalho Miranda - RM551717",
         "Gabriel Marquez Trevisan - RM99227"],
        ["Guilherme Silva dos Santos - RM551168",
         "Danilo Urze Aldred - RM99465"],
        ["Laura Claro Mathias - RM98747", ""],
    ], colWidths=[8.1*cm, 8.1*cm], style=TableStyle([
        ("FONTNAME", (0,0), (-1,-1), "Helvetica"),
        ("FONTSIZE", (0,0), (-1,-1), 7.5),
        ("TEXTCOLOR", (0,0), (-1,-1), colors.HexColor("#243746")),
        ("BACKGROUND", (0,0), (-1,-1), colors.HexColor("#EEF3F7")),
        ("BOX", (0,0), (-1,-1), 0.4, colors.HexColor("#AAB7C4")),
        ("INNERGRID", (0,0), (-1,-1), 0.25, colors.HexColor("#C5CFD8")),
        ("LEFTPADDING", (0,0), (-1,-1), 5),
        ("RIGHTPADDING", (0,0), (-1,-1), 5),
        ("TOPPADDING", (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
    ])),
    Paragraph("1. Objetivo", styles["SecaoCP"]),
    Paragraph("Adaptar o detector YOLO11 para localizar pessoas em cada quadro e reidentificar a pessoa de interesse em duas gravacoes feitas com perspectivas diferentes. Foram avaliadas similaridade de cor, orientacao de gradientes e a combinacao ponderada das duas medidas.", styles["CorpoCP"]),
    Paragraph("2. Metodologia", styles["SecaoCP"]),
    Paragraph("O YOLO11n detectou somente a classe pessoa. Foram avaliadas confiancas minimas de 0,15, 0,25, 0,35 e 0,45. Para cada caixa, o recorte foi comparado com a referencia. A cor foi representada por histograma HSV com 162 posicoes; a orientacao, por histograma de gradientes com 18 intervalos; e a medida combinada utilizou 60% de cor e 40% de orientacao. Tambem foram testados limiares de similaridade de 0,25 a 0,75, em passos de 0,05.", styles["CorpoCP"]),
    Paragraph("3. Resultados", styles["SecaoCP"]),
]

dados = [
    ["Video", "Metodo", "Conf.", "Limiar", "Aceitos", "Cobertura", "Margem"],
    ["1", "Cor", "0,15", "0,25", "475 / 482", "98,5%", "0,145"],
    ["1", "Orientacao", "0,45", "0,25", "474 / 482", "98,3%", "0,114"],
    ["1", "Combinada", "0,15", "0,25", "478 / 482", "99,2%", "0,122"],
    ["2", "Cor", "0,45", "0,25", "440 / 440", "100,0%", "0,079"],
    ["2", "Orientacao", "0,45", "0,25", "440 / 440", "100,0%", "0,061"],
    ["2", "Combinada", "0,45", "0,25", "440 / 440", "100,0%", "0,069"],
]
tabela = Table(dados, colWidths=[1.2*cm, 3.0*cm, 1.8*cm, 1.8*cm, 3.0*cm, 2.5*cm, 2.5*cm], repeatRows=1)
tabela.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#17324D")),
    ("TEXTCOLOR", (0,0), (-1,0), colors.white),
    ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
    ("FONTNAME", (0,1), (-1,-1), "Helvetica"),
    ("FONTSIZE", (0,0), (-1,-1), 8),
    ("ALIGN", (0,0), (-1,-1), "CENTER"),
    ("GRID", (0,0), (-1,-1), 0.4, colors.HexColor("#AAB7C4")),
    ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#EEF3F7")]),
    ("TOPPADDING", (0,0), (-1,-1), 4), ("BOTTOMPADDING", (0,0), (-1,-1), 4),
]))
story += [tabela, Spacer(1, 8),
    Paragraph("A margem media indica quanto a melhor pessoa se separou da segunda melhor candidata. Nos dois videos, a comparacao por cor apresentou a maior margem e foi escolhida para os videos finais. A melhor confianca foi 0,15 no video 1 e 0,45 no video 2. A cobertura de 98,5% no video 1 corresponde aos quadros em que o alvo estava detectavel; no video 2, houve reidentificacao nos 440 quadros.", styles["CorpoCP"]),
    Paragraph("4. Analise do desempenho", styles["SecaoCP"]),
    Paragraph("O metodo de cor foi o mais discriminativo porque as roupas das pessoas possuem distribuicoes cromaticas distintas: camiseta amarela no primeiro video e camiseta cinza escura no segundo. A orientacao isolada tambem manteve boa continuidade, mas apresentou menor separacao entre candidatos, pois contornos de corpos e roupas podem ser semelhantes. A combinacao reduziu parte da vantagem da cor nestas cenas, embora seja uma opcao mais robusta quando pessoas usam cores parecidas.", styles["CorpoCP"]),
    Paragraph("As principais limitacoes sao variacoes de iluminacao, oclusoes, mudanca brusca de escala e roupas visualmente semelhantes. A metodologia nao usa reconhecimento facial nem um modelo profundo especifico de reidentificacao; portanto, identifica a aparencia fornecida como referencia, e nao a identidade civil da pessoa.", styles["CorpoCP"]),
    Paragraph("5. Conclusao", styles["SecaoCP"]),
    Paragraph("A solucao cumpriu o objetivo nos dois cenarios. A configuracao final utilizou YOLO11n, similaridade de cor HSV162, limiar de 0,25 e confiancas de 0,15 no video 1 e 0,45 no video 2. Os videos de saida exibem somente a caixa da pessoa mais semelhante a referencia e informam o valor calculado em cada quadro.", styles["CorpoCP"]),
    Spacer(1, 8),
    Paragraph("Arquivos de apoio: resultados_testes.csv contem as 264 combinacoes avaliadas (3 metodos x 4 confiancas x 11 limiares x 2 videos).", styles["RodapeCP"]),
]

doc.build(story)
print(DESTINO)
