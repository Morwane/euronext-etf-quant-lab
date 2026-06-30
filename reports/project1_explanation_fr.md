# Project 1 - ETF Market-Quality & Fair-Value Analytics

## Idee simple

Le but est de verifier si un ETF se traite proprement sur le marche.

Un ETF de bonne qualite doit avoir:

- un bid-ask spread faible;
- un prix proche de sa NAV ou iNAV;
- une tracking error faible par rapport a son benchmark;
- une volatilite et un drawdown coherents avec son exposition;
- une liquidite suffisante.

## Pourquoi c'est interessant pour Euronext

Euronext est une place de cotation. Pour les ETFs, la qualite de marche est centrale: spreads, liquidite, profondeur, efficacite du prix, attractivite pour les emetteurs et les market makers.

Ce projet montre que je comprends le lien entre donnees de marche, qualite d'execution, ETF fair value et monitoring quantitatif.

## Donnees LSEG necessaires

Version minimale:

- prix daily, par exemple `TRDPRC_1`;
- historique de l'ETF;
- benchmark ETF ou indice.

Version complete:

- `BID`;
- `ASK`;
- `NAV` ou champ NAV equivalent disponible sur LSEG;
- volume;
- eventuellement iNAV intraday ou order-book si disponible.

## Ce que le code fait

1. Charge les donnees ETF.
2. Calcule les spreads si BID/ASK existent.
3. Calcule premium/discount si NAV existe.
4. Calcule tracking error vs SPY.
5. Calcule volatilite realisee, beta, drawdown.
6. Classe les ETFs par score de deterioration de qualite de marche.

## Phrase entretien

I built an ETF market-quality monitor using LSEG data. The goal is to identify ETFs where trading quality deteriorates: wider spreads, larger premium/discount to NAV, higher tracking error, higher volatility or worse drawdown. The project is relevant for an exchange because ETF market quality affects issuers, liquidity providers and end investors.

## Limite honnete

Le cache local actuel contient surtout des prix daily. Donc on peut deja faire tracking error, vol, beta et drawdown. Pour prouver les vrais spreads et premium/discount, il faut lancer le script LSEG avec Workspace ouvert afin de recuperer BID, ASK et NAV.

