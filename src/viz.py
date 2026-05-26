import csv
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")
OUT  = os.path.join(BASE, "out")
os.makedirs(OUT, exist_ok=True)

def ler_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def ler_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

COR_REGIAO = {
    "Norte":        "#2196F3",
    "Nordeste":     "#FF9800",
    "Centro-Oeste": "#9C27B0",
    "Sudeste":      "#F44336",
    "Sul":          "#4CAF50",
}

def viz1_distribuicao_graus_pizza():
    graus_raw = ler_csv(os.path.join(OUT, "graus.csv"))
    graus = [int(r["grau"]) for r in graus_raw]

    total = len(graus)
    qtd_1 = sum(1 for g in graus if g == 1)
    qtd_2_3 = sum(1 for g in graus if 2 <= g <= 3)
    qtd_4_6 = sum(1 for g in graus if 4 <= g <= 6)
    qtd_hubs = sum(1 for g in graus if g >= 7)

    
    valores_raw = [qtd_1, qtd_2_3, qtd_4_6, qtd_hubs]
    
    labels_raw = [
        f"Periféricos (Grau 1): {qtd_1} aero. ({(qtd_1/total)*100:.1f}%)",
        f"Pequenos (Grau 2-3): {qtd_2_3} aero. ({(qtd_2_3/total)*100:.1f}%)",
        f"Médios (Grau 4-6): {qtd_4_6} aero. ({(qtd_4_6/total)*100:.1f}%)",
        f"Hubs Fortes (Grau 7+): {qtd_hubs} aero. ({(qtd_hubs/total)*100:.1f}%)"
    ]
    
    cores_raw = ["#90CAF9", "#42A5F5", "#1565C0", "#FF6F00"]

    
    valores_desenho = []
    cores_desenho = []

    for v, c in zip(valores_raw, cores_raw):
        if v > 0: 
            valores_desenho.append(v)
            cores_desenho.append(c)

    fig, ax = plt.subplots(figsize=(10, 6))
    fig.patch.set_facecolor("#F8F9FA")

    
    wedges, texts, autotexts = ax.pie(
        valores_desenho, 
        autopct="%1.1f%%",         
        pctdistance=0.75,          
        startangle=140,            
        colors=cores_desenho,
        wedgeprops=dict(width=0.45, edgecolor="white", linewidth=2.5)
    )

    
    for autotext in autotexts:
        autotext.set_fontsize(10)
        autotext.set_fontweight("bold")
        autotext.set_color("white")

    
    elementos_legenda = []
    idx_desenho = 0
    
    for i, v in enumerate(valores_raw):
        if v > 0:
            elementos_legenda.append(wedges[idx_desenho])
            idx_desenho += 1
        else:
            elementos_legenda.append(mpatches.Patch(color=cores_raw[i]))

    # Exibe a legenda lateral
    ax.legend(
        elementos_legenda, 
        labels_raw,
        title="Categorias de Conectividade",
        title_fontsize=11,
        loc="center left",
        bbox_to_anchor=(0.95, 0.5), 
        frameon=False,
        fontsize=10
    )

    ax.set_title("Distribuição de Conectividade da Malha (Graus)", 
                 fontsize=14, fontweight="bold", pad=15, color="#1A1A2E")

    nota = (
        "Insight: A imensa maioria da rede é composta por nós com grau baixo (periféricos).\n"
        "Os Hubs de altíssima conectividade (7+) representam uma parcela nula ou extremamente rara."
    )
    fig.text(0.5, 0.02, nota, ha="center", fontsize=9.5, style="italic", color="#444")

    plt.tight_layout()
    
    path = os.path.join(OUT, "viz1_distribuicao_graus.png")
    plt.savefig(path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close()
    print(f"[OK] {path}")
#Ranking de aeroportos
def viz2_ranking_aeroportos():
    aeroportos_raw = ler_csv(os.path.join(DATA, "aeroportos_data.csv"))
    regiao_map = {r["iata"]: r["regiao"] for r in aeroportos_raw}

    graus_raw = ler_csv(os.path.join(OUT, "graus.csv"))
    graus_raw.sort(key=lambda r: int(r["grau"]), reverse=True)

    labels = [r["aeroporto"] for r in graus_raw]
    values = [int(r["grau"]) for r in graus_raw]
    cores  = [COR_REGIAO.get(regiao_map.get(a, ""), "#888") for a in labels]

    fig, ax = plt.subplots(figsize=(8, 7))
    bars = ax.barh(labels[::-1], values[::-1], color=cores[::-1],
                   edgecolor="white", linewidth=0.6)

    for bar, val in zip(bars, values[::-1]):
        ax.text(bar.get_width() + 0.05, bar.get_y() + bar.get_height() / 2,
                str(val), va="center", ha="left", fontsize=10, fontweight="bold")

    ax.set_title("Ranking de Aeroportos por Conectividade (Grau)", fontsize=14,
                 fontweight="bold", pad=12)
    ax.set_xlabel("Grau (número de conexões)", fontsize=11)
    ax.set_ylabel("Aeroporto (código IATA)", fontsize=11)
    ax.set_xlim(0, max(values) + 1.5)
    ax.grid(axis="x", linestyle="--", alpha=0.4)

    patches_leg = [mpatches.Patch(color=c, label=r) for r, c in COR_REGIAO.items()]
    ax.legend(handles=patches_leg, title="Região", fontsize=9,
              title_fontsize=9, loc="lower right")

    fig.text(0.5, -0.03,
        "Insight: BSB (grau 6) e GRU/FOR/GIG (grau 4) são os grandes hubs da rede.\n"
        "Aeroportos como RBR, GYN e POA têm grau 1 — dependem completamente de escala.",
        ha="center", fontsize=9, style="italic", color="#444")

    plt.tight_layout()
    path = os.path.join(OUT, "viz2_ranking_aeroportos.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"[OK] {path}")

#Comparação de métricas por região 
def viz3_comparacao_regioes():
    regioes = ler_json(os.path.join(OUT, "regioes.json"))

    nomes    = [r["regiao"]    for r in regioes]
    ordens   = [r["ordem"]     for r in regioes]
    tamanhos = [r["tamanho"]   for r in regioes]
    densids  = [r["densidade"] for r in regioes]

    x = np.arange(len(nomes))
    w = 0.28

    fig, ax1 = plt.subplots(figsize=(10, 6))
    ax2 = ax1.twinx()

    b1 = ax1.bar(x - w, ordens,   w, label="Ordem (|V|)",   color="#1976D2", alpha=0.85)
    b2 = ax1.bar(x,     tamanhos, w, label="Tamanho (|E|)", color="#388E3C", alpha=0.85)
    b3 = ax2.bar(x + w, densids,  w, label="Densidade",     color="#F57C00", alpha=0.85)

    ax1.set_title("Comparação de Métricas por Região", fontsize=14,
                  fontweight="bold", pad=12)
    ax1.set_xlabel("Região", fontsize=11)
    ax1.set_ylabel("Quantidade (|V| e |E|)", fontsize=11)
    ax2.set_ylabel("Densidade", fontsize=11, color="#F57C00")
    ax2.set_ylim(0, 1.4)
    ax2.tick_params(axis="y", colors="#F57C00")
    ax1.set_xticks(x)
    ax1.set_xticklabels(nomes, fontsize=10)
    ax1.yaxis.get_major_locator().set_params(integer=True)
    ax1.grid(axis="y", linestyle="--", alpha=0.3)

    for bar in list(b1) + list(b2):
        h = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2, h + 0.05, str(int(h)),
                 ha="center", va="bottom", fontsize=9)
    for bar in b3:
        h = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2, h + 0.02, f"{h:.2f}",
                 ha="center", va="bottom", fontsize=9)

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, fontsize=9, loc="upper right")

    fig.text(0.5, -0.04,
        "Insight: Centro-Oeste tem a maior densidade (1.0) por ser um subgrafo pequeno e completo.\n"
        "Nordeste tem mais nos, mas densidade menor — conexoes poderiam ser expandidas.",
        ha="center", fontsize=9, style="italic", color="#444")

    plt.tight_layout()
    path = os.path.join(OUT, "viz3_comparacao_regioes.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"[OK] {path}")

#Camadas BFS a partir de BSB 
def bfs_camadas(adj, origem):
    visitado = {origem: 0}
    fila = [origem]
    while fila:
        atual = fila.pop(0)
        for vizinho in adj.get(atual, []):
            if vizinho not in visitado:
                visitado[vizinho] = visitado[atual] + 1
                fila.append(vizinho)
    return visitado

def viz4_bfs_camadas():
    adj_raw = ler_csv(os.path.join(DATA, "adjacencias_aeroportos.csv"))
    aeroportos_raw = ler_csv(os.path.join(DATA, "aeroportos_data.csv"))
    regiao_map = {r["iata"]: r["regiao"] for r in aeroportos_raw}

    adj = {}
    for row in adj_raw:
        o, d = row["origem"], row["destino"]
        adj.setdefault(o, []).append(d)
        adj.setdefault(d, []).append(o)

    origem = "BSB"
    niveis = bfs_camadas(adj, origem)

    grupos = {}
    for no, nivel in niveis.items():
        grupos.setdefault(nivel, []).append(no)

    max_nivel = max(grupos.keys())
    n_cols = max(len(v) for v in grupos.values())

    fig, ax = plt.subplots(figsize=(13, 7))
    ax.set_xlim(-0.8, n_cols + 0.8)
    ax.set_ylim(-0.6, max_nivel + 1.0)
    ax.axis("off")

    pos = {}
    for nivel, nos in grupos.items():
        y = max_nivel - nivel
        xs = np.linspace(0.5, n_cols - 0.5, len(nos)) if len(nos) > 1 else [n_cols / 2]
        for no, x in zip(nos, xs):
            pos[no] = (x, y)

    desenhadas = set()
    for row in adj_raw:
        o, d = row["origem"], row["destino"]
        chave = tuple(sorted([o, d]))
        if chave not in desenhadas and o in pos and d in pos:
            desenhadas.add(chave)
            xo, yo = pos[o]
            xd, yd = pos[d]
            ax.plot([xo, xd], [yo, yd], color="#BDBDBD", linewidth=1, zorder=1)

    for no, (x, y) in pos.items():
        regiao = regiao_map.get(no, "")
        cor    = COR_REGIAO.get(regiao, "#888")
        nivel  = niveis[no]
        raio   = 0.38 if nivel == 0 else 0.28
        circulo = plt.Circle((x, y), raio, color=cor, zorder=2, linewidth=1.5,
                             edgecolor="white")
        ax.add_patch(circulo)
        ax.text(x, y, no, ha="center", va="center",
                fontsize=8, fontweight="bold", color="white", zorder=3)

    for nivel in range(max_nivel + 1):
        y = max_nivel - nivel
        label = f"Nível {nivel}" if nivel > 0 else f"Nível {nivel} (origem)"
        ax.text(-0.6, y, label, va="center", ha="right",
                fontsize=9, color="#555", style="italic")
        ax.axhline(y, color="#eee", linestyle="--", linewidth=0.5, zorder=0)

    ax.set_title(f"Camadas BFS a partir de {origem} (Hub Central)", fontsize=14,
                 fontweight="bold")

    patches_leg = [mpatches.Patch(color=c, label=r) for r, c in COR_REGIAO.items()]
    ax.legend(handles=patches_leg, title="Região", fontsize=9,
              title_fontsize=9, loc="upper right")

    fig.text(0.5, -0.02,
        "Insight: BSB alcanca todos os aeroportos em no maximo 4 saltos, confirmando seu papel de hub nacional.\n"
        "Aeroportos de nivel 4 (RBR, POA) sao extremidades da rede — mais vulneraveis a desconexao.",
        ha="center", fontsize=9, style="italic", color="#444")

    plt.tight_layout()
    path = os.path.join(OUT, "viz4_bfs_camadas_BSB.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"[OK] {path}")

def main():
    print("=== Gerando visualizacoes — Parte 8 ===")
    viz1_distribuicao_graus_pizza()
    viz2_ranking_aeroportos()
    viz3_comparacao_regioes()
    viz4_bfs_camadas()
    print("\nPronto! Arquivos salvos em out/")

if __name__ == "__main__":
    main()