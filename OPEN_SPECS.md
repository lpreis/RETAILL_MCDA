# OPEN_SPECS — RETAILL_MCDA / MCDA Moderno

## 1. Identificação do projeto

**Nome final do repositório:** `RETAILL_MCDA`  
**Nome da aplicação:** `MCDA Moderno — Seleção de Fornecedores de Fruta`  
**Tipo de projeto:** Aplicação web local em Python para apoio à decisão multicritério.  
**Tecnologia principal:** Python + Streamlit + JSON.  
**Inspiração:** Aplicação legacy MCDA e slides do exemplo MCDA para seleção de fornecedores de fruta.

> Decisão de projeto: o nome com dois “L” é intencional. O projeto deve usar `RETAILL_MCDA` de forma consistente no README e na interface.

---

## 2. Objetivo

Desenvolver uma versão moderna, simples e extensível do MCDA, usando Python e ficheiros JSON, com uma interface mais atual e visualmente inspirada na aplicação original e nos slides fornecidos.

A aplicação deve permitir estruturar um problema de decisão multicritério, avaliar alternativas com critérios ponderados, usar uma escala semântica de 7 níveis, calcular rankings e executar análises de sensibilidade/robustez.

O caso exemplo principal será a **seleção de fornecedores de fruta**.

---

## 3. Contexto funcional

Uma empresa de distribuição de fruta precisa selecionar fornecedores para a sua cadeia de abastecimento. Existem vários candidatos no mercado, mas a decisão envolve múltiplos fatores potencialmente contraditórios:

- Preço vs. qualidade;
- Prazo vs. variedade;
- Sustentabilidade vs. custo;
- Reputação vs. proximidade;
- Capacidade de fornecimento vs. risco operacional.

A metodologia MCDA/MCDA estrutura a decisão num processo claro, auditável e compreensível para decisores não técnicos.

---

## 4. Tecnologias

### 4.1 Stack principal

- Python 3.10+
- Streamlit
- Pandas
- Plotly
- Pydantic
- JSON como formato de persistência

### 4.2 Dependências

```text
streamlit>=1.36
pandas>=2.0
plotly>=5.20
pydantic>=2.7
openpyxl>=3.1
reportlab>=4.0
```

### 4.3 Execução

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## 5. Estrutura esperada do projeto

```text
RETAILL_MCDA/
  app.py
  README.md
  requirements.txt
  smoke_test.py

  core/
    __init__.py
    models.py
    storage.py
    calculation.py
    sample_data.py

  data/
    fornecedores_fruta_alpha.json

  exports/
    resultado_exemplo_base.csv

  .streamlit/
    config.toml
```

---

## 6. Design visual

A interface deve ter uma estética moderna, mas inspirada no legacy/slides.

### 6.1 Paleta visual

```text
Azul escuro:     #173A5E
Verde:           #49B051
Turquesa:        #2AC6B6
Teal:            #178F88
Fundo claro:     #F3F8F4
Branco:          #FFFFFF
Vermelho escala: #B71C1C
```

### 6.2 Estilo pretendido

- Interface em cartões;
- Dashboard inicial com visual forte;
- Header/hero azul escuro com detalhes verdes/turquesa;
- Sidebar com o logotipo `RETAILL_MCDA` no lugar do título textual, com destaque visual maior que os restantes logos;
- Barra superior com logos institucionais/parceiros, excluindo o logotipo `RETAILL_MCDA`;
- Barra de logos responsiva, compacta e com logos secundários pequenos para não competir com o logotipo principal;
- Barra de logos com altura e padding vertical suficientes para evitar cortes no topo e na base dos logos;
- A navegação interna da aplicação deve ocorrer sempre na mesma tab do browser, sem abrir novos separadores.
- Matrizes coloridas para avaliação das alternativas;
- Gráficos horizontais para ranking;
- Separação clara por etapas;
- Estética inspirada no legacy, mas mais limpa e moderna.

---

## 7. Modelo de decisão

A aplicação implementa uma metodologia de apoio à decisão multicritério baseada em soma ponderada.

### 7.1 Fórmula principal

```text
Valor Global = Σ (peso normalizado do critério × pontuação na escala)
```

### 7.2 Pesos

Os pesos podem ser introduzidos em qualquer escala relativa. A aplicação normaliza automaticamente os pesos para que a soma seja 1.

Exemplo:

```text
A1.1 = 100
A1.2 = 80
A1.3 = 60
A1.4 = 50
A1.5 = 40
A1.6 = 40
```

Soma dos pesos:

```text
100 + 80 + 60 + 50 + 40 + 40 = 370
```

Pesos normalizados aproximados:

```text
A1.1 = 27.03%
A1.2 = 21.62%
A1.3 = 16.22%
A1.4 = 13.51%
A1.5 = 10.81%
A1.6 = 10.81%
```

---

## 8. Escala semântica de 7 níveis

A aplicação deve usar a escala semântica de 7 níveis usada nos slides.

| Código | Nível | Pontuação |
|---|---|---:|
| MM | Muito Melhor | +100 |
| M | Melhor | +50 |
| LM | Ligeiramente Melhor | +25 |
| N | Neutro | 0 |
| LP | Ligeiramente Pior | -25 |
| P | Pior | -50 |
| MP | Muito Pior | -100 |

### 8.1 Cores da escala

| Código | Cor sugerida |
|---|---|
| MM | Verde escuro |
| M | Verde |
| LM | Verde claro |
| N | Verde muito claro / neutro |
| LP | Amarelo/laranja claro |
| P | Vermelho claro |
| MP | Vermelho escuro |

---

## 9. Caso exemplo principal

### 9.1 Nome

```text
Seleção de Fornecedores de Fruta
```

### 9.1.1 Exemplo alargado

A aplicação deve incluir também um ficheiro JSON exemplo com 50 fornecedores sintéticos, com perfis bastante diferentes entre si, cobrindo desde fornecedores muito bons até fornecedores muito maus.

Ficheiro:

```text
data/fornecedores_fruta_50_variado.json
```

### 9.2 Descrição

```text
Modelo MCDA/MCDA para selecionar fornecedores de fruta numa cadeia de abastecimento.
```

### 9.3 Contexto

```text
Uma empresa de distribuição de fruta precisa selecionar fornecedores.
A decisão envolve conflitos entre qualidade, preço, prazo, sustentabilidade, reputação e capacidade de fornecimento.
```

---

## 10. Critérios do exemplo

| Código | Critério | Descrição | Peso |
|---|---|---|---:|
| A1.1 | Qualidade da Fruta | Calibre, aspeto, grau Brix, ausência de defeitos e conformidade com normas. | 100 |
| A1.2 | Preço / Custo Total | Preço por kg, descontos por volume, custos de transporte e embalagem. | 80 |
| A1.3 | Prazo de Entrega | Tempo médio de entrega, cumprimento de prazos e flexibilidade de agendamento. | 60 |
| A1.4 | Sustentabilidade | Certificações bio, pegada carbónica e práticas agrícolas responsáveis. | 50 |
| A1.5 | Fiabilidade / Reputação | Histórico de incidentes, referências de clientes e anos de experiência. | 40 |
| A1.6 | Capacidade de Fornecimento | Volume disponível, variedade de espécies e continuidade ao longo do ano. | 40 |

---

## 11. Alternativas do exemplo

| Alternativa | Descrição | Custo estimado |
|---|---|---:|
| ALPHA | Fornecedor equilibrado, forte em qualidade, prazo e sustentabilidade. | 78000 |
| BETA | Fornecedor competitivo em preço e capacidade, com qualidade intermédia. | 65000 |
| GAMMA | Fornecedor muito sustentável, mas menos competitivo em preço e capacidade. | 82000 |
| DELTA | Fornecedor local de baixo custo, mas com limitações de qualidade e escala. | 59000 |

---

## 12. Matriz de avaliação exemplo

| Critério | ALPHA | BETA | GAMMA | DELTA |
|---|---|---|---|---|
| A1.1 Qualidade da Fruta | M (+50) | LM (+25) | N (0) | LP (-25) |
| A1.2 Preço / Custo Total | N (0) | M (+50) | LP (-25) | LM (+25) |
| A1.3 Prazo de Entrega | MM (+100) | LM (+25) | LM (+25) | N (0) |
| A1.4 Sustentabilidade | M (+50) | LP (-25) | MM (+100) | LP (-25) |
| A1.5 Fiabilidade / Reputação | LM (+25) | M (+50) | LM (+25) | N (0) |
| A1.6 Capacidade de Fornecimento | LM (+25) | M (+50) | LP (-25) | LP (-25) |

---

## 13. Resultado esperado do exemplo

Com os dados exemplo, a aplicação deve produzir o seguinte ranking base:

| Ranking | Alternativa | Valor Global aproximado |
|---:|---|---:|
| 1 | ALPHA | 41.89 |
| 2 | BETA | 29.05 |
| 3 | GAMMA | 12.16 |
| 4 | DELTA | -7.43 |

A recomendação principal deve ser:

```text
Fornecedor recomendado: ALPHA
```

---

## 14. Análise benefício/custo

A aplicação deve calcular uma métrica simples de benefício/custo:

```text
Benefício/Custo = Valor Global / (Custo / 1000)
```

Esta métrica é auxiliar e não substitui o ranking global.

---

## 15. Cenários de sensibilidade

A aplicação deve incluir cenários semelhantes aos slides.

### 15.1 Cenário Base

Mantém os pesos originais:

```text
A1.1 = 100
A1.2 = 80
A1.3 = 60
A1.4 = 50
A1.5 = 40
A1.6 = 40
```

### 15.2 Cenário A — Pesos iguais

Todos os critérios têm o mesmo peso.

Resultado esperado:

```text
ALPHA mantém o 1.º lugar.
```

### 15.3 Cenário B — +10% em Qualidade

Aumenta o peso da qualidade.

```text
A1.1 aumenta em 10 pontos.
```

Resultado esperado:

```text
ALPHA mantém ou reforça a liderança.
```

### 15.4 Cenário C — +10% em Preço

Aumenta o peso do preço/custo.

```text
A1.2 aumenta em 10 pontos.
```

Resultado esperado:

```text
BETA pode aproximar-se, mas ALPHA deve manter o 1.º lugar no exemplo base.
```

### 15.5 Cenário D — Sustentabilidade dominante

A sustentabilidade torna-se mais relevante.

```text
A1.4 = 100
```

Resultado esperado:

```text
GAMMA pode melhorar, mas ALPHA deve manter a recomendação no exemplo base.
```

---

## 16. Etapas do processo MCDA

A aplicação deve representar as 8 etapas discutidas nos slides:

1. Definir critérios;
2. Validar critérios;
3. Atribuir pesos;
4. Definir níveis de atratividade;
5. Definir escala de 7 níveis;
6. Avaliar alternativas;
7. Agregar resultados;
8. Análise de sensibilidade.

Estas etapas devem aparecer no dashboard inicial e orientar a navegação da aplicação.

---

## 17. Funcionalidades da aplicação

### 17.1 Dashboard

Deve apresentar:

- Nome da aplicação;
- Contexto do problema;
- As 8 etapas;
- Ranking resumido;
- Fornecedor recomendado;
- Gráfico de valor global.

### 17.2 Gestão da análise

Permitir editar:

- Nome;
- Descrição;
- Contexto;
- Metodologia;
- Responsável;
- Notas.

### 17.3 Gestão de alternativas

Permitir:

- Criar fornecedores;
- Editar fornecedores;
- Remover fornecedores;
- Definir custo estimado;
- Escrever descrição.

### 17.4 Gestão de critérios e pesos

Permitir:

- Criar critérios;
- Editar critérios;
- Remover critérios;
- Definir código;
- Definir nome;
- Definir peso;
- Definir fase;
- Ativar/desativar critérios;
- Indicar se o critério é de custo/risco;
- Mostrar pesos normalizados.
- Ao criar, alterar ou remover critérios, a matriz de avaliações deve ser sincronizada automaticamente, inicializando novos critérios com nível neutro `N`.
- Ao alterar o código de um critério, a aplicação deve tentar preservar as avaliações existentes quando a correspondência for inferível.
- Ao remover um critério, as respetivas entradas devem ser removidas de `scores` e `semantic_scores`.
- Se a análise não tiver critérios, a tabela deve surgir vazia mas com as colunas corretas e pronta para criação de novos critérios.

### 17.5 Escala de 7 níveis

Permitir visualizar:

- Código;
- Designação;
- Pontuação;
- Exemplo de referência.

### 17.6 Avaliação das alternativas

Permitir:

- Avaliar cada alternativa por critério usando dropdowns;
- Usar os níveis MM, M, LM, N, LP, P, MP;
- Visualizar matriz colorida.
- Ao ler uma nova análise JSON, a janela de avaliações deve ser recalculada/reinicializada para refletir os fornecedores, critérios e avaliações do novo ficheiro.

### 17.7 Resultados

Permitir:

- Calcular valor global;
- Mostrar ranking final;
- Mostrar fornecedor recomendado;
- Mostrar contribuições por critério;
- Exportar resultados para CSV.
- Exportar a análise completa para CSV;
- Exportar a análise completa para Excel;
- Exportar a análise completa para PDF.
- As exportações devem procurar incluir todos os dados disponíveis na aplicação: resumo, alternativas, critérios, escala, avaliações, matriz de avaliação, pontuações, resultados, contribuições, sensibilidade e robustez.
- A exportação Excel e PDF deve incluir uma matriz de avaliação colorida equivalente à matriz apresentada na interface.

### 17.8 Sensibilidade e robustez

Permitir:

- Correr cenários de sensibilidade;
- Comparar rankings por cenário;
- Mostrar se o vencedor base se mantém;
- Mostrar conclusão de robustez.

### 17.9 Ficheiros e JSON no menu lateral

O JSON deve ser gerido no menu lateral, sem uma tab final dedicada a JSON.

Permitir no menu lateral:

- Mostrar o nome da análise atual por baixo do logotipo `RETAILL_MCDA`;
- Botão `Nova Análise`, abrindo popup `Deseja Gravar a Análise Atual?` com opções `Sim`, `Não` e `Cancelar`;
- Em `Nova Análise`, a opção `Sim` deve abrir popup de gravação com nome editável, gravar, limpar a análise atual e depois pedir em popup o nome da nova análise;
- Em `Nova Análise`, a opção `Não` deve limpar a análise atual e pedir em popup o nome da nova análise;
- Em `Nova Análise`, a opção `Cancelar` deve voltar atrás sem alterar a análise atual;
- Botão `Ler Análise`, com popup inicial `Deseja Gravar a Análise Atual?` antes da seleção do ficheiro JSON;
- Em `Ler Análise`, a opção `Sim` deve gravar a análise atual e depois mostrar o seletor do JSON a ler;
- Em `Ler Análise`, a opção `Não` deve continuar diretamente para o seletor do JSON a ler;
- Em `Ler Análise`, a opção `Cancelar` deve voltar atrás sem alterar a análise atual;
- Ao ler um JSON, todas as etapas da aplicação devem passar a refletir imediatamente os dados da nova análise: metadados, alternativas, critérios, pesos, escala, avaliações, resultados, sensibilidade e robustez;
- A leitura de JSON deve reconstruir/sincronizar a matriz de avaliações para os critérios e alternativas do ficheiro carregado, inicializando valores em falta com `N`;
- Os editores e seletores da interface não devem manter valores visuais da análise anterior depois de uma nova análise ser lida ou criada;
- A matriz colorida critérios vs. produtores deve apresentar produtores nas linhas e critérios nas colunas, para suportar facilmente casos com muitos produtores e poucos critérios;
- A interface deve permitir filtrar visualmente gráficos e matrizes por `Top 5`, `Top 10` ou `Todos` os produtores, sem alterar os cálculos completos;
- Botão `Gravar Análise`, abrindo popup de gravação com nome de ficheiro JSON editável;
- Não deve existir botão separado `Descarregar JSON`; a gravação JSON é feita por `Gravar Análise`;
- Exportação da análise completa para CSV, Excel e PDF.

Estado recuperado no código: o fluxo `Nova Análise` / `Ler Análise` / `Gravar Análise` volta a ser conduzido por popups no menu lateral, a tab final de JSON não deve aparecer na navegação, o logotipo `RETAILL_MCDA` deve estar destacado na sidebar, a barra superior deve excluir esse logotipo e mostrar apenas os restantes logos em tamanho secundário, e as exportações completas CSV/Excel/PDF devem estar disponíveis no menu lateral.

---

## 18. Persistência de dados

A aplicação usa ficheiros JSON simples.

### 18.1 Exemplo de ficheiro principal

```text
data/fornecedores_fruta_alpha.json
```

### 18.2 Estrutura conceptual do JSON

```json
{
  "name": "Seleção de Fornecedores de Fruta",
  "description": "Modelo MCDA/MCDA para selecionar fornecedores de fruta numa cadeia de abastecimento.",
  "context": "Uma empresa de distribuição de fruta precisa selecionar fornecedores...",
  "methodology": "1fase",
  "alternatives": [],
  "criteria": [],
  "scores": {},
  "semantic_scores": {},
  "created_by": "MCDA Moderno",
  "notes": ""
}
```

---

## 19. Compatibilidade com o legacy

A aplicação legacy analisada parecia ser uma aplicação VB6 com:

- `Mmassiti.exe`;
- `Mmassiti.mdb`;
- ActiveX/OCX;
- Microsoft Jet OLEDB / Access;
- formulários como `frmCriterios`, `frmCustos`, `frmRelatorios`, `frmPrimeiraFase`, `frmSegundaFase`;
- módulos como `modFun`, `modMetodos`, `modDSN`.

Como o código-fonte VB6 original não estava disponível, a nova aplicação não é uma tradução linha-a-linha, mas uma **reimplementação funcional moderna**.

O objetivo é preservar os conceitos principais:

- análises;
- alternativas;
- critérios;
- pesos;
- níveis;
- avaliação;
- ranking;
- benefício/custo;
- sensibilidade;
- robustez;
- relatórios/exportação.

---

## 20. Limitações atuais

- A aplicação não garante equivalência matemática exata com o executável VB6 original.
- O algoritmo implementado é uma soma ponderada simples e auditável.
- Não há ainda sistema multiutilizador.
- Não há autenticação.
- Não há base de dados relacional.
- A exportação Excel/PDF é local e simples, orientada a protótipo.
- A análise de robustez ainda é baseada em cenários simples.

---

## 21. Evoluções recomendadas

### 21.1 Curto prazo

- Manter README atualizado com execução, teste rápido, screenshots e estado atual;
- Adicionar screenshots;
- Expandir testes unitários conforme novas funcionalidades forem adicionadas;
- Validar resultados com exemplos reais;
- Melhorar layout e conteúdo dos relatórios Excel/PDF;
- Melhorar cenários de sensibilidade.

### 21.2 Médio prazo

- Adicionar múltiplas metodologias MCDA;
- Permitir decisão em grupo;
- Permitir pesos por decisor;
- Calcular consenso entre decisores;
- Adicionar histórico de alterações;
- Adicionar comparação entre análises.

### 21.3 Longo prazo

- Migrar para uma arquitetura web completa;
- Backend FastAPI;
- Frontend React;
- Base de dados PostgreSQL;
- Gestão de utilizadores;
- Deploy cloud;
- Integração com sistemas empresariais;
- Importação/exportação estruturada.

---

## 22. Critérios de aceitação

Uma versão funcional mínima é aceite se:

- A aplicação arrancar com `streamlit run app.py`;
- Carregar o exemplo `fornecedores_fruta_alpha.json`;
- Mostrar os critérios e pesos definidos;
- Mostrar a escala de 7 níveis;
- Permitir avaliar alternativas;
- Calcular ranking final;
- Recomendar ALPHA no exemplo base;
- Mostrar análise de sensibilidade;
- Permitir criar nova análise no menu lateral;
- Permitir ler/importar análise JSON no menu lateral;
- Permitir gravar alterações em JSON no menu lateral;
- Permitir exportar a análise completa em CSV, Excel e PDF.

---

## 23. Comandos úteis

Instalar:

```bash
pip install -r requirements.txt
```

Executar:

```bash
streamlit run app.py
```

Teste rápido:

```bash
python smoke_test.py
```

---

## 24. Licença sugerida

Para um projeto académico ou demonstrador, recomenda-se uma licença permissiva:

```text
MIT License
```

Caso o projeto incorpore propriedade intelectual institucional ou empresarial, a licença deve ser definida antes da publicação pública.

---

## 25. README recomendado

O README deve começar com:

```markdown
# RETAILL_MCDA

## MCDA Moderno — Seleção de Fornecedores de Fruta
```

Evitar colocar o título principal no fim do ficheiro.

---

## 26. Estado atual

Estado do projeto:

```text
Protótipo funcional inicial com dashboard MCDA, gestão JSON no menu lateral, exportação CSV/Excel/PDF e testes unitários de cálculo.
```

Versão conceptual:

```text
v0.1.0
```

Próximo passo recomendado:

```text
Validar o exemplo com utilizadores e ajustar a metodologia/fórmulas se forem encontrados outputs de referência da aplicação legacy.
```
