from tkinter import NE
import imports
from imports import *
import settings
from settings import*
import funzioni
from funzioni import *

#=========================================================================
# CARICO I DATI
print('carico il dataframe')
df = pd.read_excel('data/Informatica.xlsx')
print('dataframe caricato: ')
display(df[0:3])

print('\n=============================\n')

#=========================================================================
# CONSIDERO SOLO LE COLONNE CHE MI INTERESSANO
print('elimino le colonne che non mi interessano')
df = df[colonneUtilizzate]
display(df[0:3])

print('\n=============================\n')

#=========================================================================
# ELIMINO GLI ESAMI CHE NON SONO DEL PRIMO ANNO
print('elimino gli esami che non sono del primo anno')
righeIniziali = df.shape[0]
print('righe iniziali: ',righeIniziali)
if(len(ESAMI_TOTALI) != 0): df = df[df['DES'].isin(ESAMI_TOTALI)]
#report
print('righe eliminate: ',righeIniziali-df.shape[0])
print('righe rimanenti: ',df.shape[0])
print('\n=============================\n')
#=========================================================================
# IN RARI CASI HO PESO NON VALIDO, SISTEMO
modificati = 0
for i in df.index:
    des = df.loc[i,'DES']
    if des == 'FISICA' or des == 'ALGEBRA E GEOMETRIA' or des == 'ALGORITMI E STRUTTURE DATI I' or des == 'ANALISI MATEMATICA':
        if df.loc[i,'PESO'] != 9: modificati+=1
        df.loc[i,'PESO'] = 9
    elif des == 'INGLESE B1':
        if df.loc[i,'PESO'] != 3: modificati+=1
        df.loc[i,'PESO'] = 3
    elif des == 'FONDAMENTI DI PROGRAMMAZIONE A - FONDAMENTI DI PROGRAMMAZIONE B':
        if df.loc[i,'PESO'] != 15: modificati+=1
        df.loc[i,'PESO'] = 15
    elif des == 'ARCHITETTURA DEGLI ELABORATORI':
        if df.loc[i,'PESO'] != 6: modificati+=1
        df.loc[i,'PESO'] = 6

print('PESI sistemati: ',modificati)

#========================================================================= 
# segno gli esami contrassegnati con 'P' con 'F'

print('segno gli esami contrassegnati con \'P\' con \'F\'')
cont = 0
for i in df.index:
    a = df.loc[i,'STA_SCE_COD']
    if(a!='S'and a!='F'):
        cont +=1
        df.loc[i,'STA_SCE_COD'] = 'F'
print('ho sistemato ',cont,' esami')
print('\n=============================\n')

#========================================================================= 
# ORDINO GLI ESAMI IN ORDINE ALFABETICO

print('ordino gli esami in ordine alfabetico')
df = df.sort_values(by='DES')
display(df)
print('\n=============================\n')
#========================================================================= 
# ELIMINO GLI ORARI DA DATA_SUP, DATA_FREQ, DATA_PRIMO_APPELLO, DATA_MAX_APPELLO
print('elimino gli orari dalle date\n')

print('prima:\n')
print(df.iloc[0])
# SEMPLIFICO DATA_FREQ
vDataFreq = df['DATA_FREQ']     #vecchio
nDataFreq = []                  #nuovo

for elem in vDataFreq:
    if pd.isna(elem):
        nDataFreq.append(elem)
    else:
        nDataFreq.append(elem[0:10])

df['DATA_FREQ'] =   nDataFreq

#   SEMPLIFICO DATA_SUP
dateComplete = df['DATA_SUP']
dateAnni = []
for elem in dateComplete:
    if pd.isna(elem):
        dateAnni.append(elem)
    else:
        dateAnni.append(elem[0:10])

df['DATA_SUP'] = dateAnni

#   SEMPLIFICO DATA_PRIMO_APPELLO

vDataPrimoApp = df['DATA_PRIMO_APPELLO']
nDataPrimoApp = []

for elem in vDataPrimoApp:
    if pd.isna(elem):
        nDataPrimoApp.append(elem)
    else:
        nDataPrimoApp.append(elem[0:10])

df['DATA_PRIMO_APPELLO'] = nDataPrimoApp

# SEMPLIFICO DATA_MAX_APPELLO
vData = df['DATA_MAX_APPELLO']     #vecchio
nData = []                  #nuovo

for elem in vData:
    if pd.isna(elem):
        nData.append(elem)
    else:
        nData.append(elem[0:10])

df['DATA_MAX_APPELLO'] = nData

#SEMPLIFICO DATA_CHIUSURA
vDataChius = df['DATA_CHIUSURA']     #vecchio
nDataChius = []                      #nuovo

for elem in vDataChius:
    if pd.isna(elem):
        nDataChius.append(elem)
    else:
        nDataChius.append(elem[0:10])

df['DATA_CHIUSURA'] =   nDataChius

#report
print('\ndopo :\n')
print(df.iloc[0])
print('\n=============================\n')

#========================================================================= 
# AGGIUNGO LA COLONNA "PRIMO_ANNO" AL DATAFRAME, CHE INIDICA IL PRIMO ANNO EFFETTIVO DI OGNI STUDENTE

# Cerco il minimo degli anni in cui lo studente ha seguito le lezioni di un corso (aMinimo).
# Probabilmente questo `e il primo anno dello studente.
# A questo punto imposto il primo anno dello studente come:

# 􏰀 aMinimo se l’ anno di avvio della carriera dello studente +1 corrisponde ad aMinimo. 
# Questo caso `e quello piu` comune, in cui lo studente si iscrive in un certo anno 
# (per esempio a luglio, al termine delle superiori) e poi inizia a dare gli esami l’ anno successivo (verso gennaio/febbraio).
# (il 92.8 % degli esami rientrano in questo caso)
# 􏰀 aMinimo se l’ anno di avvio della carriera dello studente corrisponde a primoAnnoCorsoSeguito. Faccio cosi perch`e,
#  dalle osservazioni che ho fatto, questo caso si verifica principalmente quando lo studente si `e iscritto dopo gennaio.
# (l’ 1.2 % degli esami rientrano in questo caso)
# 􏰀 in tutti gli altri casi lo imposto come anno avvio carriera +1. Questa cosa potrebbe generare inconsistenze, 
# ma mi sembra il modo migliore con cui gestirla (il 5.9 % degli esami rientrano in questo caso)

print('aggiungo la colonna \'primo anno\' al dataframe')

primoAnno = []
# caso1 = 0
# caso2 = 0
# caso3 = 0

for i in df.index:

    matricola = df.loc[i,'STU_ID']
    avvCar = df.loc[i,'ANNO_AVVIO_CARRIERA']
    primoACorsoSeg = getAnnoInizioFrequentazioneLezioni(df,matricola)
    annoSup = df.loc[i,'DATA_SUP']

    if pd.notna(annoSup):
        annoSup = str(annoSup)[0:4]
        annoSup = int(annoSup)
    
    #caso normale (lo studente si iscrive in un certo anno e frequenta lezioni di quell' anno)
    if avvCar+1 == primoACorsoSeg: 
        primoAnno.append(primoACorsoSeg)
        # caso2+=1
    
    #caso in cui lo studente si è iscritto dopo gennaio
    elif avvCar == primoACorsoSeg :
        primoAnno.append(primoACorsoSeg)
        # caso1+=1
        # print(df.loc[i],'\n')

    #se non riesco a stimare con precisione l' anno di inizio, lo imposto come anno avvio carriera +1
    #   questa cosa potrebbe generare dell' errore ma non saprei come altro fare dato che a volte i dati sono incoerenti
    else: 
        primoAnno.append(avvCar+1)
        # caso3+=1

df['PRIMO_ANNO'] = primoAnno
# print('caso1: ',caso1)
# print('caso2: ',caso2)
# print('caso3: ',caso3)

print('\n=============================\n')
#========================================================================= 

#sistemo questo studente per cui ho visto che il primo anno e' sbagliato
for i in df.index:
    if df.loc[i,'STU_ID']==267757: df.loc[i,'PRIMO_ANNO']=2016
#========================================================================= 
#numero di esami e di studenti per anno

#numero di esami per ogni anno
anni = []
for i in df.index: anni.append(df.loc[i,'PRIMO_ANNO'])
anni = uniq(anni)

print('numero di esami negli anni:')
for anno in anni:
    print('numero di esami nell\' anno ',anno,': ',len(df[df['PRIMO_ANNO']==anno]))

#numero di studenti per ogni anno
somme = np.zeros((len(anni)))
matr = calcolaMatricole(df)

for i in range(len(anni)):
    for j in range(len(matr)):
        if matr[j].iloc[0,14] == anni[i]: somme[i] +=1

print('numero di studenti negli anni:')
for i in range(len(anni)):
    print('numero di studenti nell\' anno ',anni[i],': ',somme[i])
#========================================================================= 
# gestisco i casi in cui manca DATA_FREQ
#  In 139 casi(5.1% del totale) manca la data di fine lezioni

#   sistemo andando a cercare il data freq di uno studente che ha dato la stessa materia nello stesso anno

print('correggo i data_freq mancanti')

fine_lezioni = df['DATA_FREQ']
correzioniFatte = 0
printed = False

#-----------report iniziale
da_correggere = []
for i in df.index:
    if(pd.isna(df.loc[i,'DATA_FREQ'])):
        
        anno = df.loc[i,'PRIMO_ANNO']
        esame = df.loc[i,'DES']
        dataFreqCorretta = -1

        for j in df.index:
            primoAnnoAltro = df.loc[j,'PRIMO_ANNO']
            annoDataFreq = df.loc[j,'DATA_FREQ']

            if type(annoDataFreq)==str:
                annoDataFreq = annoDataFreq[0:4]
            if primoAnnoAltro == anno and df.loc[j,'DES'] == esame and annoDataFreq==anno:
                dataFreqCorretta= df.loc[j,'DATA_FREQ']
                break
        
        #se non risesco a trovare un valore tra i dati degli altri studenti, imposto il primo anno dello studente seguito da un mese e giorno
        #in base a se l' esame e' nel primo o secondo semestre
        if(dataFreqCorretta == -1):
            dataFreqCorretta = df.loc[i,'PRIMO_ANNO']
            dataFreqCorretta = str(dataFreqCorretta)
            if (esame in( ESAMI_PRIMO_SEMESTRE)):
                dataFreqCorretta = dataFreqCorretta + '-01-15'
            else:
                print(dataFreqCorretta)
                dataFreqCorretta = dataFreqCorretta + '-06-10'         
        
        if not printed:
            display(df.loc[i])

        df.loc[i,'DATA_FREQ']=dataFreqCorretta
        correzioniFatte +=1

        if not printed:
            printed = True
            display(df.loc[i])

print('correzioni fatte: ',correzioniFatte)

print('\n=============================\n')

#========================================================================= 
# questa colonna non mi serve più
print('elimino la colonna ANNO AVVIO CARRIERA')
df.drop('ANNO_AVVIO_CARRIERA',axis=1,inplace=True)
print('\n=============================\n')
#=========================================================================
# CALCOLO LA FEATURE GIORNI_ESAME_PASSATO (GIORNI DOPO I QUALI LO STUDENTE HA PASSATO L' ESAME)
#   GIORNI_ESAME_NON_SUPERATO               ->  esame non superato
#   numero giorni                           ->  esame superato dopo questi giorni

print('calcolo la feature \'GIORNI ESAME PASSATO\'')

#   conteggio di quanti giorni sono passati prima che lo studente desse l' esame
giorniSup = []
#   date ultima lezione per esame
date_ultime_lez = df['DATA_FREQ']
#   date superamento
date_sup = df['DATA_SUP']
risultati = df['STA_SCE_COD']

for i in df.index:
    #se ho passato l' esame calcolo dopo quanti giorni
    if risultati[i]=='S':
        
        #per ogni riga ottengo le date che mi interessano
        strUltimaLez = date_ultime_lez[i]
        strSup = date_sup[i]

        #   sostituisco - con / nelle stringhe
        strUltimaLez = strUltimaLez.replace('-','/')
        strSup = strSup.replace('-','/')
        #   calcolo degli oggetti data a partire dalle stringhe
        dataUltimaLez = datetime.strptime(strUltimaLez,'%Y/%m/%d')
        dataSup = datetime.strptime(strSup,'%Y/%m/%d')
        dataSup = dataSup.date()
        dataUltimaLez = dataUltimaLez.date()

        delta = dataSup - dataUltimaLez
        #estraggo i giorni
        delta = delta.days
        
        

        #   calcolo dopo quanti giorni dalla fine delle lezioni lo studente ha dato l' esame, e lo aggiungo all' array della nuova feature
        giorniSup.append(delta)

    #se non ho passato l' esame segno -1
    else:
        giorniSup.append(GIORNI_ESAME_NON_SUPERATO)

del(strSup)
del(strUltimaLez)

df['GIORNI_ESAME_PASSATO']=giorniSup

#========================================================================= 
# CALCOLO LA FEATURE GIORNI_ESAME_PROVATO (GIORNI DOPO I QUALI LO STUDENTE HA PROVATO L' ESAME PER LA PRIMA VOLTA)

#   GIORNI_ESAME_MAI_PROVATO              ->  prima prova mai fatta   (modificare?)
#   -2              ->  inconsistenza dati
#   numero giorni   ->  esame provato dopo questi giorni

print('calcolo la feature \'GIORNI ESAME PROVATO\'')

#   conteggio di quanti giorni sono passati prima che lo studente desse l' esame
giorniProv = []
#   date ultima lezione per esame
date_ultime_lez = df['DATA_FREQ']
#   date superamento
date_prima_prov = df['DATA_PRIMO_APPELLO']
risultati = df['STA_SCE_COD']

for i in df.index:
    #   per ogni riga ottengo le date che mi interessano
    strUltimaLez = date_ultime_lez[i]
    strPrimaProv = date_prima_prov[i]

    #   caso prima prova mai fatta (data prima prova = nan)
    if(pd.isna(strPrimaProv)):
        giorniProv.append(GIORNI_ESAME_MAI_PROVATO)
    
    #   altrimenti calcolo il numero di giorni dopo cui è stata fatta la prima prova
    else:
        #   sostituisco - con / nelle stringhe
        strUltimaLez = strUltimaLez.replace('-','/')
        strPrimaProv = strPrimaProv.replace('-','/')
        #   calcolo degli oggetti data a partire dalle stringhe
        dataUltimaLez = datetime.strptime(strUltimaLez,'%Y/%m/%d')
        dataPrimaProv = datetime.strptime(strPrimaProv,'%Y/%m/%d')
        dataUltimaLez = dataUltimaLez.date()
        dataPrimaProv = dataPrimaProv.date()

        delta = dataPrimaProv - dataUltimaLez
        delta = delta.days

        # se mi risulta un delta negativo, i dati sono inconsitenti e quindi segno -2, piu avanti aggiusto con valore medio
        # CAMBIRARE APPROCCIO? VOLENDO POTREI ANCHE METTERE -1
        if delta < 0:
            delta = -2

        #   calcolo dopo quanti giorni dalla fine delle lezioni lo studente ha dato l' esame, e lo aggiungo all' array della nuova feature
        giorniProv.append(delta)

df['GIORNI_ESAME_PROVATO']=giorniProv

display(df)

print('\n=============================\n')


#=========================================================================
# gestione valori mancanti o inconsistenti
#========================================================================= 
print('\n=================================')
print('       gestione valori mancanti o inconsistenti     ')
print('=================================\n')

#========================================================================= stampo la situazione prima dell' eliminazione dei valori mancanti
print('\numero righe iniziali: ',len(df))

matricoleTemp = calcolaMatricole(df)

primiAnni = []
for i in range(len(matricoleTemp)):
    primoAnno = matricoleTemp[i].iloc[0,13]
    primiAnni.append(primoAnno)
primiAnni = uniq(primiAnni)

conteggi = np.zeros(len(primiAnni))
for i in range(len(matricoleTemp)):
    primoAnno = matricoleTemp[i].iloc[0,13]
    for j in range(len(primiAnni)):
        if primoAnno == primiAnni[j]:
            conteggi[j]+=1

print('primi anni: ', primiAnni)
print('conteggi: ', conteggi)
print('totale studenti: ',len(matricoleTemp),'\n')
del(matricoleTemp)


#=========================================================================
#non ci sono esami superati per cui manca il numero di giorni esame superato
df[(df['GIORNI_ESAME_PASSATO']==GIORNI_ESAME_NON_SUPERATO) & (df['STA_SCE_COD']=='S')]
#=========================================================================
# sistemo giorni esame passato < 0 impostando data fine lezioni = data superamento (MIGLIORABILE)

print('casi con giorni esame passato < 0, dovuto a data freq > data sup: ',len(df[df['GIORNI_ESAME_PASSATO']<0]))

for i in df.index:
    if df.loc[i,'GIORNI_ESAME_PASSATO']<0:
        df.loc[i,'GIORNI_ESAME_PASSATO']=10
        df.loc[i,'DATA_FREQ']=df.loc[i,'DATA_SUP']

print('sistemo...')
print('casi al termine: ',len(df[df['GIORNI_ESAME_PASSATO']<0]))
#=========================================================================
# ci sono esami superati per cui manca il numero di giorni del primo tentativo, sistemo stimando i valori mancanti
print('casi con giorni esame provato mancante: ',len(df[(df['GIORNI_ESAME_PROVATO']==GIORNI_ESAME_MAI_PROVATO) & (df['STA_SCE_COD']=='S')]))

for i in df.index:
    if df.loc[i,'GIORNI_ESAME_PROVATO']==GIORNI_ESAME_MAI_PROVATO and df.loc[i,'STA_SCE_COD']=='S':
        df.loc[i,'DATA_PRIMO_APPELLO']=df.loc[i,'DATA_FREQ']
        df.loc[i,'GIORNI_ESAME_PROVATO']=0
        numero = 1
        giorniPassato = df.loc[i,'GIORNI_ESAME_PASSATO']
        if giorniPassato > 15 and giorniPassato<40: numero = 2
        elif giorniPassato >=40 and giorniPassato < 60: numero = 3
        else: numero = 4
        df.loc[i,'NUMERO']= numero

print('al termine: ',len(df[(df['GIORNI_ESAME_PROVATO']==GIORNI_ESAME_MAI_PROVATO) & (df['STA_SCE_COD']=='S')]))
#=========================================================================
# ci sono casi con data fine lezioni > data primo tentativo
print('casi con giorni esame provato mancante: ',len(df[df['GIORNI_ESAME_PROVATO']<0]))

for i in df.index:
    if df.loc[i,'GIORNI_ESAME_PROVATO']<0:
        df.loc[i,'DATA_FREQ']=df.loc[i,'DATA_PRIMO_APPELLO']
        df.loc[i,'GIORNI_ESAME_PROVATO'] = 0
print('al termine: ',len(df[df['GIORNI_ESAME_PROVATO']<0]))
#=========================================================================


#=========================================================================
# per 5 studenti mancano i dati di certi esami
#   questi studenti non hanno piu' dato alcun esame anche negli anni successivi, quindi probabilmente gli esami mancanti non sono stati superati
#   quindi aggiungo gli esami mancanti segnandoli come non superati

print('aggiungo gli esami che sono mancanti per certi studenti')

matricole = calcolaMatricole(df)

#----------------------------------------------------------
#   ELIMINO STUDENTI PER CUI MANCANO I DATI DI CERTI ESAMI

# A 2 studenti (0.01% dei casi) mancano le righe relative ad alcuni esami.

DA_SISTEMARE = []

numeroColonne = len(matricole[1].columns)
numeroRighe = len(ESAMI_TOTALI)
numeroCampiPrevisi = numeroColonne*numeroRighe

for i in range (len(matricole)):
    l = len(matricole[i].to_numpy().flatten())
    if l!=numeroCampiPrevisi:
        matricola = matricole[i]
        DA_SISTEMARE.append(matricola.iloc[0,0])

DA_SISTEMARE = uniq(DA_SISTEMARE)

nesamiSistemati = 0
for elem in DA_SISTEMARE:
    nesamiSistemati+= len(df[df['STU_ID'] == elem])

valoriMancanti = len(DA_SISTEMARE)

#===============================================================aggiungo esami mancanti
nEsamiAggiunti = 0
esameNonSuperato = df.iloc[0].copy(deep=True)
esameNonSuperato.loc['STU_ID'] = 0
esameNonSuperato.loc['STA_SCE_COD']='F'
esameNonSuperato.loc['VOTO']=np.nan
esameNonSuperato.loc['LODE_FLG']=0
esameNonSuperato.loc['NUMERO']=0
esameNonSuperato.loc['DATA_SUP']=np.nan
esameNonSuperato.loc['DATA_FREQ']=np.nan
esameNonSuperato.loc['DATA_MAX_APPELLO']=np.nan
esameNonSuperato.loc['DATA_PRIMO_APPELLO']=np.nan
esameNonSuperato.loc['GIORNI_ESAME_PASSATO']=GIORNI_ESAME_NON_SUPERATO
esameNonSuperato.loc['GIORNI_ESAME_PROVATO']=GIORNI_ESAME_MAI_PROVATO

for i in range(len(DA_SISTEMARE)):
    datiStudente = df[df['STU_ID']==DA_SISTEMARE[i]]
    print('studente con esami mancanti:')
    display(datiStudente)

    esamiDati = datiStudente['DES'].tolist()
    for esame in ESAMI_TOTALI:
        if esame not in (esamiDati):

            if esame == 'ALGEBRA E GEOMETRIA' or esame == 'ALGORITMI E STRUTTURE DATI I' or esame == 'ANALISI MATEMATICA' or esame == 'FISICA': peso = 9
            elif esame == 'ARCHITETTURA DEGLI ELABORATORI': peso = 6
            elif esame == 'FONDAMENTI DI PROGRAMMAZIONE A - FONDAMENTI DI PROGRAMMAZIONE B': peso = 15
            else: peso = 3

            nEsamiAggiunti+=1
            nuovoEsame = esameNonSuperato.copy(deep=True)
            nuovoEsame.loc['DES']= esame
            nuovoEsame.loc['PRIMO_ANNO']=datiStudente.iloc[0,13]
            nuovoEsame.loc['PESO']=peso
            nuovoEsame.loc['AA_OFF_ID']=datiStudente.iloc[0,7]
            nuovoEsame.loc['STU_ID']=DA_SISTEMARE[i]
            df= df.append(nuovoEsame,ignore_index = True)
    print('studente con esami mancanti sistemato:')
    # ORDINO GLI ESAMI IN ORDINE ALFABETICO
    df = df.sort_values(by='DES')
    display(df[df['STU_ID']==DA_SISTEMARE[i]])


#===============================================================

print('studenti per cui ci sono esami mancanti: ',valoriMancanti) 
print('in totale ho aggiunto: ',nEsamiAggiunti,' esami')
del(matricole)

print('\n=============================\n')


#=========================================================================

print('controlli:')

#CONTROLLI SU POSSIBILI INCONSISTENZE
if len (df[df['GIORNI_ESAME_PASSATO']<0]) > 0:
    print('PROBLEMA: ci sono giorni esame passato < 0')

if len (df[df['GIORNI_ESAME_PASSATO']<0]) > 0:
    print('PROBLEMA: ci sono giorni esame passato < 0')

problema = False
for i in df.index:
    if df.loc[i,'STA_SCE_COD']=='S' and pd.isna(df.loc[i,'VOTO']) and df.loc[i,'DES']!= 'INGLESE B1':
        problema = True
if problema: print('PROBLEMA: ci sono esami superati in cui manca il voto')

print('\n=============================\n')

#=========================================================================

print('rimuovo STA_SCE_COD segnando voto = 0 quando l\' esame non viene superato')
#RIMUVO STA_SCE_COD
#segno voto = 0 nel caso l' esame non sia stato superato
for i in df.index:
    if df.loc[i,'STA_SCE_COD']=='F':
        df.loc[i,'VOTO'] = 0
    #segno 30 come voto di inglese nel caso sia stato superato
    if df.loc[i,'DES']=='INGLESE B1':
        if df.loc[i,'STA_SCE_COD']=='S':
            df.loc[i,'VOTO']= 30
    
df = df.astype({"VOTO": int})
df.drop('STA_SCE_COD',axis=1,inplace=True)
        
#=========================================================================
print('rimuovo colonna lode segnando voto = 31 quando uno studente la ottiene')
# #   ELIMINO COLONNA LODE SEGNANDO VOTO 31 AL POSTO DEL FLAG
for i in df.index:
    if df.loc[i,'LODE_FLG'] == 1 and df.loc[i,'VOTO']==30:
        df.loc[i,'VOTO']=31
df.drop('LODE_FLG',axis=1,inplace=True)

display(df)

print('\n=============================\n')
''#=========================================================================
# #sistemo questo studente per cui ho visto che il primo anno e' sbagliato
# for i in df.index:
#     if df.loc[i,'STU_ID']==267757: df.loc[i,'PRIMO_ANNO']=2016

#sistemo qeusti studenti
studentiDaSistemare = [243460,239249,239815,267757]
if MESE_RIFERIMENTO < 4:
    for i in df.index:
        stuId = df.loc[i,'STU_ID']
        if stuId in studentiDaSistemare and df.loc[i,'VOTO']>0:
            if df.loc[i,'DES']=='FONDAMENTI DI PROGRAMMAZIONE A - FONDAMENTI DI PROGRAMMAZIONE B':
                df.loc[i,'VOTO'] = 0
                df.loc[i,'GIORNI_ESAME_PASSATO']=GIORNI_ESAME_NON_SUPERATO
                df.loc[i,'NUMERO'] = 0
                df.loc[i,'GIORNI_ESAME_PROVATO']=GIORNI_ESAME_MAI_PROVATO


#=========================================================================report situazione finale
print('numero righe finali: ',len(df))

matricoleTemp = calcolaMatricole(df)

primiAnni = []
for i in range(len(matricoleTemp)):
    primoAnno = matricoleTemp[i].iloc[0,11]
    primiAnni.append(primoAnno)
primiAnni = uniq(primiAnni)

conteggi = np.zeros(len(primiAnni))
for i in range(len(matricoleTemp)):
    primoAnno = matricoleTemp[i].iloc[0,11]
    for j in range(len(primiAnni)):
        if primoAnno == primiAnni[j]:
            conteggi[j]+=1

print('primi anni: ', primiAnni)
print('conteggi: ', conteggi)
print('totale studenti: ',len(matricoleTemp))
del(matricoleTemp)
