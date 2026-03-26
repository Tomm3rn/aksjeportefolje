# Slik legger du aksjeportefølje-appen på internett

Dette er en komplett steg-for-steg-guide. Du trenger ikke teknisk kunnskap.
Hele prosessen tar ca. 20–30 minutter første gang.

---

## Oversikt over hva vi gjør

1. Opprette en **GitHub-konto** – et sted å lagre koden din på nett
2. Installere **Git** – et program som laster opp koden til GitHub
3. Laste opp koden til GitHub
4. Opprette en **Render-konto** – gratis tjeneste som kjører appen på nett
5. Koble Render til GitHub og starte appen

---

## STEG 1 – Opprett GitHub-konto

GitHub er som en skylagring for kode. Helt gratis.

1. Åpne nettleseren og gå til: **https://github.com**
2. Klikk på den grønne knappen **Sign up**
3. Fyll inn:
   - E-postadresse
   - Passord (husk det!)
   - Brukernavn (f.eks. `tomfrederik` – kun bokstaver, tall og bindestrek)
4. Klikk **Continue** gjennom stegene og velg **Free**-planen
5. Bekreft e-posten din (GitHub sender en e-post med en kode)

Du er nå logget inn på GitHub.

---

## STEG 2 – Opprett et nytt repo på GitHub

Et "repo" er mappen der koden din lagres på GitHub.

1. Når du er logget inn på GitHub, klikk på **+**-tegnet øverst til høyre
2. Velg **New repository**
3. Fyll inn:
   - **Repository name:** `aksjeportefolje`
   - La alt annet stå som det er
4. Klikk den grønne knappen **Create repository**
5. Du ser nå en side med instruksjoner. **La denne siden være åpen** – du trenger den i steg 4.

---

## STEG 3 – Installer Git på PCen din

Git er et gratis program som lar deg laste opp filer til GitHub fra PCen din.

1. Gå til: **https://git-scm.com/download/win**
2. Nedlastingen starter automatisk. Hvis ikke, klikk på lenken for 64-bit
3. Åpne den nedlastede filen og installer med alle standardvalg (bare klikk **Next** hele veien og til slutt **Install**)
4. Når installasjonen er ferdig, klikk **Finish**

**Verifiser at Git er installert:**
1. Trykk `Windows-tasten`, skriv `cmd` og trykk **Enter**
2. Et sort vindu åpner seg (dette er terminalen)
3. Skriv `git --version` og trykk **Enter**
4. Du skal se noe som `git version 2.x.x` – da fungerer det!

---

## STEG 4 – Last opp koden til GitHub

Nå skal vi sende koden fra PCen din til GitHub.

1. Åpne terminalen (det sorte vinduet fra forrige steg, eller søk på `cmd` igjen)
2. Kopier og lim inn disse kommandoene **én om gangen**. Trykk **Enter** etter hver:

```
cd C:\Users\lehrm\Claude\aksjeportefolje
```
*(dette navigerer deg til mappen der koden ligger)*

```
git init
```
*(klargjør mappen for opplasting)*

```
git add .
```
*(velger alle filer for opplasting)*

```
git commit -m "første versjon"
```
*(lagrer en snapshot av koden)*

```
git branch -M main
```
*(setter opp hoved-grenen)*

**Nå trenger du GitHub-brukernavnet ditt:**
```
git remote add origin https://github.com/DITT-BRUKERNAVN/aksjeportefolje.git
```
> Bytt ut **DITT-BRUKERNAVN** med brukernavnet du valgte på GitHub (f.eks. `tomfrederik`)

```
git push -u origin main
```
*(laster opp koden til GitHub)*

Når du kjører siste kommando vil GitHub be om brukernavn og passord.
- **Brukernavn:** GitHub-brukernavnet ditt
- **Passord:** Her må du bruke et "Personal Access Token" i stedet for vanlig passord (GitHub godtar ikke vanlig passord lenger). Se neste avsnitt.

### Lage et Personal Access Token (PAT) på GitHub:
1. Gå til **https://github.com/settings/tokens**
2. Klikk **Generate new token** → **Generate new token (classic)**
3. Gi det et navn, f.eks. `aksjeportefolje`
4. Under **Expiration**, velg **No expiration**
5. Huk av boksen ved siden av **repo**
6. Scroll ned og klikk **Generate token**
7. **Kopier tokenet** (det vises bare én gang!) – det ser ut som `ghp_xxxxxxxxxxxxxx`
8. Bruk dette tokenet som passord når Git spør

Hvis alt gikk bra ser du noe som `Writing objects: 100%` i terminalen.
Refresh GitHub-siden i nettleseren – du skal nå se filene dine der!

---

## STEG 5 – Opprett Render-konto og deploy appen

Render er tjenesten som kjører appen din på internett. De har en gratis plan.

1. Gå til: **https://render.com**
2. Klikk **Get Started for Free**
3. Klikk **Continue with GitHub** og logg inn med GitHub-kontoen din
4. Godkjenn at Render får tilgang til GitHub

### Deploy appen:
1. Inne på Render, klikk **New +** øverst til høyre
2. Velg **Blueprint**
3. Du ser nå GitHub-repoene dine. Klikk **Connect** ved siden av **aksjeportefolje**
4. Render finner automatisk `render.yaml`-filen og foreslår oppsett
5. Gi tjenesten et navn (f.eks. `aksjeportefolje`) eller behold forslaget
6. Klikk **Apply**

Render begynner nå å bygge og starte appen. Dette tar **2–5 minutter**.
Du kan se fremdriften i loggen på skjermen.

### Når appen er klar:
- Du ser en grønn tekst **Live** ved siden av tjenestenavn
- URL-en din vises øverst, f.eks.: `https://aksjeportefolje.onrender.com`

---

## STEG 6 – Del med vennen din

1. Kopier URL-en fra Render (f.eks. `https://aksjeportefolje.onrender.com`)
2. Send den til vennen din på SMS eller e-post
3. Dere åpner begge nettsiden i nettleseren
4. Klikk **Opprett konto** og lag hvert deres brukernavn og passord
5. Dere ser nå kun sin egen portefølje

---

## Viktig å vite om gratisplanen

- Render sin gratis plan **sover** etter 15 minutter uten besøk
- Første gang du åpner siden etter en pause tar det **30–60 sekunder** å våkne
- Etter det er den rask som normalt
- Vil du ha den alltid rask kan du oppgradere til betalt plan ($7/mnd)

---

## Noe gikk galt?

De vanligste problemene:
- **Git spør om passord:** Bruk Personal Access Token (se Steg 4)
- **"Permission denied" ved push:** Sjekk at brukernavnet i kommandoen stemmer med GitHub-brukernavnet ditt
- **Render bygger men krasjer:** Vent 5 minutter og sjekk loggen – gi beskjed til Tom i Claude så hjelper han deg

---

*Laget med Claude – mars 2026*
