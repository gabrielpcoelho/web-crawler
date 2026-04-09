# Web Crawler BRACIS

Versao final - 08/04/2026

Este repositorio contem um notebook para:

- Coletar trabalhos do BRACIS (edicoes 2023, 2024 e 2025) no portal SOL/SBC.
- Consolidar os dados em tabela e exportar CSV.
- Aplicar modelagem de topicos com duas abordagens: NMF com BoW/TF-IDF e BERTopic.
- Comparar os metodos com metricas e graficos.

## Estrutura do repositorio

- `crawler_bracis.ipynb`: notebook principal com coleta, processamento e analise.
- `bracis_trabalhos_2023_2025.csv`: dataset consolidado gerado pelo notebook.
- `AGI_development.pdf`: material de apoio no repositorio.

## Tecnologias e bibliotecas

- Python 3
- requests
- beautifulsoup4
- pandas
- numpy
- matplotlib
- seaborn
- scikit-learn
- bertopic
- sentence-transformers
- umap-learn
- hdbscan
- gensim

## Como executar

### Opcao 1 - Google Colab

1. Abra o arquivo `crawler_bracis.ipynb` no Colab.
2. Execute as celulas em ordem.
3. Caso necessario, rode a celula de instalacao de dependencias da Parte 2.

### Opcao 2 - Ambiente local (Jupyter)

1. Crie e ative um ambiente virtual.
2. Instale dependencias:

```bash
pip install notebook requests beautifulsoup4 pandas numpy matplotlib seaborn scikit-learn bertopic sentence-transformers umap-learn hdbscan gensim
```

3. Inicie o Jupyter:

```bash
jupyter notebook
```

4. Abra `crawler_bracis.ipynb` e execute as celulas em ordem.

## Saida de dados

O notebook exporta:

- `bracis_trabalhos_2023_2025.csv`

Colunas principais do CSV:

- `Conferencia`
- `Ano`
- `Edicao`
- `Titulo`
- `Resumo`
- `Link`

## Observacoes

- A coleta depende da estrutura atual do site SOL/SBC (`https://sol.sbc.org.br/index.php`).
- Mudancas no HTML do portal podem exigir ajustes nos seletores do crawler.
- O notebook foi ajustado para renderizar corretamente no GitHub.
