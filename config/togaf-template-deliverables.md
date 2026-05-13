# TOGAF Template Deliverables Reference

Riferimento derivato dalla struttura del file locale `i094_1.zip` fornito dall'utente.

Usa questa tassonomia come struttura guida per `wiki/togaf/`. La reference contiene organizzazione, fasi, nomi dei deliverable e informazioni attese dedotte dalle intestazioni dei template. I contenuti delle pagine TOGAF devono essere generati esclusivamente dalla LLM Wiki principale e devono diventare documenti architetturali utilizzabili, non semplici indici.

## Regola di compilazione

- Per ogni deliverable crea o aggiorna una pagina solo se la wiki principale contiene informazioni utili.
- Se mancano dati, mantieni la sezione `Gap informativi` esplicita.
- Non copiare testo dei template: usa questa reference come checklist di copertura e struttura, non come contenuto documentale.
- Trasforma le informazioni disponibili in sintesi, ambito, contenuto documentale, analisi TOGAF, relazioni, decisioni/requisiti/vincoli e gap, mantenendo ogni affermazione tracciabile alla LLM Wiki.
- Nel metadato `Template di riferimento` usa il nome del deliverable qui riportato.

## Preliminary Phase

### Architecture Principles

Informazioni attese:
- scopo del documento, input e output;
- template dei principi;
- principi business;
- principi dati;
- principi applicativi;
- principi tecnologici.

### Architecture Repository

Informazioni attese:
- scopo del documento, input e output;
- landscape architetturale: architetture strategiche, segment e capability;
- reference library: overview, standard body, vendor, community, template, best practice, reference architecture, reference model, viewpoint library;
- standards library: standard legali, regolatori, industriali, organizzativi, business, data, application e technology;
- governance repository: decision log, compliance assessment, capability assessment, calendario, portfolio progetti, misure performance;
- solutions landscape;
- enterprise repository;
- repository esterni: reference model, standard, approvazioni Architecture Board;
- architecture capability: skill repository, struttura organizzativa, architecture charter.

### Business Principles, Goals, and Drivers

Informazioni attese:
- scopo del documento, input e output;
- contesto business per l'architettura;
- principi business;
- obiettivi business;
- driver business.

### Organizational Model for Enterprise Architecture

Informazioni attese:
- scopo del documento, input e output;
- organizzazioni impattate e relativo scope;
- maturity assessment, gap e approccio di risoluzione;
- ruoli e responsabilita del team architetturale, inclusa vista RACI se disponibile;
- vincoli sul lavoro architetturale;
- requisiti di budget;
- strategia di governance e supporto.

### Request for Architecture Work

Informazioni attese:
- scopo del documento, input e output;
- richiesta di lavoro architetturale e sponsor;
- missione organizzativa;
- obiettivi business e cambiamenti attesi;
- piani strategici business;
- cambiamenti dell'ambiente business;
- limiti temporali;
- vincoli organizzativi, di budget, esterni e business;
- informazioni aggiuntive: sistema business corrente, architettura/IT corrente, organizzazione di sviluppo, risorse disponibili.

### Tailored Architecture Framework

Informazioni attese:
- scopo del documento, input e output;
- metodo architetturale adattato;
- contenuto architetturale adattato, inclusi deliverable e artefatti;
- tool configurati e distribuiti;
- interfacce con governance model e framework: corporate business planning, enterprise architecture, portfolio/program/project management, system development/engineering, operations/services.

## Phase A - Architecture Vision

### Architecture Definition

Informazioni attese:
- scopo del documento, input e output;
- definizione architetturale: scope, goal, obiettivi, vincoli, principi, baseline architecture;
- modelli architetturali per gli stati modellati: business, data, application, technology;
- razionale e giustificazione dell'approccio architetturale;
- mapping verso repository: architecture landscape, reference model, standard, riuso;
- gap analysis;
- impatti sul landscape: architetture preesistenti, cambiamenti recenti, opportunita, altri progetti;
- transition architecture: stati di transizione e viste business, data, application, technology.

### Architecture Vision

Informazioni attese:
- scopo del documento, input e output;
- descrizione del problema;
- stakeholder e concern;
- issue o scenari da indirizzare;
- statement of architecture;
- viste di sintesi, inclusi value chain diagram e solution concept diagram se disponibili;
- requisiti stakeholder mappati;
- riferimento alla bozza di Architecture Definition Document.

### Capability Assessment

Informazioni attese:
- scopo del documento, input e output;
- business capability assessment: capability business, baseline performance, aspirazione futura, baseline capability, future capability, impatti organizzativi;
- IT capability assessment: maturity baseline/target dei processi di change e operation, capability baseline, capacity assessment, impatti IT;
- architecture maturity assessment: processi governance, organizzazione/ruoli/responsabilita, skill, landscape, standard, reference model, riuso;
- business transformation readiness assessment: fattori readiness, visione, rating corrente, rating target, rischi readiness.

### Communications Plan

Informazioni attese:
- scopo del documento, input e output;
- stakeholder;
- requisiti di comunicazione e overview;
- meccanismi di comunicazione;
- timetable comunicazione, milestone, durata, effort e risorse.

### Statement of Architecture Work

Informazioni attese:
- scopo del documento, input e output;
- titolo;
- richiesta progetto e background;
- descrizione progetto e scope;
- overview dell'Architecture Vision;
- procedure di cambio scope;
- ruoli, responsabilita e deliverable;
- piano e schedule del progetto architetturale;
- criteri e procedure di accettazione, inclusi metriche e KPI;
- approvazioni e firme.

## Phase B - Business Architecture

### Architecture Requirements Specification

Informazioni attese:
- scopo del documento, input e output;
- requisiti architetturali;
- misure di successo;
- contratti di servizio business;
- contratti di servizio applicativi;
- linee guida, specifiche e standard implementativi;
- requisiti di interoperabilita;
- requisiti di IT service management;
- vincoli;
- assunzioni.

### Architecture Roadmap

Informazioni attese:
- scopo del documento, input e output;
- candidate roadmap component per business, information systems e technology architecture;
- versione iniziale completa della roadmap;
- work package portfolio: descrizione, obiettivi, deliverable, requisiti funzionali, dipendenze, relazione con opportunita, ADD/ARS e valore business;
- implementation factor catalog: rischi, issue, assunzioni, dipendenze, azioni, input;
- matrice consolidata gap/soluzioni/dipendenze per dominio, gap, soluzioni potenziali e dipendenze;
- transition architecture;
- raccomandazioni implementative: misure di efficacia, rischi, issue, solution building block.

## Phase C - Information Systems Architecture

### Architecture Deliverables Phases C and D

Informazioni attese:
- artefatti architetturali per information systems;
- contenuti relativi a data architecture;
- contenuti relativi ad application architecture;
- relazioni con deliverable di Phase D quando applicabile;
- gap informativi se i dettagli data/application non sono presenti nelle fonti.

## Phase D - Technology Architecture

### Architecture Deliverables Phases C and D

Informazioni attese:
- artefatti architetturali per technology architecture;
- componenti tecnologici, piattaforme, infrastrutture e vincoli tecnologici;
- relazioni con deliverable di Phase C quando applicabile;
- gap informativi se i dettagli tecnologici non sono presenti nelle fonti.

## Phase E - Opportunities and Solutions

### Implementation and Migration Plan

Informazioni attese:
- scopo del documento, input e output;
- strategia di implementazione e migrazione;
- direzione strategica di implementazione;
- approccio di sequencing implementativo;
- breakdown progetto/portfolio dell'implementazione;
- allocazione work package a progetti o portfolio;
- capability consegnate dai progetti;
- milestone e timing;
- work breakdown structure;
- impatti su portfolio, programmi e progetti esistenti;
- project charter: work package inclusi, valore business, rischi, issue, assunzioni, dipendenze, risorse, costi, benefici, stime di opzioni di migrazione.

## Phase F - Migration Planning

### Architecture Building Blocks

Informazioni attese:
- scopo del documento e processo dei building block;
- building block: funzionalita fondamentale, attributi, semantica, security capability, manageability;
- interfacce: overview, interoperabilita, building block dipendenti;
- mapping verso entita business/organizzative e policy business/organizzative.

### Architecture Contract

Informazioni attese:
- scopo del documento, input e output;
- contratto di design e sviluppo architetturale: background, scope, principi, requisiti, conformita, ruoli di processo, misure target, deliverable di fase, workplan prioritizzato, finestre temporali, metriche architetturali e business;
- stakeholder architecture contract: background, requisiti strategici, obiettivi, scope, conformita, adopter, finestra temporale, metriche business, service architecture.

### Implementation Governance Model

Informazioni attese:
- scopo del documento, input e output;
- processi di governance e overview;
- struttura di governance;
- ruoli e responsabilita di governance;
- checkpoint di governance;
- criteri di successo/fallimento;
- procedura di accettazione.

## Phase G - Implementation Governance

### Compliance Assessment

Informazioni attese:
- scopo del documento, input e output;
- overview;
- checklist architetturali completate;
- checklist hardware e operating system;
- checklist software services e middleware;
- checklist applications;
- checklist information management;
- checklist security;
- checklist system management;
- checklist system engineering;
- checklist methods and tools.

### Solution Building Blocks

Informazioni attese:
- scopo del documento e processo dei building block;
- solution building block: funzionalita specifica, attributi, performance, configurabilita, driver, vincoli;
- interfacce: overview, interoperabilita, building block dipendenti, SBB richiesti;
- mapping SBB;
- relazioni tra SBB e ABB.

## Phase H - Architecture Change Management

### Change Request

Informazioni attese:
- scopo del documento, input e output;
- dettagli base della change request;
- descrizione del cambiamento;
- razionale e impatti del cambiamento;
- driver del cambiamento;
- razionale del cambiamento;
- impatti previsti;
- requirements impact assessment.

### Requirements Impact Assessment

Informazioni attese:
- scopo del documento, input e output;
- dettagli base;
- impact assessment;
- raccomandazioni;
- raccomandazioni sulla gestione dei requisiti.
