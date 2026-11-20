# PSYOPSNEWS AI-redaktion

## Pipeline
1. **Nyhetsjägaren** samlar RSS-nyheter och metadata med länkar och publiceringsdatum.
2. **Källgranskaren** markerar belagda påståenden, osäkerhet och saknade belägg.
3. **Redaktionschefen** väljer vinkel och program.
4. **Satirförfattaren** skriver skämt med grovt språk men utan påhittade verkliga citat.
5. **Dialogförfattaren** fördelar repliker mellan karaktärerna.
6. **Karaktärsagenten** bevarar dialekter och personlighet.
7. **Producenten** skapar strukturerad dialog-JSON som videomotorn kan läsa.

Dessa är definierade agentroller och arbetssteg, inte ännu sex autonoma LLM-processer. v0.3 kan samla RSS och skapa idéunderlag automatiskt; LLM-manus kräver separat modell-API.

## Program
- bear: Björnen har ordet – ilsken stockholmsk satir.
- journalist: Journalisten granskar – torr småländsk ton.
- rock: Rockbrudens Backstage – musik, metal, bred stockholmska.
- panel: Tre idioter och en mikrofon – alla tre, längre dialog.

## Redaktionella regler
Märk påhittade inslag SATIR. Använd länkar och datum för faktiska nyheter. Skriv inte fabricerade uttalanden som om verkliga personer sagt dem. För varje verklighetsbaserat manus: separera källfakta från komiska påhitt.
