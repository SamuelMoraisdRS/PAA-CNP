# Problema dos Nós Críticos (CNP) — guloso greedy2

Trabalho da disciplina de PAA.
Autores: **Leonardo Machado Moreira** e **Samuel Morais da Rocha e Silva**.

Implementação em Python puro do guloso construtivo *greedy2* (Addis et al.)
para o Problema dos Nós Críticos, em duas versões: uma ingênua, que recalcula
a função objetivo do zero para cada candidato, e uma rápida, baseada em busca
em profundidade e pontos de articulação (Ventresca & Aleman, 2015).

---

## Como executar

### 1. Verifique o Python

É preciso ter o **Python 3.8 ou mais recente**. Nenhuma biblioteca externa é
necessária: o código usa apenas a biblioteca padrão do Python. Para conferir a
versão instalada:

```bash
python3 --version
```

> **Windows:** o comando costuma ser `python` em vez de `python3`. Isso vale
> para todos os comandos abaixo.

### 2. Entre na pasta do projeto

```bash
cd PAA-CNP
```

O programa também roda a partir de outra pasta, indicando o caminho até o
`main.py` (por exemplo, `python3 caminho/para/PAA-CNP/main.py`).

### 3. Abra a interface

```bash
python3 main.py
```

Aparece o menu com as instâncias disponíveis:

```
======================================================================
PROBLEMA DOS NÓS CRÍTICOS (CNP) — guloso greedy2
======================================================================
Instâncias disponíveis:
   1) BarabasiAlbert_n500m1      K=50    (Ventresca)
   2) BarabasiAlbert_n1000m1     K=75    (Ventresca)
  ...
  16) WattsStrogatz_n1500        K=265   (Ventresca)
  17) exemplo7                   K=2     (testes)
   T) Rodar todas as instâncias do benchmark (gera a tabela)
   S) Sair
Escolha uma opção:
```

| Digite | O que acontece |
|---|---|
| o número de uma instância | Roda essa instância. O programa pergunta o valor de K (Enter usa o K padrão do benchmark) e o algoritmo: **1** = greedy2 rápido (DFS, padrão); **2** = greedy2 ingênuo (lento nas instâncias grandes). |
| **T** | Roda as 16 instâncias do benchmark com o K padrão e gera a tabela de resultados. |
| **S** | Sai do programa. |

### 4. Exemplo: rodando uma instância

Escolhendo o grafo pequeno de exemplo (opção **17**) e apertando Enter nas
duas perguntas, para usar o K padrão e o algoritmo rápido:

```
Escolha uma opção: 17
Valor de K [Enter = 2]:
Algoritmo:
  1) greedy2 rápido (DFS + pontos de articulação)
  2) greedy2 ingênuo (recalcula f do zero; lento nas instâncias grandes)
Escolha [Enter = 1]:

Executando...

======================================================================
RELATÓRIO DO EXPERIMENTO — Problema dos Nós Críticos (CNP)
======================================================================
Instância ................ exemplo7
Arquivo .................. testes/exemplo7.txt
Vértices (n) ............. 7
Arestas (m) .............. 8
K (máx. de remoções) ..... 2
Algoritmo ................ greedy2 rápido (DFS + pontos de articulação), O(k(n+m))
Tempo de execução ........ 0.000 s
f(G) sem remoções ........ 21
f(G\R) obtido ............ 3
Melhor valor conhecido ... 2
Gap para o melhor ........ +50.00%

MELHOR SOLUÇÃO ENCONTRADA
|R| ...................... 2
f(G\R) ................... 3
R (na ordem de escolha):
  3 5
R (ordenado):
  3 5
======================================================================
Relatório completo (com a evolução de f) salvo em: resultados/exemplo7_dfs.txt
```

Depois disso o menu aparece de novo, para rodar outra instância. Digite **S**
para sair.

### 5. Veja os resultados salvos

Tudo o que aparece na tela também é salvo na pasta `resultados/`, criada
automaticamente:

- `resultados/<instancia>_<algoritmo>.txt`: o relatório do experimento, igual
  ao da tela (instância, n, m, K, algoritmo, tempo, f(G \ R) obtido, melhor
  valor conhecido, gap e a melhor solução encontrada, o conjunto R). No final,
  a evolução de f(G \ R) a cada vértice removido.
- `resultados/tabela_<algoritmo>.csv`: tabela com todas as instâncias, gerada
  pela opção **T**.

`<algoritmo>` é `dfs` (versão rápida) ou `ingenuo` (versão ingênua).

### 6. (Opcional) Rode os testes de validação

```bash
python3 validar.py
```

Leva poucos segundos e deve terminar com:

```
Todas as verificações passaram.
```

A seção [Validação](#validação) explica o que é verificado.

---

## O problema

Dado um grafo não direcionado G = (V, E) e um inteiro K, o CNP pede um
conjunto R ⊆ V com |R| ≤ K cuja remoção deixe o grafo o **menos conectado
possível**. A conectividade é medida por

```
f(G \ R) = Σ C(|Cᵢ|, 2) = Σ |Cᵢ|·(|Cᵢ| − 1) / 2
```

em que Cᵢ são as componentes conexas do grafo residual G \ R. Ou seja, f conta
quantos pares de vértices ainda conseguem se alcançar.

**Exemplo** (`testes/exemplo7.txt`): dois triângulos ligados por uma ponte, mais
uma folha.

```
0 ── 1        4
 \  /        / \
  2 ─────── 3 ── 5 ── 6
```

Sem remoções, os 7 vértices estão conectados: f = C(7,2) = 21. Removendo o
vértice 3, sobram dois pedaços de 3 vértices: f = 3 + 3 = 6, a melhor remoção
única.

**Complexidade.** O problema é NP-difícil (Arulselvan et al., 2009). Com o
limite B = 0, a pergunta "existe R com |R| ≤ K e f(G \ R) ≤ B?" vira "existe
R com |R| ≤ K que toque todas as arestas?", que é exatamente o problema da
Cobertura de Vértices (*Vertex Cover*), NP-completo.

---

## O algoritmo: greedy2

```
R ← ∅
enquanto |R| < K:
    v* ← o vértice fora de R que, removido, deixa o menor f(G \ (R ∪ {v}))
    R ← R ∪ {v*}
    se f(G \ R) = 0: pare          (não há mais arestas)
devolva R
```

Empates são decididos pelo **menor índice**. As duas versões só diferem na
forma de avaliar os candidatos:

|  | Ingênua | Rápida |
|---|---|---|
| Arquivo | `algorithms/greedy2.py` | `algorithms/greedy2_dfs.py` |
| Avaliação dos candidatos | uma BFS do zero para cada candidato | uma única DFS avalia todos os candidatos |
| Custo por iteração | O(n·(n+m)) | O(n+m) |
| Custo total | O(k·n·(n+m)) | O(k·(n+m)) |

As duas escolhem **exatamente os mesmos vértices**; isso é verificado pelo
`validar.py`.

### Como a versão rápida avalia todos os candidatos de uma vez

Uma DFS iterativa (com pilha explícita, para não estourar o limite de recursão
do Python) calcula, para cada vértice v:

- `dfn[v]`: a ordem de visita;
- `low[v]`: o menor `dfn` alcançável a partir da subárvore de v usando uma
  aresta de retorno (regra de Tarjan);
- o tamanho da subárvore de v.

Um filho c de v é um **filho de corte** quando `low[c] ≥ dfn[v]`: nenhuma
aresta da subárvore de c escapa para cima de v, então remover v isola essa
subárvore. Somando os pares de cada subárvore isolada com os pares do "resto"
(ancestrais e subárvores que não são de corte, que continuam numa peça só):

```
f(G \ (S ∪ {v})) = f(G \ S) − C(|comp(v)|, 2) + Σ C(|subárvore de corte|, 2) + C(resto, 2)
```

Isso dá o valor de **todos** os candidatos em O(n+m), em vez de O(n·(n+m)).

O greedy2 não tem garantia de aproximação provada: é uma heurística
construtiva. No exemplo de 7 vértices com K = 2, ele escolhe {3, 5} (f = 3),
mas o ótimo é {2, 5} (f = 2).

---

## Estrutura do repositório

```
PAA-CNP/
├── main.py                  interface (menu); ponto de entrada
├── graph.py                 leitura das instâncias (formato Ventresca)
├── f_function.py            f(G \ S) calculado do zero (BFS)
├── validar.py               testes de validação
├── algorithms/
│   ├── greedy2.py           greedy2 ingênuo
│   └── greedy2_dfs.py       greedy2 rápido (DFS + pontos de articulação)
├── Ventresca/               16 instâncias sintéticas do benchmark
├── testes/
│   └── exemplo7.txt         grafo pequeno de 7 vértices
├── resultados/              saídas geradas pelo main.py
└── README.md
```

---

## Instâncias

As 16 instâncias sintéticas do benchmark de Ventresca (2012), em quatro
famílias: Barabási–Albert, Erdős–Rényi, Forest Fire e Watts–Strogatz. O
formato de cada arquivo é:

```
n
0: vizinhos de 0
1: vizinhos de 1
...
```

Os nomes dos arquivos trazem o n usado na geração. As instâncias Erdős–Rényi
têm menos vértices que isso (por exemplo, `ErdosRenyi_n250` tem 235 e aparece
na literatura como ER235). As instâncias Barabási–Albert são árvores
(m = n − 1).

Os valores de K e os melhores valores conhecidos usados para comparação vêm da
Tabela IV de Zhou, Hao & Glover (2019).

Os vértices são numerados de 0 a n − 1. Para testar outro grafo, basta colocar
um arquivo `.txt` nesse formato na pasta `testes/`. Ele aparece
automaticamente no menu, sem K padrão: o programa pede o valor.

---

## Resultados

Versão rápida, com o K padrão de cada instância. Os tempos foram medidos num
Intel Core i7-12700 com Python 3.12.

| Instância | n | m | K | f(G \ R) | Melhor conhecido | Gap | Tempo (s) |
|---|---:|---:|---:|---:|---:|---:|---:|
| BarabasiAlbert_n500m1 | 500 | 499 | 50 | 199 | 195 | +2,05% | 0,023 |
| BarabasiAlbert_n1000m1 | 1000 | 999 | 75 | 559 | 558 | +0,18% | 0,069 |
| BarabasiAlbert_n2500m1 | 2500 | 2499 | 100 | 3726 | 3704 | +0,59% | 0,205 |
| BarabasiAlbert_n5000m1 | 5000 | 4999 | 150 | 10216 | 10196 | +0,20% | 0,426 |
| ErdosRenyi_n250 | 235 | 350 | 50 | 3889 | 295 | +1218,31% | 0,006 |
| ErdosRenyi_n500 | 466 | 700 | 80 | 28520 | 1524 | +1771,39% | 0,024 |
| ErdosRenyi_n1000 | 941 | 1400 | 140 | 124426 | 5012 | +2382,56% | 0,088 |
| ErdosRenyi_n2500 | 2344 | 3500 | 200 | 1393897 | 902498 | +54,45% | 0,326 |
| ForestFire_n250 | 250 | 514 | 50 | 210 | 194 | +8,25% | 0,008 |
| ForestFire_n500 | 500 | 828 | 110 | 277 | 257 | +7,78% | 0,053 |
| ForestFire_n1000 | 1000 | 1817 | 150 | 1388 | 1260 | +10,16% | 0,103 |
| ForestFire_n2000 | 2000 | 3413 | 200 | 4873 | 4545 | +7,22% | 0,310 |
| WattsStrogatz_n250 | 250 | 1246 | 70 | 16110 | 3083 | +422,54% | 0,022 |
| WattsStrogatz_n500 | 500 | 1496 | 125 | 69378 | 2072 | +3248,36% | 0,081 |
| WattsStrogatz_n1000 | 1000 | 4996 | 200 | 319600 | 109807 | +191,06% | 0,454 |
| WattsStrogatz_n1500 | 1500 | 4498 | 265 | 760761 | 13098 | +5708,22% | 0,525 |

Gap = (f obtido − melhor conhecido) / melhor conhecido.

### Tempo: versão ingênua × versão rápida

As duas versões chegam ao mesmo f em todas as instâncias; muda só o tempo.

| Instância | n | Ingênua (s) | Rápida (s) | Aceleração |
|---|---:|---:|---:|---:|
| BarabasiAlbert_n500m1 | 500 | 2,59 | 0,023 | ≈ 112× |
| BarabasiAlbert_n1000m1 | 1000 | 14,74 | 0,069 | ≈ 214× |
| BarabasiAlbert_n2500m1 | 2500 | 105,18 | 0,205 | ≈ 513× |
| BarabasiAlbert_n5000m1 | 5000 | 617,73 | 0,426 | ≈ 1450× |
| ErdosRenyi_n250 | 235 | 0,40 | 0,006 | ≈ 67× |
| ErdosRenyi_n500 | 466 | 2,54 | 0,024 | ≈ 106× |
| ErdosRenyi_n1000 | 941 | 19,38 | 0,088 | ≈ 220× |
| ErdosRenyi_n2500 | 2344 | 169,57 | 0,326 | ≈ 520× |
| ForestFire_n250 | 250 | 0,40 | 0,008 | ≈ 50× |
| ForestFire_n500 | 500 | 3,74 | 0,053 | ≈ 70× |
| ForestFire_n1000 | 1000 | 23,30 | 0,103 | ≈ 226× |
| ForestFire_n2000 | 2000 | 125,94 | 0,310 | ≈ 406× |
| WattsStrogatz_n250 | 250 | 0,73 | 0,022 | ≈ 33× |
| WattsStrogatz_n500 | 500 | 3,38 | 0,081 | ≈ 42× |
| WattsStrogatz_n1000 | 1000 | 34,34 | 0,454 | ≈ 76× |
| WattsStrogatz_n1500 | 1500 | 85,59 | 0,525 | ≈ 163× |
| **Total** | | **≈ 1238 s (20,6 min)** | **≈ 2,7 s** | |

Dentro de cada família, a aceleração cresce com n, como prevê a análise: a
versão ingênua tem um fator n a mais por iteração. Entre famílias, a
aceleração varia (é menor nas Watts–Strogatz), porque as constantes das duas
implementações não são iguais, e a análise assintótica não mede constantes.

### Discussão

- **Barabási–Albert e Forest Fire:** o guloso fica perto do melhor conhecido
  (0,2% a 10%). Esses grafos têm muitos vértices cuja remoção desconecta o
  grafo, e o guloso os encontra.
- **Watts–Strogatz:** o resultado é muito pior. Num grafo Watts–Strogatz (um
  anel com atalhos), nenhum vértice sozinho desconecta o grafo. Todos os
  candidatos empatam, e o guloso remove vértices sem nunca quebrar o grafo. Na
  WattsStrogatz_n250, os 70 vértices removidos deixam uma única componente de
  180 vértices: f = C(180, 2) = 16110.
- **Erdős–Rényi:** aqui não há empate geral, mas a escolha que mais reduz f
  num único passo não leva a um bom conjunto depois de K passos.
- As duas famílias mostram a limitação de um guloso que olha só um passo à
  frente. Por isso os métodos da literatura combinam construção gulosa com
  busca local ou outras estratégias.

---

## Validação

`python3 validar.py` executa cinco verificações, com semente aleatória fixa:

1. **Exemplo de 7 vértices:** f e as escolhas do guloso batem com os valores
   calculados à mão.
2. **Avaliação rápida × do zero:** em 300 grafos aleatórios (alguns com
   arestas repetidas), o valor que a DFS calcula para cada candidato é igual
   ao f recalculado do zero (cerca de 30 mil comparações).
3. **Guloso rápido × ingênuo:** em 100 grafos aleatórios, as duas versões
   escolhem os mesmos vértices.
4. **Instâncias do benchmark:** o mesmo teste nas quatro menores instâncias,
   com o K real.
5. **Força bruta:** no exemplo de 7 vértices, compara o guloso com o ótimo
   exato (o guloso nunca é melhor que o ótimo, e com K = 2 é pior).

---

## Referências

- Addis, B., Aringhieri, R., Grosso, A., Hosteins, P. (2016). Hybrid
  constructive heuristics for the critical node problem. *Annals of Operations
  Research*, 238, 637–649.
- Arulselvan, A., Commander, C. W., Elefteriadou, L., Pardalos, P. M. (2009).
  Detecting critical nodes in sparse graphs. *Computers & Operations
  Research*, 36(7), 2193–2200.
- Tarjan, R. (1972). Depth-first search and linear graph algorithms. *SIAM
  Journal on Computing*, 1(2), 146–160.
- Ventresca, M. (2012). Global search algorithms using a combinatorial
  unranking-based problem representation for the critical node detection
  problem. *Computers & Operations Research*, 39(11), 2763–2775.
- Ventresca, M., Aleman, D. (2015). Efficiently identifying critical nodes in
  large complex networks. *Computational Social Networks*, 2(1), 6.
- Zhou, Y., Hao, J.-K., Glover, F. (2019). Memetic search for identifying
  critical nodes in sparse graphs. *IEEE Transactions on Cybernetics*.
  arXiv:1705.04119.
