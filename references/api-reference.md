# GA4 Data API - Referência de Métricas e Dimensões

Referência rápida das métricas e dimensões mais úteis do Google Analytics 4 Data API v1.

---

## Métricas mais usadas

### Usuários e Sessões

| Métrica | Descrição |
|---|---|
| `activeUsers` | Usuários ativos no período |
| `totalUsers` | Total de usuários |
| `newUsers` | Novos usuários |
| `sessions` | Total de sessões |
| `sessionsPerUser` | Sessões por usuário |
| `engagedSessions` | Sessões com engajamento (>10s ou conversão ou 2+ pageviews) |
| `engagementRate` | Taxa de engajamento (engagedSessions / sessions) |
| `bounceRate` | Taxa de rejeição (1 - engagementRate) |

### Tempo e Navegação

| Métrica | Descrição |
|---|---|
| `averageSessionDuration` | Duração média da sessão (segundos) |
| `userEngagementDuration` | Tempo total de engajamento |
| `screenPageViews` | Total de pageviews |
| `screenPageViewsPerSession` | Pageviews por sessão |
| `screenPageViewsPerUser` | Pageviews por usuário |

### Eventos e Conversões

| Métrica | Descrição |
|---|---|
| `eventCount` | Total de eventos |
| `eventCountPerUser` | Eventos por usuário |
| `eventValue` | Valor total dos eventos |
| `conversions` | Total de conversões |
| `userConversionRate` | Taxa de conversão por usuário |
| `sessionConversionRate` | Taxa de conversão por sessão |

### E-commerce

| Métrica | Descrição |
|---|---|
| `ecommercePurchases` | Total de compras |
| `purchaseRevenue` | Receita total |
| `averagePurchaseRevenue` | Receita média por compra |
| `totalRevenue` | Receita total (inclui ad revenue) |
| `addToCarts` | Adições ao carrinho |
| `checkouts` | Checkouts iniciados |
| `purchaserConversionRate` | Taxa de conversão de compra |
| `cartToViewRate` | Taxa carrinho/visualização |

### Publicidade

| Métrica | Descrição |
|---|---|
| `advertiserAdClicks` | Cliques em ads |
| `advertiserAdCost` | Custo de ads |
| `advertiserAdCostPerClick` | CPC |
| `advertiserAdImpressions` | Impressões de ads |
| `returnOnAdSpend` | ROAS |

---

## Dimensões mais usadas

### Tempo

| Dimensão | Descrição | Exemplo |
|---|---|---|
| `date` | Data (YYYYMMDD) | 20260401 |
| `dateHour` | Data + hora | 2026040114 |
| `dayOfWeek` | Dia da semana (0=dom) | 1 |
| `hour` | Hora do dia | 14 |
| `month` | Mês | 04 |
| `week` | Semana do ano | 14 |
| `year` | Ano | 2026 |

### Fonte de Tráfego

| Dimensão | Descrição | Exemplo |
|---|---|---|
| `sessionSource` | Fonte da sessão | google |
| `sessionMedium` | Mídia da sessão | cpc |
| `sessionCampaignName` | Nome da campanha | black_friday_2026 |
| `sessionDefaultChannelGroup` | Canal padrão | Paid Search |
| `firstUserSource` | Primeira fonte do usuário | facebook |
| `firstUserMedium` | Primeira mídia do usuário | social |
| `firstUserCampaignName` | Primeira campanha | lancamento_q1 |
| `source` | Fonte (evento) | google |
| `medium` | Mídia (evento) | organic |
| `campaignName` | Campanha (evento) | retargeting |

### Página e Conteúdo

| Dimensão | Descrição | Exemplo |
|---|---|---|
| `landingPage` | Página de destino | /produtos |
| `pagePath` | Caminho da página | /blog/post-1 |
| `pageTitle` | Título da página | Home - Meu Site |
| `unifiedScreenName` | Nome da tela/página | Home |
| `contentGroup` | Grupo de conteúdo | Blog |

### Dispositivo e Tecnologia

| Dimensão | Descrição | Exemplo |
|---|---|---|
| `deviceCategory` | Categoria | desktop, mobile, tablet |
| `operatingSystem` | SO | Android, iOS, Windows |
| `browser` | Navegador | Chrome, Safari |
| `screenResolution` | Resolução | 1920x1080 |

### Geografia

| Dimensão | Descrição | Exemplo |
|---|---|---|
| `country` | País | Brazil |
| `city` | Cidade | São Paulo |
| `region` | Estado/Região | São Paulo |
| `continent` | Continente | Americas |

### Eventos

| Dimensão | Descrição | Exemplo |
|---|---|---|
| `eventName` | Nome do evento | page_view, purchase |
| `isConversionEvent` | É conversão? | true, false |

### Demografia

| Dimensão | Descrição | Exemplo |
|---|---|---|
| `userAgeBracket` | Faixa etária | 25-34 |
| `userGender` | Gênero | male, female |

---

## Exemplos de queries comuns

### 1. Visão geral dos últimos 30 dias

```
Dimensões: (nenhuma)
Métricas: sessions, totalUsers, newUsers, screenPageViews, bounceRate, averageSessionDuration, conversions
DateRange: 30daysAgo → today
```

### 2. Fontes de tráfego

```
Dimensões: sessionSource, sessionMedium
Métricas: sessions, totalUsers, bounceRate, conversions
DateRange: 30daysAgo → today
OrderBy: sessions DESC
```

### 3. Landing pages com bounce rate

```
Dimensões: landingPage
Métricas: sessions, bounceRate, averageSessionDuration, conversions
DateRange: 30daysAgo → today
OrderBy: sessions DESC
Limit: 20
```

### 4. Evolução diária

```
Dimensões: date
Métricas: sessions, totalUsers, screenPageViews, bounceRate
DateRange: 30daysAgo → today
OrderBy: date ASC
```

### 5. Performance de campanhas UTM

```
Dimensões: sessionSource, sessionMedium, sessionCampaignName
Métricas: sessions, totalUsers, bounceRate, conversions
DateRange: 30daysAgo → today
OrderBy: sessions DESC
```

### 6. Dispositivos

```
Dimensões: deviceCategory
Métricas: sessions, totalUsers, bounceRate, averageSessionDuration
DateRange: 30daysAgo → today
```

### 7. E-commerce

```
Dimensões: sessionSource, sessionMedium
Métricas: sessions, ecommercePurchases, purchaseRevenue, returnOnAdSpend
DateRange: 30daysAgo → today
OrderBy: purchaseRevenue DESC
```

### 8. Tempo real — Páginas ativas

```
Dimensões: unifiedScreenName
Métricas: activeUsers
(Realtime Report — sem DateRange)
```

---

## Benchmarks BR (referência rápida)

| Métrica | CRÍTICO | ATENÇÃO | BOM | EXCELENTE |
|---|---|---|---|---|
| Bounce rate (LP de ads) | > 80% | 60-80% | 40-60% | < 40% |
| Tempo médio na página | < 15s | 15-30s | 30-60s | > 60s |
| Taxa conversão (sessão → lead) | < 1% | 1-3% | 3-5% | > 5% |
| Páginas por sessão | < 1.2 | 1.2-1.5 | 1.5-2.5 | > 2.5 |

Fonte: ads-ratos/references/benchmarks-br.md
