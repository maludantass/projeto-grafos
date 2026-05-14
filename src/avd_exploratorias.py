#parte 10 análise exploratória
import csv
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.colors as mcolors
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

ORDEM_REGIAO = ["Norte", "Nordeste", "Centro-Oeste", "Sudeste", "Sul"]

#heatmap de adjacências entre regiões 

def viz10_1_heatmap_adjacencias():
    #pq dessa escolha para avd: análise exploratória

    #O que mostra: Uma matriz 5x5 com a contagem de arestas entre pares de regiões. 
    # A diagonal representa conexões intrarregionais, fora da diagonal, inter-regionais.

    #Insight: permite identificar quais regiões estão mais integradas entre si e quais ficam isoladas. 
    # Regiões com muitas conexões inter-regionais funcionam como pontes da rede.

    #Por que heatmap: A matriz de adjacência regional é um dado 2-D categórico x categórico, heatmap é o tipo
    #  canônico para esse padrão, codifica a magnitude por cor e facilita a leitura cruzada.

    aeroportos_raw = ler_csv(os.path.join(DATA, "aeroportos_data.csv"))
    adj_raw        = ler_csv(os.path.join(DATA, "adjacencias_aeroportos.csv"))
    regiao_map     = {r["iata"]: r["regiao"] for r in aeroportos_raw}

    idx = {r: i for i, r in enumerate(ORDEM_REGIAO)}
    n   = len(ORDEM_REGIAO)
    mat = np.zeros((n, n), dtype=int)

    for row in adj_raw:
        r_o = regiao_map.get(row["origem"],  "")
        r_d = regiao_map.get(row["destino"], "")
        if r_o in idx and r_d in idx:
            i, j = idx[r_o], idx[r_d]
            mat[i][j] += 1
            if i != j:
                mat[j][i] += 1

    fig, ax = plt.subplots(figsize=(8, 6.5))
    fig.patch.set_facecolor("#0F1923")
    ax.set_facecolor("#0F1923")

    cmap = mcolors.LinearSegmentedColormap.from_list(
        "aurora", ["#0F1923", "#1B3A5C", "#1565C0", "#42A5F5", "#E3F2FD"]
    )
    im = ax.imshow(mat, cmap=cmap, aspect="auto")

    rotulos = [r.replace("-", "-\n") for r in ORDEM_REGIAO]
    ax.set_xticks(range(n)); ax.set_xticklabels(rotulos, color="white", fontsize=10)
    ax.set_yticks(range(n)); ax.set_yticklabels(ORDEM_REGIAO, color="white", fontsize=10)

    for i in range(n):
        for j in range(n):
            val = mat[i][j]
            cor_txt = "black" if val >= 3 else "white"
            diag = " *" if i == j else ""
            ax.text(j, i, f"{val}{diag}", ha="center", va="center",
                    fontsize=13, fontweight="bold", color=cor_txt)

    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.ax.yaxis.set_tick_params(color="white")
    ticks = cbar.get_ticks()
    cbar.ax.set_yticks(ticks)
    cbar.ax.set_yticklabels([str(int(t)) for t in ticks], color="white")
    cbar.set_label("Nr de arestas", color="white", fontsize=10)

    ax.set_title("Heatmap de Adjacências entre Regiões", fontsize=14,
                 fontweight="bold", color="white", pad=14)
    ax.set_xlabel("Região de Destino", fontsize=11, color="#90CAF9", labelpad=8)
    ax.set_ylabel("Região de Origem",  fontsize=11, color="#90CAF9", labelpad=8)
    ax.tick_params(colors="white")
    for spine in ax.spines.values():
        spine.set_edgecolor("#1B3A5C")

    nota = (
        "* Diagonal = conexoes intrarregionais  |  "
        "Nordeste-Sudeste: maior integracao inter-regional (2 arestas)\n"
        "Centro-Oeste (BSB) serve de ponte: conecta-se com 4 das 5 regioes — "
        "hub estrategico nacional."
    )
    fig.text(0.5, -0.03, nota, ha="center", fontsize=8.5,
             color="#90CAF9", style="italic")

    plt.tight_layout()
    path = os.path.join(OUT, "viz10_1_heatmap_adjacencias.png")
    plt.savefig(path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close()
    print(f"[OK] {path}")

# barras horizontais ordenadas 

def viz10_2_centralidade_grau():
    #pq dessa escolha para avd: análise exploratória

    #O que mostra: Barras horizontais com a centralidade normalizada de cada aeroporto, ordenadas do maior
    #  para o menor grau. Cada barra é colorida pela região do aeroporto. Uma linha vertical marca a média da rede. 
    # Faixas de fundo destacam os três níveis.

    #Insight: Revela a assimetria da rede: poucos aeroportos concentram alta centralidade enquanto a maioria permanece periférica.
    # A coloração por região expõe quais regiões possuem hubs e quais são dependentes de escala.

    #Por que barras horizontais: Com 20 aeroportos cada um precisando ser identificado, barras horizontais são o tipo canônico
    # cada aeroporto ocupa sua própria linha, rótulo legível à esquerda, comprimento proporcional ao valor.
    # Zero sobreposição possível.

    aeroportos_raw = ler_csv(os.path.join(DATA, "aeroportos_data.csv"))
    graus_raw      = ler_csv(os.path.join(OUT,  "graus.csv"))
    regiao_map     = {r["iata"]: r["regiao"] for r in aeroportos_raw}

    # em caso de empate coloca como alfabetica 
    graus_sorted = sorted(graus_raw,
                          key=lambda r: (-int(r["grau"]), r["aeroporto"]))

    nos   = [r["aeroporto"] for r in graus_sorted]
    graus = [int(r["grau"]) for r in graus_sorted]
    n     = len(nos)
    V_1   = n - 1
    cents = [g / V_1 for g in graus]
    media = np.mean(cents)
    cores = [COR_REGIAO.get(regiao_map.get(no, ""), "#888") for no in nos]

    fig, ax = plt.subplots(figsize=(11, 9))
    fig.patch.set_facecolor("#FAFAFA")
    ax.set_facecolor("#FAFAFA")

    y_pos = np.arange(n)

    ax.axvspan(0,      0.106, alpha=0.10, color="#2196F3", zorder=0)
    ax.axvspan(0.106,  0.263, alpha=0.10, color="#FF9800", zorder=0)
    ax.axvspan(0.263,  0.42,  alpha=0.10, color="#F44336", zorder=0)

    ax.text(0.053, n - 0.1, "BAIXO", ha="center", fontsize=8,
            color="#1565C0", fontweight="bold", alpha=0.7, va="top")
    ax.text(0.184, n - 0.1, "MÉDIO", ha="center", fontsize=8,
            color="#E65100", fontweight="bold", alpha=0.7, va="top")
    ax.text(0.340, n - 0.1, "ALTO",  ha="center", fontsize=8,
            color="#B71C1C", fontweight="bold", alpha=0.7, va="top")

    bars = ax.barh(y_pos, cents, color=cores,
                   edgecolor="white", linewidth=0.6,
                   height=0.65, zorder=2)

    for bar, c, g in zip(bars, cents, graus):
        ax.text(c + 0.004,
                bar.get_y() + bar.get_height() / 2,
                f"{c:.3f}  (grau {g})",
                va="center", ha="left", fontsize=8.5, color="#333")

    # linha de média
    ax.axvline(media, color="#E53935", linestyle="--",
               linewidth=1.8, zorder=3, label=f"Média = {media:.3f}")

    ax.set_yticks(y_pos)
    ax.set_yticklabels(nos, fontsize=10, fontweight="bold")
    ax.set_xlabel("Centralidade Normalizada  [grau / (|V|-1)]",
                  fontsize=11, labelpad=8)
    ax.set_ylabel("Aeroporto (código IATA)", fontsize=11)
    ax.set_title("Centralidade de Grau por Aeroporto e Região",
                 fontsize=14, fontweight="bold", pad=12)
    ax.set_xlim(0, max(cents) + 0.12)
    ax.set_ylim(-0.6, n - 0.4)
    ax.grid(axis="x", linestyle="--", alpha=0.35)

    patches_leg = [mpatches.Patch(color=c, label=r) for r, c in COR_REGIAO.items()]
    ax.legend(handles=patches_leg + [
        mpatches.Patch(color="#E53935", label=f"Média = {media:.3f}")
    ], title="Região", fontsize=9, title_fontsize=9, loc="lower right")

    nota = (
        "Insight exploratório: BSB concentra a maior centralidade (0.316), "
        "seguido por GRU, FOR e GIG (0.211).\n"
        "Cerca de 50% dos aeroportos ficam abaixo da média — "
        "dependência crítica de poucos hubs."
    )
    fig.text(0.5, -0.02, nota, ha="center", fontsize=8.5,
             color="#555", style="italic")

    plt.tight_layout()
    path = os.path.join(OUT, "viz10_2_centralidade_grau.png")
    plt.savefig(path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close()
    print(f"[OK] {path}")

def main():
    print("Visualizações Exploratórias")
    viz10_1_heatmap_adjacencias()
    viz10_2_centralidade_grau()
    print("\nArquivos salvos em out/")
    print("viz10_1_heatmap_adjacencias.png")
    print("viz10_2_centralidade_grau.png")

if __name__ == "__main__":
    main()