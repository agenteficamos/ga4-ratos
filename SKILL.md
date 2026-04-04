---
name: ga4-ratos
description: Consulta dados do Google Analytics 4 via SDK oficial (google-analytics-data). Le propriedades, gera relatorios de sessoes, usuarios, pageviews, bounce rate, conversoes, fontes de trafego, landing pages, campanhas UTM, dispositivos, geo e dados em tempo real. Use quando o usuario mencionar google analytics, ga4, analytics, sessoes, usuarios, pageviews, bounce rate, fontes de trafego, landing pages, campanhas utm, tempo real, realtime, dados do site, comportamento do site, trafego do site, conversoes ga4. Tambem dispara com /ga4-ratos setup.
---

# GA4 Ratos

Skill completa para consulta de dados do Google Analytics 4 via SDK oficial (`google-analytics-data`). Gera relatorios de sessoes, usuarios, pageviews, bounce rate, conversoes, fontes de trafego, landing pages, campanhas UTM, dispositivos, geo e dados em tempo real.

**IMPORTANTE: Esta skill e o braco de execucao para GA4. Para inteligencia (diagnostico, auditoria, estrategia), use a skill ads-ratos como camada acima.**

**IMPORTANTE: Esta skill e separada do google-ads-ratos porque muita gente usa Meta Ads + GA4 sem Google Ads. Porem, se o usuario ja tem google-ads-ratos configurado, as credenciais OAuth podem ser compartilhadas.**

**IMPORTANTE: NUNCA usar MCPs (adloop, google-analytics-mcp, etc). Esta skill usa SOMENTE os scripts Python locais.**

## Setup (primeira vez)

Quando o usuario pedir para configurar, rodar setup, ou for a primeira vez usando a skill, o Claude deve guiar o setup interativo:

### 1. Verificar dependencias

```bash
pip3 install google-analytics-data google-auth
```

### 2. Verificar .env

Checar se existe `~/.claude/skills/ga4-ratos/.env`. Se NAO existir, criar com o template:

```
# GA4 Ratos — Configuracao
# Os scripts leem este arquivo automaticamente. NAO precisa adicionar ao ~/.zshrc.

# OBRIGATORIO: Property ID do GA4 (ex: 123456789, sem "properties/")
GA4_PROPERTY_ID=""

# AUTH — Escolha UM dos dois modos:

# MODO 1: Service Account (mais simples pra GA4)
# Baixe o JSON da service account no Google Cloud Console
# e coloque o path completo aqui:
GA4_CREDENTIALS_PATH=""

# MODO 2: OAuth2 (compartilhado com google-ads-ratos)
# Se voce ja tem google-ads-ratos configurado, pode reusar as credenciais:
# GA4_CLIENT_ID=""
# GA4_CLIENT_SECRET=""
# GA4_REFRESH_TOKEN=""
# Ou deixe em branco e o script busca automaticamente no .env do google-ads-ratos.
```

**Modo 1 (Service Account):** Mais simples. Cria uma service account no Google Cloud Console, da acesso de leitura na propriedade GA4, baixa o JSON e coloca o path em `GA4_CREDENTIALS_PATH`.

**Modo 2 (OAuth2):** Se o usuario ja tem `google-ads-ratos` configurado com OAuth, os scripts buscam automaticamente as credenciais de `~/.claude/skills/google-ads-ratos/.env`. Nao precisa configurar nada extra.

### 3. Cadastro de propriedades (contas.yaml) — SETUP CONVERSACIONAL

Depois que o `.env` estiver preenchido, o Claude DEVE proativamente guiar o cadastro:

1. Rodar `read.py account` para verificar acesso a propriedade
2. Perguntar ao usuario: "Qual o site/app principal? Me passa o nome do cliente, e eu preencho o contas.yaml pra ti."
3. Para cada cliente, perguntar:
   - Nome do cliente
   - Property ID do GA4
4. Preencher o `contas.yaml` automaticamente com as respostas
5. Perguntar: "Quer cadastrar mais algum cliente?"

## Cadastro de clientes (contas.yaml)

**Arquivo:** `~/.claude/skills/ga4-ratos/contas.yaml`

Antes de executar qualquer operacao, o Claude DEVE ler este arquivo para resolver nomes de clientes para property IDs.
Quando o usuario disser "analytics do Meu Cliente" ou "sessoes da Meu Cliente", consultar o contas.yaml
para obter o property_id do cliente.

Se o cliente nao estiver cadastrado, perguntar os dados e oferecer para adicionar ao arquivo.

## Como usar

Todos os scripts estao em `~/.claude/skills/ga4-ratos/scripts/`. O padrao e:

```
python3 <script>.py <subcomando> [argumentos]
```

O Claude deve interpretar o pedido do usuario e executar o script correto via Bash.

---

## Referencia rapida de operacoes

### Leitura (read.py)

| Subcomando | O que faz | Exemplo |
|---|---|---|
| `properties` | Lista propriedades GA4 acessiveis | `read.py properties` |
| `account` | Detalhes de uma propriedade (nome, timezone, currency) | `read.py account --property 123456789` |

### Relatorios (reports.py) — CORE DA SKILL

| Subcomando | O que faz | Exemplo |
|---|---|---|
| `overview` | Resumo geral (sessoes, usuarios, pageviews, bounce rate, conversoes) | `reports.py overview --date-range 30daysAgo` |
| `traffic-sources` | Fontes de trafego (source/medium) com metricas | `reports.py traffic-sources --date-range 7daysAgo` |
| `landing-pages` | Paginas de destino com bounce rate e conversoes | `reports.py landing-pages --date-range 30daysAgo --limit 20` |
| `campaigns` | Performance de campanhas UTM (source, medium, campaign) | `reports.py campaigns --date-range 30daysAgo` |
| `conversions` | Eventos de conversao com contagem e valor | `reports.py conversions --date-range 30daysAgo` |
| `devices` | Breakdown por dispositivo (desktop, mobile, tablet) | `reports.py devices --date-range 7daysAgo` |
| `geo` | Breakdown por pais/cidade | `reports.py geo --date-range 30daysAgo` |
| `daily` | Evolucao diaria de metricas | `reports.py daily --start-date 2026-03-01 --end-date 2026-03-31` |
| `custom` | Query custom (metricas e dimensoes livres) | `reports.py custom --dimensions date,sessionSource --metrics sessions,totalUsers` |

Parametros comuns:

| Parametro | O que faz | Exemplo |
|---|---|---|
| `--property` | Property ID do GA4 | `123456789` |
| `--date-range` | Periodo relativo | `7daysAgo`, `30daysAgo`, `90daysAgo`, `365daysAgo` |
| `--start-date` | Data inicio | `2026-03-01` |
| `--end-date` | Data fim | `2026-03-31` |
| `--limit` | Limite de linhas | `50` |

### Tempo real (realtime.py)

| Subcomando | O que faz | Exemplo |
|---|---|---|
| `now` | Usuarios ativos agora, paginas sendo vistas, fontes | `realtime.py now` |
| `events` | Eventos em tempo real | `realtime.py events` |

---

## Regras de seguranca

O Claude DEVE seguir estas regras ao executar operacoes:

1. **Somente leitura** — GA4 Ratos e uma skill de consulta, NAO modifica dados
2. **Nunca hardcodar property IDs ou credenciais** — sempre usar env vars ou contas.yaml
3. **Respeitar rate limits** — se receber erro de quota, aguardar 60 segundos antes de tentar novamente
4. **Nunca assumir origem de dados** — ao mostrar metricas, SEMPRE especificar o periodo e a propriedade consultada
5. **NUNCA usar MCPs** — esta skill usa SOMENTE os scripts Python locais, NUNCA tools de MCP (adloop, google-analytics-mcp, etc)

## Fluxos comuns

### Visao geral do site

1. `reports.py overview --date-range 30daysAgo` — resumo geral
2. `reports.py traffic-sources --date-range 30daysAgo` — de onde vem o trafego
3. `reports.py devices --date-range 30daysAgo` — desktop vs mobile
4. `reports.py landing-pages --date-range 30daysAgo --limit 10` — principais paginas

### Analise de campanhas UTM

1. `reports.py campaigns --date-range 30daysAgo` — performance por campanha
2. `reports.py traffic-sources --date-range 30daysAgo` — source/medium detalhado
3. `reports.py landing-pages --date-range 30daysAgo` — onde o trafego esta chegando

### Monitoramento em tempo real

1. `realtime.py now` — quem esta no site agora
2. `realtime.py events` — o que estao fazendo

### Evolucao diaria

1. `reports.py daily --start-date 2026-03-01 --end-date 2026-03-31` — serie temporal
2. Comparar com periodo anterior para identificar tendencias

### Diagnostico de bounce rate alto

1. `reports.py landing-pages --date-range 30daysAgo --limit 20` — paginas com maior bounce
2. `reports.py devices --date-range 30daysAgo` — se mobile tem bounce maior
3. `reports.py traffic-sources --date-range 30daysAgo` — se alguma fonte tem bounce anomalo
