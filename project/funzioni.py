import imports
from imports import *

import settings
from settings import *

#================================================================================================================

def getAnno(data) -> int:
    ris = data[0:4]
    ris = int(ris)
    return ris

#================================================================================================================

# rende non ripetuti gli elementi di un array
def uniq(arr):
    arrUnique = []
    for elem in arr:
        if not elem in arrUnique:
            arrUnique.append(elem)
    return(arrUnique)

#================================================================================================================

#   funzione che riceve una matricola, e restituisce il minimo dei data_freq dello studente
#   ovvero il minimo anno in cui sono terminate le lezioni di un corso a cui lo studente era iscritto

def getAnnoInizioFrequentazioneLezioni (df:pd.DataFrame,matricola:int) -> int:
    #cerco il minimo come il minimo anno in cui lo studente ha finito di seguire un corso
    minimo = -1 # -1 = non impostato
    for i in df.index:
        matricolaCorrente = df.loc[i,'STU_ID']
        if matricola == matricolaCorrente:
            fineLezioni = df.loc[i,'DATA_FREQ']
            if pd.notna(fineLezioni):
                annoFineLezioni = int(fineLezioni[0:4])
                if minimo == -1 or annoFineLezioni < minimo:
                    minimo = annoFineLezioni

    #   ATTENZIONE: QUESTA COSA VA MODIFICATA NEL CASO SI VOLESSE ADDESTRARE L' ALGORITMO SU ESAMI DI ANNI SUCCESSIVI AL PRIMO
    #   nota che questa cosa potrebbe portare ad inconsistenza dei dati nel caso lo studente si fosse iscritto da gennaio in poi
    #   (ma la cosa si verifica in pochissimi casi quindi va bene cosi)
    #   se lo studente non ha frequentato neanche una lezione, uso l' anno di iscrizione +1
    if minimo == -1:
        print('uno studente non ha frequentato neanche una materia')
        for i in df.index:
            matricolaCorrente = df.loc[i,'STU_ID']
            if matricola == matricolaCorrente:
                avvioCarriera = df.loc[i,'ANNO_AVVIO_CARRIERA']
                minimo = avvioCarriera+1

    return minimo
                

#================================================================================================================

#calcola un' array di studenti, dove in ogni cella ci sono tutti gli esami di un certo studente
def calcolaMatricole (dataframe : pd.DataFrame):
#----------------------------------------------------CALCOLO MATRICOLE
    # array contenente tutti i numeri di matricola
    numeri_matricola = dataframe.STU_ID.unique()

    # array di matrici, ogni matrice contiene gli esami di uno studente
    matricole = []
    for matricola in numeri_matricola:
        #voglio solo gli esami dati dallo studente con la matricola giusta
        esMatricola = dataframe[dataframe['STU_ID']==matricola]
        # matricole.append(esMatricola)
        matricole.append(esMatricola) 
    return matricole

#================================================================================================================

#   annulla gli esami dello studente dati dopo il mese x del suo primo anno
def annullaEsami (dataframe: pd.DataFrame, mese:int):

    #controllo consistenza dati
    for i in dataframe.index:
        if(dataframe.loc[i,'VOTO'] > 0 and pd.isna(dataframe.loc[i,'DATA_SUP'])):
            print('problema: ci sono esami superati in cui manca la data di superamento')

    #annullo esami
    esami_annullati = 0
    for i in dataframe.index:
        if dataframe.loc[i,'VOTO'] > 0:
            #   data completa di superamento
            dataSup = dataframe.loc[i,'DATA_SUP']
            meseSup = dataSup[5:7]
            annoSup = dataSup[0:4]
            
            #convertire a stringa
            meseSup = int(meseSup)
            annoSup = int(annoSup)
            
            #   segno come non superati tutti gli esami dati dopo il primo anno dello studente
            if annoSup > dataframe.loc[i,'PRIMO_ANNO'] or meseSup > mese:
                # print('anno sup: ',annoSup,' mese sup: ',meseSup, 'primo anno: ',df.loc[i,'PRIMO_ANNO'],'mese rif: ',mese)
                dataframe.loc[i,'VOTO'] = 0
                dataframe.loc[i,'GIORNI_ESAME_PASSATO'] = GIORNI_ESAME_NON_SUPERATO
                esami_annullati +=1
                
    print('\n in totale ho annullato ',esami_annullati,' esami')



#================================================================================================================

# annullo i primi tentativi dello studente fatti dopo il mese x del suo primo anno
def annullaPrimiTentativi (d:pd.DataFrame,meseRif:int):
    primi_tentativi_annullati = 0
    for i in d.index:
        dataPrimo= d.loc[i,'DATA_PRIMO_APPELLO']
        if pd.notna(dataPrimo):
            mesePrimo = dataPrimo[5:7]
            annoPrimo = dataPrimo[0:4]

            #   conversione a stringa
            mesePrimo = int(mesePrimo)
            annoPrimo = int(annoPrimo)
            
            #   segno come non superati tutti gli esami dati dopo il primo anno dello studente
            if annoPrimo > d.loc[i,'PRIMO_ANNO'] or mesePrimo > meseRif:
                
                d.loc[i,'DATA_PRIMO_APPELLO'] = np.NaN
                d.loc[i,'DATA_MAX_APPELLO']=np.NaN
                d.loc[i,'NUMERO']=0
                d.loc[i,'GIORNI_ESAME_PROVATO'] = GIORNI_ESAME_MAI_PROVATO
                primi_tentativi_annullati +=1
                
    print('\n in totale ho annullato ',primi_tentativi_annullati,' primi tentativi')

#================================================================================================================

#calcola il numero di sessioni che lo studente ha avuto a disposizione per dare l' esame

#giorno primo tentativo, mese, anno, giorno ultimo tentativo, mese, anno
def calcolaSessioni (mp,ap,mu,au):

    sessioni = 0
    difAnni = au - ap

    #caso sessioni in anni diversi
    if difAnni !=0:

        if difAnni !=1:
            #agiungo sessioni anni di mezzo
            sessioni += 3

        #aggiungo sessioni ultimo anno
        # ultimo appello dato in sessione invernale
        if mu < 4: sessioni +=1
        #ultimo appello dato in sessione estiva
        elif mu < 9:sessioni +=2
        else: sessioni +=3

        #aggiungo sessioni primo anno
        if mp < 4: sessioni += 3
        elif mp < 9: sessioni +=2
        else: sessioni +=1

    #caso sessioni fatte tutte nello stesso anno
    else:
        # ultimo appello dato in sessione invernale
        if mu < 4 :sessioni +=1
        #ultimo appello dato in sessione estiva
        elif mu < 9: 
            #appello provato solo in sessione estiva
            if mp >=5: sessioni +=1
            #esame provato anche in sessione invernale
            else: sessioni +=2
        #ultimo appello in sessione autunnale
        else: 
            # primo appello in sessione invernale
            if mp <5: sessioni +=3
            # estiva
            elif mp < 9: sessioni +=2
            # autunnale
            else: sessioni +=1

    return sessioni

#================================================================================================================

import math
def sistemaNumero (d:pd.DataFrame,meseRif:int):
    
    for i in d.index:

        numero = d.loc[i,'NUMERO']

        #se numero = 0 va bene
        #dato che prima chiamo "annullaPrimiTentativi", sono sicuro che tutti gli appelli con numero != 0 abbiamo il primo tentativo fatto prima della data di riferimento
        if numero!=0:

            #ricavo dati ultimo tentativo
            dataUltimo = d.loc[i,'ULTIMO_TENTATIVO']

            # giornoUltimo = dataUltimo[8:]
            meseUltimo= dataUltimo[5:7]
            annoUltimo = dataUltimo[0:4]

            meseUltimo = int(meseUltimo)
            annoUltimo = int(annoUltimo)
            
            #ricavo dati primo tentativo
            dataPrimo= d.loc[i,'DATA_PRIMO_APPELLO']

            # giornoPrimo = dataPrimo[8:]
            mesePrimo = dataPrimo[5:7]
            annoPrimo = dataPrimo[0:4]

            mesePrimo = int(mesePrimo)
            annoPrimo = int(annoPrimo)
            
            sessioni = calcolaSessioni(mesePrimo,annoPrimo,meseUltimo,annoUltimo)
            tentativiMediSessione = round(sessioni / numero)

            #altrimenti ho studenti che hanno passato l' esame con 0 tentativi
            if tentativiMediSessione == 0: tentativiMediSessione=1

            #se lo studente ha data primo appello diversa da data ultimo appello, allora ha fatto almeno due prove, quindi non ci deve essere NUMERO = 1
            if tentativiMediSessione == 1 and (d.loc[i,'ULTIMO_TENTATIVO']!=d.loc[i,'DATA_PRIMO_APPELLO']) and d.loc[i,'VOTO']>0:
                tentativiMediSessione = 2

            #marzo
            if meseRif <= 3:
                if tentativiMediSessione > 2: tentativiMediSessione = 2
                d.loc[i,'NUMERO'] = tentativiMediSessione
            #agosto
            elif meseRif <= 7 : 
                if tentativiMediSessione > 5: tentativiMediSessione = 5
                d.loc[i,'NUMERO'] = tentativiMediSessione
            #ottobre
            else : 
                if tentativiMediSessione > 7: 
                    tentativiMediSessione = 7
                d.loc[i,'NUMERO'] = tentativiMediSessione

#================================================================================================================
def analizza(model,X,y,nloop=NLOOP,reteNeurale=False,epochs = 20):

    acc = []
    prec = []
    recall = []
    f1 = []

    for j in range(nloop):
        print(nloop-j)
        X_train, X_test, y_train, y_test = train_test_split(X,y, train_size=0.75, test_size=0.25)

        if reteNeurale:
            if j != 0: del(model)
            #inserire qui il codice della rete da testare <--
            model = tf.keras.models.Sequential()
            model.add(tf.keras.layers.Flatten())
            model.add(tf.keras.layers.Dense(28, activation=tf.nn.relu))
            model.add(tf.keras.layers.Dense(2, activation=tf.nn.softmax))
            model.compile(optimizer='adam',
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])
              
            model.fit(X_train,y_train,epochs=20,verbose=0)
        else:
            model.fit(X_train,y_train)

        pred = model.predict(X_test)
        if reteNeurale:
            temp = []
            for k in range(len(pred)):
                temp.append(np.argmax(pred[k]))
            pred = temp
    
        acc.append(sklearn.metrics.accuracy_score(y_test, pred, normalize=True, sample_weight=None))
        prec.append(sklearn.metrics.precision_score(y_test, pred, labels=None, pos_label=1, average='binary', sample_weight=None, zero_division='warn'))
        recall.append(sklearn.metrics.recall_score(y_test, pred, labels=None, pos_label=1, average='binary', sample_weight=None, zero_division='warn'))
        f1.append(sklearn.metrics.f1_score(y_test, pred, labels=None, pos_label=1, average='binary', sample_weight=None, zero_division='warn'))

    acc = round(np.mean(acc),3)
    prec = round(np.mean(prec),3)
    recall = round(np.mean(recall),3)
    f1 = round(np.mean(f1),3)

    print('accuracy: ',acc)
    print('prec: ',prec)
    print('recall: ',recall)
    print('f1: ',f1)

    return acc,prec,recall,f1

#================================================================================================================

# def analizzaRegr(model,X,y,nloop=2000):

#     acc = []
#     prec = []
#     recall = []
#     f1 = []

#     for j in range(nloop):
#         print(nloop-j)
#         X_train, X_test, y_train, y_test = train_test_split(X,y, train_size=0.75, test_size=0.25)
#         model.fit(X_train,y_train)
#         pred = model.predict(X_test)

#         for i in range(len(pred)):
#             if pred[i]>1:pred[i]=1
#             if pred[i]<0:pred[i]=0
#             pred[i]= round(pred[i])
    
#         acc.append(sklearn.metrics.accuracy_score(y_test, pred, normalize=True, sample_weight=None))
#         prec.append(sklearn.metrics.precision_score(y_test, pred, labels=None, pos_label=1, average='binary', sample_weight=None, zero_division='warn'))
#         recall.append(sklearn.metrics.recall_score(y_test, pred, labels=None, pos_label=1, average='binary', sample_weight=None, zero_division='warn'))
#         f1.append(sklearn.metrics.f1_score(y_test, pred, labels=None, pos_label=1, average='binary', sample_weight=None, zero_division='warn'))

#     acc = round(np.mean(acc),3)
#     prec = round(np.mean(prec),3)
#     recall = round(np.mean(recall),3)
#     f1 = round(np.mean(f1),3)

#     print('accuracy: ',acc)
#     print('prec: ',prec)
#     print('recall: ',recall)
#     print('f1: ',f1)

#     return acc,prec,recall,f1



#================================================================================================================

# utilizzata per regressione con yregr (numero di cfu di ciascuno studente), non con y = 0 o 1


def analizzaRegr(model,X,y,tipoPrevisioneCFU):
    acc = []
    prec = []
    recall = []
    f1 = []

    for j in range(NLOOP):
        X_train, X_test, y_train, y_test = train_test_split(X,y, train_size=0.75, test_size=0.25)
        model.fit(X_train,y_train)
        pred = model.predict(X_test)

        #caso previsione CFU a fine anno 
        if tipoPrevisioneCFU:
            for i in range(len(pred)):
                if pred[i]<40:pred[i]=0
                else:pred[i]=1

                if y_test[i]<40:y_test[i]=0
                else:y_test[i]=1

        # caso previsione attivita' II anno
        else:
            for i in range(len(pred)):
                if pred[i]>1:pred[i]=1
                if pred[i]<0:pred[i]=0
                pred[i]= round(pred[i])
    
        acc.append(sklearn.metrics.accuracy_score(y_test, pred, normalize=True, sample_weight=None))
        prec.append(sklearn.metrics.precision_score(y_test, pred, labels=None, pos_label=1, average='binary', sample_weight=None, zero_division='warn'))
        recall.append(sklearn.metrics.recall_score(y_test, pred, labels=None, pos_label=1, average='binary', sample_weight=None, zero_division='warn'))
        f1.append(sklearn.metrics.f1_score(y_test, pred, labels=None, pos_label=1, average='binary', sample_weight=None, zero_division='warn'))

    acc = round(np.mean(acc),3)
    prec = round(np.mean(prec),3)
    recall = round(np.mean(recall),3)
    f1 = round(np.mean(f1),3)

    print('accuracy: ',acc)
    print('prec: ',prec)
    print('recall: ',recall)
    print('f1: ',f1)

    return acc,prec,recall,f1

#================================================================================================================

#stampa la matrice di confusione
def matrix(model,X_train,y_train,X_test,y_test,regression,tipoPrevisioneCFU):
    model = model.fit(X_train, y_train)
    pred = model.predict(X_test)
    y_test_copy = y_test.copy()
    
    if regression:
            
            for j in range(len(pred)):
                
                #arrotondo i valori
                pred[j]=round(pred[j])

                if pred[j]>1:pred[j]=1
                if pred[j]<0:pred[j]=0
                  
            cm = confusion_matrix(y_test_copy,pred)

    else:
        cm = confusion_matrix(y_test_copy, pred)

    labels = []
    if tipoPrevisioneCFU:
        labels.append('0 - {} '.format(CFU_RICHIESTI-1))
        labels.append('{} - 60 '.format(CFU_RICHIESTI))
    else:
        labels.append('non attivo')
        labels.append('attivo')
    
    #stampo la matrice
    cmap = seaborn.cubehelix_palette(50, hue=0.05, rot=0, light=0.9, dark=0, as_cmap=True)
    seaborn.heatmap(cm,annot=True,fmt="d",cmap=cmap,xticklabels=labels,yticklabels=labels)

    return cm

#================================================================================================================

#restituisce array con l' importanza delle features per il modello
def importanzaFeatures(modello,X,y,regression = False):

    X_train, X_test, y_train, y_test = train_test_split(X,y, train_size=0.75, test_size=0.25)
    modello.fit(X_train,y_train)

    if regression:
        explainer = lime.lime_tabular.LimeTabularExplainer(training_data=X_train,mode = "regression")
    else:
        explainer = lime.lime_tabular.LimeTabularExplainer(training_data=X_train,mode = "classification")

    #ogni cella di questo array indica l' importanza di una feature
    importanze = []
    numeroFeatures = len(X_test[0])

    #array contenente l' importanza di ogni feature, inizialmente tutte le features hanno importanza = 0
    importanze = np.zeros(numeroFeatures)
    importanzePos = importanze.copy()
    importanzeNeg = importanze.copy()

    #per ogni elemento di Xtest
    for i in range(len(X_test)):
        #ottengo lista che descrive importanza features
        if regression:
            exp = explainer.explain_instance(X_test[i],predict_fn=modello.predict)
        else:
            exp = explainer.explain_instance(X_test[i],modello.predict_proba)
    
        lista = exp.as_list()

        # print(lista)

        #per ogni elemento della lista, guardo a quale feature corrisponde, e quanta importanza le è associata
        for j in range(len(lista)):
            feature = lista[j][0]
            feature = [int(s) for s in feature.split() if s.isdigit()]
            feature = feature[0]

            # print('feature: ',feature)
   
            importanza = lista[j][1]

            # print('importanza: ',importanza)
            # somma features con incidenza positiva
            if importanza > 0: importanzePos[feature]+= importanza
            # somma features con incidenza negativa
            else: importanzeNeg[feature]+=importanza
            # importanza features generica
            importanza = abs(importanza)
            importanze[feature] += importanza
    print(importanze)

    return importanze, importanzePos, importanzeNeg

#================================================================================================================

def importanzaFeaturesMedie(nloop,modello,X,y,regression=False):
    print(nloop)
    #calcolo l' importanza delle features una prima volta per inizializzare gli array
    importanze, importanzePos, importanzeNeg = importanzaFeatures(modello,X,y,regression)
    #calcolo altre volte l' iportanza delle features, sommando l' importanza totale negli array originali
    for i in range(nloop-1):
        print(nloop-1-i)
        temp1, temp2, temp3 = importanzaFeatures(modello,X,y,regression)
        for j in range(len(importanze)):
            importanze[j]+=temp1[j]
            importanzePos[j]+=temp2[j]
            importanzeNeg[j]+=temp3[j]
    
    for j in range(len(importanze)):
        importanze[j]=importanze[j]/nloop
        importanzePos[j]=importanzePos[j]/nloop
        importanzeNeg[j]=importanzeNeg[j]/nloop
    return importanze, importanzePos, importanzeNeg

#=================================================================================================================

    #   stima il numero di tentativi di esame fatti in un certo mese
def contaEsamiProvatiNelMese (df: pd.DataFrame, mese:int):

    nEsami = 0
    for i in df.index:
        if df.loc[i,'VOTO'] > 0:
            #   data completa di superamento
            dataSup = df.loc[i,'DATA_SUP']
            ultimoTentativo = df.loc[i,'ULTIMO_TENTATIVO']
            primoTentativo = df.loc[i,'DATA_PRIMO_APPELLO']

            

            meseSup = dataSup[5:7]
            meseUltimoTentativo = ultimoTentativo[5:7]
            mesePrimoTentativo = primoTentativo[5:7]

            #convertire a stringa
            meseSup = int(meseSup)
            meseUltimoTentativo= int(meseUltimoTentativo)
            mesePrimoTentativo = int(mesePrimoTentativo)
            if meseSup == mese or meseUltimoTentativo == mese or mesePrimoTentativo == mese: 
                nEsami+=1
    
    return nEsami

#=================================================================================================================

def sistemaDatiTemporali(df:pd.DataFrame,MESE_RIFERIMENTO):
    #   annulo gli esami dati dopo settembre
    annullaEsami(df,MESE_RIFERIMENTO)

    #   annullo i primi tentativi fatti dopo settembre
    annullaPrimiTentativi(df,MESE_RIFERIMENTO)

  
    #sistemo NUMERO

    # CONTROLLO CHE NON CI SIANO ESAMI PER CUI NON SI HA LA DATA DELL' ULTIMO TENTATIVO
    display(df[pd.isna(df['DATA_MAX_APPELLO']) & pd.isna(df['DATA_SUP']) & df['NUMERO']!=0])



    #CALCOLO ULTIMO TENTATIVO
    ULTIMO_TENTATIVO = []
    for i in df.index:
        dataSup = df.loc[i,'DATA_SUP']
        ultimoTenativo = df.loc[i,'DATA_MAX_APPELLO']
        if df.loc[i,'NUMERO']==0:
            ULTIMO_TENTATIVO.append(np.NaN)
        else:
            if pd.notna (dataSup): ULTIMO_TENTATIVO.append(dataSup)
            elif pd.notna (ultimoTenativo):ULTIMO_TENTATIVO.append(ultimoTenativo)
            else: print('ERRORE, DATA ULTIMO TENTATIVO NON DISPONIBILE PER QUESTO ESAME')

    df['ULTIMO_TENTATIVO']= ULTIMO_TENTATIVO
    df.drop('DATA_MAX_APPELLO',axis=1,inplace=True)


    sistemaNumero(df,MESE_RIFERIMENTO)

#==================================================================================

def esportaMatricole(matricole):
    for i in range(len(matricole)):
        nome = 'export/X/' + str(i) + '.csv'
        matricole[i].to_csv(nome,index=False)

#==================================================================================

def esportaCFU(cfu):
    with open('export/y_cfu.txt', 'w') as f:
        for elem in cfu:
            f.write(str(elem)+'\n')

#==================================================================================
def calcolaArrayCFU(df:pd.DataFrame):
    dfCFU = df.copy()

    # SEGNO GLI ESAMI DATI DOPO IL PRIMO ANNO COME NON DATI (quindi gli esami del primo semestre dati a fine anno vengono considerati superati)
    #serve perche' altrimenti se uno studente da un esame del primo semestre al secondo, non gli conteggerei i CFU

    #annulla tutti gli esami dati dopo il primo anno dello studente
    annullaEsami(dfCFU,12)

    #   CALCOLO ARRAY CFU
    cfu = []
    matricole = calcolaMatricole(dfCFU)
    print('numero studenti: ',len(matricole))

    for elem in matricole:
        cfuStudente = 0
        for i in elem.index:
            if elem.loc[i,'VOTO']>0:
                cfuStudente+= elem.loc[i,'PESO']
        cfu.append(cfuStudente)

    print(cfu)
    del(matricole)

    return cfu