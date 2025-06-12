# Kontekstno-odvisen informacijski agent za sledenje cen delnic

Avtorji
- Filip Aljaž Stoapr
- Ervin Haraćič

## Povzetek
V današnjem hitro spreminjajočem se finančnem okolju je dostop do ažurnih in natančnih informacij o delnicah ključnega pomena za vlagatelje, analitike in podjetja. Ročno iskanje in analiziranje podatkov iz različnih virov je zamudno in lahko vodi do netočnih odločitev. Zato smo v tem projektu razvili kontekstno-odvisnega informacijskega agenta, ki samodejno pridobiva, analizira in posreduje podatke in napovedi o cenah 25-ih delnic. Cilj je bilo ustvariti agenta, ki dostopa do finančnih API-jev v realnem času, najde trenutne podatke o delnici, napove prihodno vrednost delnic in njihovo rast/padanje ter obvešča uporabnika. Cilj smo dosegli s pomočjo nevronskih mrež med katerimi so se najbolje izkazali GRU in LSTM→GRU (hibrid). 


## Uvod
V sodobnem finančnem svetu se trg vrednostnih papirjev hitro spreminja, kar od vlagateljev, analitikov in drugih deležnikov zahteva nenehno spremljanje in hitro odzivanje na nove informacije. Ker so podatki o delnicah razpršeni po različnih spletnih virih in finančnih platformah, njihovo ročno zbiranje in obdelava postajata vse bolj neučinkovita ter podvržena napakam. Pojavlja se potreba po avtomatiziranih rešitvah, ki bi omogočale zanesljiv, hiter in kontekstno prilagojen dostop do ključnih informacij.

V okviru tega projekta smo se osredotočili na razvoj informacijskega agenta, ki znadostopati do podatkovnih virov (prek API-jev), analizirati zgodovinske in trenutne podatke ter na podlagi tega ustvariti napovedi gibanja cen delnic. Agent uporablja metode strojnega učenja, predvsem nevronske mreže (LSTM, GRU), za razpoznavo vzorcev v časovnih vrstah.

Cilj naloge je bil ustvariti sistem, ki podpira inteligentno odločanje na področju finančne analize. V nadaljevanju poročila predstavimo sorodna dela, uporabljene metode, podrobnosti implementacije, rezultate testiranj in ključne ugotovitve.

## Sorodna dela
Za napoved vrednosti delnic sem se odločil za uporabo modelov LSTM in GRU za napovedovanje, saj so se ti pristopi izkazali za učinkovite v številnih predhodnih raziskavah.

Na primer, Talharti idr. (2025) so v svoji študiji primerjali napovedno učinkovitost modelov umetnih nevronskih mrež (ANN) in LSTM pri napovedovanju gibanja desetih delnic iz indeksa MADEX na Casablanski borzi. Ugotovili so, da LSTM dosledno prekaša ANN pri vseh izbranih časovnih horizontih (10, 20 in 30 dni), predvsem zaradi sposobnosti zaznavanja dolgoročnih vzorcev in trendov v časovnih vrstah. Avtorji v zaključku priporočajo nadaljnje raziskave z uporabo modelov GRU in SVM za dodatno izboljšanje natančnosti in robustnosti, kar dodatno potrjuje primernost vključitve GRU v mojo raziskavo.

Podobno Kulkarni idr. (2024) predstavijo sistem za napovedovanje borznih cen, ki temelji na arhitekturi LSTM in uporablja zgodovinske podatke (OHLC vrednosti) iz Yahoo Finance. Njihov model uspešno zajema tako kratkoročne kot dolgoročne odvisnosti v podatkih in s tem dosega višjo natančnost napovedi v primerjavi z obstoječimi pristopi. Avtorji izpostavljajo prednosti LSTM, kot so obvladovanje nelinearnosti, prepoznavanje kompleksnih vzorcev ter izboljšana učinkovitost pri obdelavi finančnih časovnih vrst.

Dodatno primerjalno študijo sta izvedla Vatsal Patel in Dr. Saurabh Tandel (2024), ki sta analizirala delnice treh velikih indijskih podjetij (TCS, Reliance, Infosys) z uporabo modelov LSTM in GRU, obogatenih s tehničnimi indikatorji (RSI, MACD, Bollinger Bands). Vključenost teh indikatorjev je pri obeh modelih večinoma znižala napako (RMSE in MAE), vendar učinek ni bil enoten za vse delnice. Rezultati kažejo, da LSTM v povprečju dosega višjo natančnost, GRU pa prednjači po hitrosti izvajanja zaradi enostavnejše arhitekture. Zaključek njune študije izpostavlja pomen prilagoditve modela in vhodnih značilnosti posameznemu finančnemu instrumentu, kar je pomembna usmeritev tudi za naš raziskovalni pristop.

Na podlagi rezultatov vseh treh študij smo se tudi mi odločili za uporabo modelov LSTM in GRU, saj omogočajo učinkovito analizo volatilnih in kompleksnih finančnih časovnih vrst ter napovedovanje gibanja borznih cen z večjo stopnjo zanesljivosti. Moji rezultati se ne čisto ujemajo z ugotovitvami omenjenih raziskav – LSTM je v večini primerov dosegel nekoliko nižjo natančnost kot GRU. To potrjuje, da je GRU kljub manjši arhitekturni kompleksnosti ustrezna alternativa LSTM, zlasti pri nalogah, kjer je ključna učinkovitost ob podobni napovedni zmogljivosti. 



## Metodologija
Namen te raziskave je razviti inteligentnega agenta, ki samodejno analizira časovne vrste podatkov o delnicah in napoveduje njihovo prihodnjo vrednost ter smer gibanja (rast/padec). Zasnovali smo sistem, ki združuje dve instanci nevronskih modelov – kratkoročno in dolgoročno – ter omogoča kombinirano analizo svežih in zgodovinskih tržnih trendov.
### Raziskovalna vprašanja
  1. Kako lahko agent samostojno posodablja svoje modele in deluje brez nadzora uporabnika?
  2. A obstaja povezava med natančnostjo napovedi točnih vrednosti delnic in napovedi rasti/padanja vrednosti delnice?
  3. Primerjava učinkovitosti različnih modelov.
### Izbor metod in utemeljitev
Za reševanje zgoraj navedenih vprašanj smo se odločili za uporabo metod globokega učenja, saj so le-te še posebej učinkovite pri napovedovanju časovnih vrst. 
Med eksperimentalnim postopkom smo testirali pet različnih modelnih arhitektur in na podlagi rezultatov izbrali dve najboljši za vključitev v končno rešitev.

Uporaba dveh instanc (zgodovinska in tekoča) omogoča modelu več perspektiv – dolgotrajni trendi pomagajo zmanjševati vpliv kratkoročnih šumov, medtem ko sveži podatki omogočajo odzivnost na aktualna dogajanja.
### KONČNA IMPLEMENTACIJA AGENTA   
### 1. Struktura sistema

1. **Uvoz in predobdelava podatkov**  
   - Podatke o delnicah pridobivamo prek Alpha Vantage API-ja in Yfinance API-ja.    
   - Pridobljene podatke shranjujemo:  
     1. V relacijsko bazo (poenostavljen dostop za agenta). Obdržimo izvorno obliko podatkov.  
     2. V CSV datoteke za vsak simbol posebej (za lažjo gradnjo in ponovno uporabo modelov). Iz .csv odstranimo vse podatke razen (`Close`) cene.   

2. **Dve instanci modelov**  
   Za boljše napovedi agenta uporabljamo dve ločeni instanci modelov:

   **Utemeljitev**  
   - **Kratkoročna nihanja**  
     Modeli, usposobljeni na zadnjih dveh mesecih, bolje zajamejo sveža tržna gibanja in kratkoročna nihanja cen.  
   - **Dolgoročni vzorci**  
     Zgodovinski modeli zajamejo dolgoročne sezonske in makroekonomske vplive, kar pomaga zmehčati prekomerno prilagajanje kratkoročnim šokom.

   **1. Dolgotrajna (zgodovinska) instanca**  
   - **Obseg podatkov:** podatki za 25 delnic shranjeni v .csv, obdobje od **25. marca 2023** do **23. marca 2025**.  
   - **Modeli:**  
     - **GRU** – napovedovanje točne cene  
     - **LSTM → GRU** – klasifikacija rasti/padanja  
   - **Postopek:**  
     1. Enkratno usposabljanje nad dvema letoma zgodovinskih podatkov.  
     2. Integracija usposobljenih modelov v sistem za klic napovedi (brez ponovnega treniranja pri vsakem zagonu).

   **2. Kratkoročna (tekoča) instanca**  
   - **Obseg podatkov:**podatki za25 delnic shranjenih v bazi, obdobje zadnja **2 meseca**. Podatk iv bazi se dinamično posodabljajo (vsak zagon sistem prevzame nove podatke zadnjih dveh mesecev).  
   - **Postopek ob vsakem zagonu:**  
     1. Agent prevzame nove cene in posodobi bazo.  
     2. Ponovno zgradi **GRU** in **LSTM → GRU** modele na svežih podatkih (enaki namen modelov kot pri zgodovinski instanci).  
     3. Uporabi jih za generiranje dnevnih napovedi.
     
3. **Uporabniški vmesnik**
   - Agent vsebuje uporabniški vmesnik, ki umogoča uporabniku, da si lahko izbere delnico. Agent mu s pomočjo svojih 4 modelov napove vrednost delnice za naslednji dan in rast/padec vrednosti delnice v prihodnosti (Pri tem mu modoela naučena na dogotrajni instanci in kratkoročni instanci vrneta ločena rezultata). Glede na rezultate obeh modelov agent poda uporabniko priporočilo.          

4. **Redno posodabljanje in samostojno delovanje**  
   - Agent posodobi bazo vsakič ko naredi napoved.  
   - Agent lahko deluje samostojno, kjer uporabnik določi čas, ob katerem dnevno agent sam posodobi svojo bazo, izračuna napovedi in obvesti uporabnika na Discord strežniku s uporabo spletnega kavlja.



### Tehnične podrobnosti:
- Program je napisan v Pythonu,
- Modeli so bili usposobljeni z uporabo “sliding window” okna dolžine 3,
- Vsak model je bil treniran 100-krat čez celoten učni niz,
- Podatki o modelih:

    | Model                   | Arhitektura                                                        |
    |-------------------------|---------------------------------------------------------------------|
    | **Model2a: Čisti GRU**  | `Input(shape=(n,1)) → GRU(64) → Dense(32, activation='relu') → Dense(1)` |
    | **Model2b: LSTM→GRU**   | `Input(shape=(n,1)) → LSTM(64, return_sequences=True) → GRU(64) → Dense(32, activation='relu') → Dense(1)` |



## Poskusi in rezultati
Da bi kar najbolj natančno napovedali gibanje cene delnice (tako absolutne vrednosti kot njen trend), smo izvedli primerjalni eksperiment. V njem smo preverili, kateri model daje napovedi najbližje dejanski ceni in kateri najzanesljiveje predvidi naraščanje ali padanje. Kodo uporabljeno pri eksperimentu lahko najdete na https://github.com/Stocks-agent-org/Stocks-agent.
### Potek eksperimenta

1. **Priprava podatkov**  
   - Ustvarili smo vzorce, kjer vsak vzorec vsebuje tri zaporedne dnevne zaključne cene in ciljno naslednjo ceno.
   - Korpus podatkov obsega vsak dan med 2023-03-25 in 2025-03-23 pri čemer smo uporabljali "close".  

2. **Razdelitev na sklope**  
   - Prvih 80 % smo uporabili za učenje, naslednjih 10 % za validacijo in zadnjih 10 % za testiranje.  
   
3.  **MODELI:**
  
    **LSTM z gostimi plastmi**  
       - Arhitektura:  
         - En LSTM-sloj s 64 enotami  
         - Dva gosta sloja po 32 nevronov (ReLU)  
         - En izhodni nevron za napoved cene  
       - Model smo trenirali 100-krat čez učni sklop.

    **LSTM → 1D konvolucija → LSTM**  
       - Predhodno smo vse vrednosti preskaliral v [0, 1] glede na učni sklop.  
       - Arhitektura:  
         - LSTM-sloj s 64 enotami (vračanje zaporedij)  
         - Konvolucijski 1D-sloj z 32 filtri in velikostjo okna 2  
         - Drugi LSTM-sloj s 64 enotami  
         - Gost sloj s 32 nevroni (ReLU) in izhodni nevron  
       - Tudi tega semo trenirali 100-krat z validacijskim spremljanjem.

    **Rolling-window**  
       - Podatke smo razdelil po mesecih in izvedeli 11 korakov: za vsak par zaporednih mesecev smo model izučili na prvem mesecu (20 iteracij) in ga preizkusil na naslednjem.  
    
    **Čisti GRU**  
       - Predhodna normalizacija: vse vrednosti smo skalirali v [0, 1] glede na učni sklop.  
       - Arhitektura:  
         - GRU-sloj s 64 skritimi enotami  
         - Gost sloj s 32 nevroni (ReLU)  
         - En izhodni nevron za napoved cene  
       - Model smo trenirali 100-krat čez učni sklop.

    **Hibrid LSTM → GRU**  
       - Predhodna normalizacija: enaka kot pri čistem GRU modelu.  
       - Arhitektura:  
         - LSTM-sloj s 64 enotami (`return_sequences=True`)  
         - GRU-sloj s 64 enotami  
         - Gost sloj s 32 nevroni (ReLU)  
         - En izhodni nevron  
       - Model smo prav tako trenirali 100-krat čez učni sklop..

4. **Končna evalvacija**  
   - Na testnem sklopu smo za pet modelov (preprost LSTM, LSTM→Conv1D→LSTM, čisti GRU, hibrid LSTM→GRU in rolling window) izračunali:  
     - MAE (povprečna absolutna napaka), MSE (povprečna kvadratna napaka), RMSE (koren srednje kvadratne napake), MAPE (povprečna odstotna napaka), R² (koeficient determinacije)  in delež pravilno napovedane smeri giba.  
   - Vse rezultate smo združil v eno tabelo.
5. **Končna evalvacija modelov**

| Model                  | MAE   | MSE    | RMSE  | MAPE (%) | R²     | Dir. Acc. (%) |
|------------------------|-------|--------|-------|-----------|--------|----------------|
| LSTM z gostimi plastmi | 5.91  | 46.94  | 6.85  | 2.09      | 0.244  | 52.0           |
| LSTM → Conv1D → LSTM   | 7.28  | 88.80  | 9.42  | 2.60      | –0.430 | 48.0           |
| Čisti GRU              | 5.72  | 42.77  | 6.54  | 2.02      | 0.311  | 52.0           |
| LSTM → GRU (hibrid)    | 6.71  | 59.84  | 7.74  | 2.38      | 0.036  | 56.0           |
| Rolling-window model   | 6.95  | 67.07  | 8.19  | 2.46      | –0.080 | 48.0           |
6. **Analiza rezultatov**
  
    **Najbolj natančen model (glede na MAE in RMSE):**

    **Čisti GRU** dosega najnižji **MAE (5.72)** in najnižji **RMSE (6.54)** med vsemi modeli.  
    Prav tako ima najnižji **MAPE (2.02 %)**, kar pomeni, da so napovedi v povprečju najmanj odstopale od pravih vrednosti v odstotkih.  

    To pomeni, da je **GRU model napovedoval cene najbližje dejanskim vrednostim**.

    ---

    **Najboljši pri napovedovanju smeri (ali delnica raste/pada):**

    **LSTM → GRU (hibridni model)** ima najvišjo **Directional Accuracy – 56 %**.  
    Čeprav ima ta model nekoliko slabšo natančnost pri napovedani vrednosti (višji MAE in RMSE kot GRU), **najbolje prepozna smer gibanja cene**.

    ---
    **Ugotovitev**
    
    Najboljši model za napovedovanje vrednosti delnic je Čisti GRU, najboljši pri napovedovanju smeri pa LSTM → GRU (hibrid). Za to smo pri gradnji agenta uporabili ta dva modela. LSTM z gostimi plastmi je konkurenčen (MAE 5.91, RMSE 6.85), vendar nekoliko zaostaja. LSTM → Conv1D → LSTM je bil najmanj uspešen pri napovedovanju vrednosti (najvišji MAE, RMSE in najnižji R²), kar kaže na prekomerno kompleksnost ali slabšo ujemanje z značajem podatkov. Čeprav je model  LSTM → GRU (hibrid) najboljši pri napovedanju rasti/padanje vrednosti delinice, je njegova natančnost samo 56 % kar je rahlo nad naključjem. To nam pove, da je delnice zelo težko napovedati, glede na časaovno zaporedje saj na njih vplivajo mnogi zunanji faktorji. LSTM → GRU (hibrid) je imel tudi najvišji Dir. Acc. (%), kljub temu, da so njegove MAE,MSE in RMSE bile slabše od LSTM z gostimi plastmi in Čisti GRU. Iz tega sklepamo, da bližina napovedi pravi vrednosti delnice ni nujno znak, da bo model dobro znal napovedati rast/padanje.  
## Zaključek
V projektu smo uspešno razvili kontekstno-odvisnega informacijskega agenta za sledenje cenam delnic, ki z uporabo dveh nevronskih arhitektur (GRU in LSTM→GRU) zagotavlja samodejno napovedovanje tako točnih vrednosti delnic kot tudi njihovega gibanja (rast/padec). Sistem temelji na dveh ločenih instancah (kratkoročni in dolgoročni), kar omogoča bolj zanesljivo napovedovanje v spremenljivem tržnem okolju. Eksperimenti so pokazali, da model GRU v povprečju dosega boljšo napovedno zmogljivost kot LSTM.

Agent je zasnovan kot avtonomni sistem, sposoben redne posodobitve svojih podatkov in modelov ter podaje personaliziranih napovedi uporabniku prek uporabniškega vmesnika in obvestilnega sistema (Discord). Rešitev torej omogoča zanesljivo in odzivno spremljanje dogajanja na borzi brez stalnega človeškega nadzora.

V prihodnje bi bilo smiselno raziskati možnosti vključitve dodatnih zunanjih dejavnikov (npr. novice, sentiment iz družbenih omrežij) ter razširiti nabor tehničnih indikatorjev. Nadalje bi lahko agentu dodali funkcionalnosti za optimizacijo portfeljev ali celo samodejno trgovanje, kar bi še dodatno povečalo njegovo uporabnost v resničnih finančnih okoljih.

## Viri
1. https://www.researchgate.net/profile/Xu-Huang-37/publication/380756642_Understanding_the_planning_of_LLM_agents_A_survey/links/664d5a9dbc86444c72f64b6f/Understanding-the-planning-of-LLM-agents-A-survey.pdf
2. https://xploreqa.ieee.org/stamp/stamp.jsp?tp=&arnumber=6072968
3. https://xploreqa.ieee.org/stamp/stamp.jsp?tp=&arnumber=9167404
4. https://www.researchgate.net/publication/388190054_Comparative_Analysis_of_Generative_LSTM_Models_with_Other_AI_Techniques
5. https://www.researchgate.net/publication/391644818_Machine_Learning_for_Stock_Price_Prediction_on_the_Casablanca_Stock_Exchange_A_Comparative_Study_of_ANN_and_LSTM_Approaches
6. https://www.researchgate.net/publication/390570409_Stock_Price_Prediction_Using_LSTM
7. https://www.researchgate.net/publication/391633283_A_Comparative_Analysis_of_LSTM_and_GRU_Models_Enhanced_with_Technical_Indicators_for_Stock_Forecasting
8. https://github.com/Stocks-agent-org/Stocks-agent


