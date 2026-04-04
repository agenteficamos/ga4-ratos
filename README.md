# GA4 Ratos

Skill do ecossistema Ratos para consulta de dados do Google Analytics 4 via SDK oficial (`google-analytics-data`).

## O que faz

- Consulta propriedades e detalhes de conta GA4
- Gera relatórios de sessões, usuários, pageviews, bounce rate, conversões
- Analisa fontes de tráfego (source/medium), landing pages, campanhas UTM
- Breakdown por dispositivo e geolocalização
- Dados em tempo real (usuários ativos, páginas, eventos)
- Query customizada com métricas e dimensões livres

## Pré-requisitos

```bash
pip3 install google-analytics-data google-auth
```

## Configuração

Crie o arquivo `~/.claude/skills/ga4-ratos/.env`:

```
GA4_PROPERTY_ID="123456789"

# Opção 1: Service Account
GA4_CREDENTIALS_PATH="/path/to/service-account.json"

# Opção 2: OAuth2 (compartilhado com google-ads-ratos)
# Deixe GA4_CREDENTIALS_PATH vazio — busca automaticamente do google-ads-ratos
```

## Uso

```bash
# Resumo geral dos últimos 30 dias
python3 scripts/reports.py overview --date-range 30daysAgo

# Fontes de tráfego
python3 scripts/reports.py traffic-sources --date-range 7daysAgo

# Dados em tempo real
python3 scripts/realtime.py now
```

## Ecossistema Ratos

- **meta-ads-ratos** — Gestão de Meta Ads (Facebook/Instagram)
- **google-ads-ratos** — Gestão de Google Ads
- **ga4-ratos** — Consulta de dados GA4 (este)
- **ads-ratos** — Camada de inteligência (diagnóstico, auditoria, estratégia)
