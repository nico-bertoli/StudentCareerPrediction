# distribuire tentativi in modo omogeneo nel tempo (2,3,2 tentativi per ogni punto di previsione)
# possibilita di dare in output un csv con i dati da dare in pasto al modello
# inserire peso features
# provare tpot per regressione
# fai modello che prevede se uno studente e' attivo al secondo anno in base ai tentativi che fa
# calcolo ic16 considerando come inattivi gli studenti che non fanno piu tentativi di esame
# -----

# possibilita di dare in output un json con i dati da dare in pasto al modello

# esportare modello (possibilmente in json)

################################################################################################# FEATURES NON UTILIZZATE
#   ANNO_ARRIVO_ATENEO  -> ARRIVO DELLO STUDENTE IN ATENEO  
#   MOTIVO_CARRIERA     -> IMM (studente non laureato che non ha mai fatto la rinuncia agli studi), RIN(rinuncia agli studi), TIT(laureato)
#   DATA_CHIUSURA       -> QUANDO LO STUDENTE SI È LAUREATO
#   ANNO_CORSO          -> ANNO IN CUI SI SVOLGONO LE LEZIONI DELL' ESAME

#   AA_OFF_ID           -> ANNO IN CUI L' ESAME E' PROPOSTO ALLO STUDENTE
#   RIC_ID              -> 0 -> esame fatto, 2/4 -> tipo di riconoscimento ()
#   TIPO_RIC_COD        -> descrive meglio RIC_DI
#   SOVRAN_FLG			-> X
#   DEBITO_FLG			-> X
#   LIBERA_FLG			-> X
#   NO_MEDIA_FLG		-> X
#   MAT_ID				-> codice identificativo esame  X
#   COD					-> CODICE IDENTIFICATIVO ESAME  X
#   DATA_MAX_APPELLO    -> DATA IN CUI LO STUDENTE HA PROVATO PER L' ULTIMA VOLTA L' APPELLO (MOLTI SONO MANCANTI ANCHE NEL CASO LO STUDENTE ABBIA PASSATO L' ESAME)
#   NUMERO              -> TENTATIVI FATTI DALLO STUDENTE
################################################################################################# FEATURES UTILIZZATE
#   STUD_ID             -> ID STUDENTE

#   ANNO_AVVIO_CARRIERA -> AVVIO DELLA CARRIERA DELLO STUDENTE

#   DES                 -> NOME ESAME
#   PESO                -> CREDITI ESAME
#   STA_SCE_COD         -> STATO ESAME ??? S = SUPERATO,F=FALLITO,  P=???
#   VOTO                -> VOTO PRESO
#   LODE_FLG            -> 0 = NO LODE, 1 = LODE
#   DATA_FREQ           -> DATA FINE LEZIONI *
#   DATA_SUP            -> DATA SUPERAMENTO ESAME *
#   DATA_PRIMO_APPELLO  -> DATA IN CUI LO STUDENTE HA PROVATO PER LA PRIMA VOLTA L' APPELLO *

#   feature create da me:
#   GIORNI_ESAME_PASSATO    -> DOPO QUANTI GIORNI DOPO LA FINE DELLE LEZIONI LO STUDENTE HA PASSATO L' ESAME
#   GIORNI_ESAPE_PROVATO    -> DOPO QUANTI GIONRI DOPO LA FINE DELLE LEZIONI LO STUDENTE HA PROVATO PER LA PRIMA VOLTA L' ESAME
##################################################################################################### SELECT SUL DB

#pd.isna            -> vero se valore = NaN
#pd.notna           -> vero se valore = !NaN






# SETTINGS

#esami sulla base dei quali voglio fare la previsione (vuoto = tutti gli esami)
from pickle import FALSE


ESAMI_TOTALI = [
    'ALGEBRA E GEOMETRIA',
    'ALGORITMI E STRUTTURE DATI I',
    'ANALISI MATEMATICA',
    'ARCHITETTURA DEGLI ELABORATORI',
    'FISICA',
    'FONDAMENTI DI PROGRAMMAZIONE A - FONDAMENTI DI PROGRAMMAZIONE B',
    'INGLESE B1'
    ]
ESAMI_TOTALI.sort()   #metto in ordine alfabetico

ESAMI_PRIMO_SEMESTRE = [
    'ARCHITETTURA DEGLI ELABORATORI',
    'ANALISI MATEMATICA',
    'INGLESE B1',
]
ESAMI_PRIMO_SEMESTRE.sort()

#   colonne del db che servono al programma per funzionare
colonneUtilizzate = ['STU_ID',
                    'DES',
                    'PESO',
                    'STA_SCE_COD',
                    'VOTO',
                    'LODE_FLG',
                    'NUMERO',
                    'AA_OFF_ID',
                    'ANNO_AVVIO_CARRIERA',
                    'DATA_FREQ',
                    'DATA_MAX_APPELLO',
                    'DATA_SUP',
                    'DATA_PRIMO_APPELLO',
                    'DATA_CHIUSURA'
                    ]


#il classificatore andrà a distinguere tra studenti con cfu >= CFU_RICHIESTI e studenti con CFU < CFU_RICHIESTI
CFU_RICHIESTI = 40

# mese nel quale si vuole fare la previsione
# MESE_RIFERIMENTO = 3       # previsione a fine sessione invernale
# MESE_RIFERIMENTO = 7     # previsione a fine sessione estiva
# MESE_RIFERIMENTO = 9     # previsione a fine sessione autunnale
MESE_RIFERIMENTO = 12

#vuoi usare tpot per cercare un modello?
USE_TPOT = False
GENERATIONS = 100
POP_SIZE = 100

#numero di addestramenti su cui valutare le prestazioni dei modelli
NLOOP = 1

#vuoi esportare X ed y in formato csv?
ESPORTA_DATI = False

#NON MODIFICARE, valore dato al numero di giorni in cui un esame e' passato/provato, nel caso non sia mai stato passato/provato
GIORNI_ESAME_NON_SUPERATO = GIORNI_ESAME_MAI_PROVATO = 99999999

VERDE = '#1f9c23'
ROSSO = '#db0000'
BLU = '#1061e3'
GIALLO = '#ffbb00'
VIOLA = '#7c00bf'
ARANCIONE = '#ff6a00'

ALGEBRA = 0
ALGORITMI = 1
ANALISI = 2
ARCHITETTURA = 3
FISICA = 4
FONDAMENTI = 5
INGLESE = 6