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
    #   questa cosa potrebbe generare dell' errore ma non saprei come altro fare dato che a volte i dati sono incoerenti (vedi sotto)
    else: 
        primoAnno.append(avvCar+1)
        # caso3+=1

df['PRIMO_ANNO'] = primoAnno
# print('caso1: ',caso1)
# print('caso2: ',caso2)
# print('caso3: ',caso3)

print('\n=============================\n')

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
# eliminazione valori mancanti
#========================================================================= 

print('\n=================================')
print('       eliminazione outliers     ')
print('=================================\n')

#========================================================================= stampo la situazione prima dell' eliminazione dei valori mancanti
print('\numero righe iniziali: ',len(df))

matricoleTemp = calcolaMatricole(df)

primiAnni = []
for i in range(len(matricoleTemp)):
    primoAnno = matricoleTemp[i].iloc[0,12]
    primiAnni.append(primoAnno)
primiAnni = uniq(primiAnni)

conteggi = np.zeros(len(primiAnni))
for i in range(len(matricoleTemp)):
    primoAnno = matricoleTemp[i].iloc[0,12]
    for j in range(len(primiAnni)):
        if primoAnno == primiAnni[j]:
            conteggi[j]+=1

print('primi anni: ', primiAnni)
print('conteggi: ', conteggi)
print('totale studenti: ',len(matricoleTemp),'\n')
del(matricoleTemp)

#=========================================================================

print('elimino DATA_FREQ inconsistenti')

# ELIMINAZIONE DATA_FREQ INCONSISTENTI

# In 8 casi (0.7% del totale) casi ho la data di fine lezioni in un anno successivo a quello
#  in cui lo studente ha superato l’ esame, quidi i dati sono inconsistenti.

#nota che in questo modo vengono eliminati tutti gli studenti con GIORNI_ESAME_PASSATO < 0

DA_ELIMINARE = []      
stampato = False

for i in df.index:
    #se lo studente ha superato l' esame
    if df.loc[i,'STA_SCE_COD']=='S':
        #per ogni riga ottengo le date che mi interessano
        strUltimaLez = df.loc[i,'DATA_FREQ']
        strSup = df.loc[i,'DATA_SUP']

        #   sostituisco - con / nelle stringhe
        strUltimaLez = strUltimaLez.replace('-','/')
        strSup = strSup.replace('-','/')

        #   calcolo degli oggetti data a partire dalle stringhe
        dataUltimaLez = datetime.strptime(strUltimaLez,'%Y/%m/%d')
        dataSup = datetime.strptime(strSup,'%Y/%m/%d')
        dataSup = dataSup.date()
        dataUltimaLez = dataUltimaLez.date()

        #estraggo i giorni la differenza in giorni
        delta = dataSup - dataUltimaLez
        delta = delta.days

        #se ho data_freq successiva a data_sup, correggo
        if delta < 0:

            matricola = df.loc[i,'STU_ID']
            DA_ELIMINARE.append(matricola)
            
            #report
            if not stampato: 
                print('esempio:')
                print(df.loc[i])
                stampato = True

esami_eliminati = len(DA_ELIMINARE)
DA_ELIMINARE = uniq(DA_ELIMINARE)

nesamiEliminati = 0
for elem in DA_ELIMINARE:
    nesamiEliminati+= len(df[df['STU_ID'] == elem])

for elem in DA_ELIMINARE:
    df = df[df['STU_ID'] != elem]

print('valori mancanti: ',esami_eliminati,' esami') 
print('\nho eliminato: ',len(DA_ELIMINARE),' studenti')
print('esami eliminati: ',nesamiEliminati)

print('\n=============================\n')

#=========================================================================
#   IN ALCUNI CASI HO ESAME PASSATO, MA MANCA IL NUMERO DI GIORNI DEL PRIMO TENTATIVO
#   ELIMINO QUESTI OUTLIERS

# In 9 casi (0.8% del totale) ho che lo studente ha superato l’ esame, ma manca il numero di giorni dopo cui lo ha provato.

print('elimino casi in cui ho esame passato ma manca il numero di giorni del primo tentativo')

DA_ELIMINARE = []
n = 0
daSistemare = []

for i in df.index:
    risultato = df.loc[i,'STA_SCE_COD']
    giorni_esame_provato = df.loc[i,'GIORNI_ESAME_PROVATO']
    if(risultato == 'S' and giorni_esame_provato== GIORNI_ESAME_MAI_PROVATO):
        n+=1
        daSistemare.append(i)
        matricola = df.loc[i,'STU_ID']
        DA_ELIMINARE.append(matricola)

print('alcuni esempi:')
display(df.loc[daSistemare[0:6]])

esami_eliminati = len(DA_ELIMINARE)
DA_ELIMINARE = uniq(DA_ELIMINARE)

nesamiEliminati = 0
for elem in DA_ELIMINARE:
    nesamiEliminati+= len(df[df['STU_ID'] == elem])

for elem in DA_ELIMINARE:
    df = df[df['STU_ID'] != elem]

print('valori mancanti: ',esami_eliminati,' esami') 
print('\nho eliminato: ',len(DA_ELIMINARE),' studenti')
print('esami eliminati: ',nesamiEliminati)

print('\n=============================\n')

#=========================================================================
#   ELIMINO OUTLIERS GIORNI ESAME PROVATO INCONSISTENTI (data sup < data fine lezioni) 
# In 2 casi (0.01 % del totale) ho che lo studente ha superato l’ esame prima della data in cui sono finite le lezioni.

print('elimino GIORNI ESAME PROVATO inconsistenti ')

DA_ELIMINARE = []

for i in df.index:
    val = df.loc[i,'GIORNI_ESAME_PROVATO']
    if val == -2: 
        matricola = df.loc[i,'STU_ID']
        DA_ELIMINARE.append(matricola)

esami_eliminati = len(DA_ELIMINARE)
DA_ELIMINARE = uniq(DA_ELIMINARE)

nesamiEliminati = 0
for elem in DA_ELIMINARE:
    nesamiEliminati+= len(df[df['STU_ID'] == elem])

for elem in DA_ELIMINARE:
    df = df[df['STU_ID'] != elem]

print('valori mancanti: ',esami_eliminati,' esami') 
print('\nho eliminato: ',len(DA_ELIMINARE),' studenti')
print('esami eliminati: ',nesamiEliminati)

print('\n=============================\n')

#=========================================================================
#ELIMINAZIONE STUDENTI PER CUI MANCANO CERTI ESAMI

print('elimino studenti per cui mancano i dati di certi esami')

matricole = calcolaMatricole(df)

#----------------------------------------------------------
#   ELIMINO STUDENTI PER CUI MANCANO I DATI DI CERTI ESAMI

# A 2 studenti (0.01% dei casi) mancano le righe relative ad alcuni esami.

DA_ELIMINARE = []

numeroColonne = len(matricole[1].columns)
numeroRighe = len(ESAMI_TOTALI)
numeroCampiPrevisi = numeroColonne*numeroRighe

for i in range (len(matricole)):
    l = len(matricole[i].to_numpy().flatten())
    if l!=numeroCampiPrevisi:
        matricola = matricole[i]
        DA_ELIMINARE.append(matricola.iloc[0,0])

DA_ELIMINARE = uniq(DA_ELIMINARE)

nesamiEliminati = 0
for elem in DA_ELIMINARE:
    nesamiEliminati+= len(df[df['STU_ID'] == elem])

for elem in DA_ELIMINARE:
    df = df[df['STU_ID'] != elem]

print('valori mancanti: ',esami_eliminati,' esami') 
print('\nho eliminato: ',len(DA_ELIMINARE),' studenti')
print('esami eliminati: ',nesamiEliminati)
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

#=========================================================================report situazione finale
print('numero righe finali: ',len(df))

matricoleTemp = calcolaMatricole(df)

primiAnni = []
for i in range(len(matricoleTemp)):
    primoAnno = matricoleTemp[i].iloc[0,10]
    primiAnni.append(primoAnno)
primiAnni = uniq(primiAnni)

conteggi = np.zeros(len(primiAnni))
for i in range(len(matricoleTemp)):
    primoAnno = matricoleTemp[i].iloc[0,10]
    for j in range(len(primiAnni)):
        if primoAnno == primiAnni[j]:
            conteggi[j]+=1

print('primi anni: ', primiAnni)
print('conteggi: ', conteggi)
print('totale studenti: ',len(matricoleTemp))
del(matricoleTemp)