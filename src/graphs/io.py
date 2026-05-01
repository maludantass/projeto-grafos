import csv
from .graph import Grafo

def ler_aeroportos(caminho_arquivo):

    grafo = Grafo()
    with open(caminho_arquivo, mode='r', encoding='utf-8') as f:
        leitor_csv = csv.DictReader(f)
        for linha in leitor_csv:
            iata = linha.get('iata', '').strip()
            cidade = linha.get('cidade', '').strip()
            regiao = linha.get('regiao', '').strip()
            
            if iata:
                # Adiciona o nó rotulado com IATA, guardando cidade e regiao como atributos
                grafo.adicionar_no(iata, cidade=cidade, regiao=regiao)
                
    return grafo

def ler_adjacencias(grafo, caminho_arquivo):
    with open(caminho_arquivo, mode='r', encoding='utf-8') as f:
        leitor_csv = csv.DictReader(f)
        for linha in leitor_csv:
            origem = linha.get('origem', '').strip()
            destino = linha.get('destino', '').strip()
            tipo_conexao = linha.get('tipo_conexao', '').strip()
            justificativa = linha.get('justificativa', '').strip()
            peso = linha.get('peso', '1.0').strip()
            
            if origem and destino:
                grafo.adicionar_aresta(
                    origem=origem,
                    destino=destino,
                    peso=peso,
                    tipo_conexao=tipo_conexao,
                    justificativa=justificativa
                )
