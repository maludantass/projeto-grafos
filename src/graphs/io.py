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
    colunas_obrigatorias = {
        "origem",
        "destino",
        "tipo_conexao",
        "justificativa",
        "peso"
    }

    with open(caminho_arquivo, mode='r', encoding='utf-8') as f:
        leitor_csv = csv.DictReader(f)

        if leitor_csv.fieldnames is None:
            raise ValueError("O arquivo de adjacências está vazio.")

        colunas_faltando = colunas_obrigatorias - set(leitor_csv.fieldnames)

        if colunas_faltando:
            raise ValueError(
                "Colunas obrigatórias ausentes em adjacencias_aeroportos.csv: "
                + ", ".join(sorted(colunas_faltando))
            )

        for numero_linha, linha in enumerate(leitor_csv, start=2):
            origem = linha.get('origem', '').strip().upper()
            destino = linha.get('destino', '').strip().upper()
            tipo_conexao = linha.get('tipo_conexao', '').strip()
            justificativa = linha.get('justificativa', '').strip()
            peso_texto = linha.get('peso', '').strip()

            if not origem:
                raise ValueError(f"Linha {numero_linha}: origem vazia.")

            if not destino:
                raise ValueError(f"Linha {numero_linha}: destino vazio.")

            if not tipo_conexao:
                raise ValueError(f"Linha {numero_linha}: tipo_conexao vazio.")

            if not justificativa:
                raise ValueError(f"Linha {numero_linha}: justificativa vazia.")

            if not peso_texto:
                raise ValueError(f"Linha {numero_linha}: peso vazio.")

            try:
                peso = float(peso_texto)
            except ValueError:
                raise ValueError(f"Linha {numero_linha}: peso inválido: {peso_texto}")

            if peso < 0:
                raise ValueError(f"Linha {numero_linha}: peso negativo não é permitido na Parte 1.")

            grafo.adicionar_aresta(
                origem=origem,
                destino=destino,
                peso=peso,
                tipo_conexao=tipo_conexao,
                justificativa=justificativa
            )