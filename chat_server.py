#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 24 18:12:40 2020

@author: rocco
"""

import socket #libreria for sockets
import sys #libreria di systema
import threading
import argparse
import logging


#HELP
parser = argparse.ArgumentParser(version='0.1', description='Chat SERVER')
parser.add_argument('-i', '--ip', type=str, help='My Chat Server IP, default=0.0.0.0', default="0.0.0.0")
parser.add_argument('-p', '--port', type=int, help='My Chat Server PORT, default=8888', default=8888)
args = parser.parse_args()

#DATI
IP=args.ip
PORT=args.port

#LOG
logging.basicConfig(level=logging.INFO)


#Funzione che verra lanciata in parallelo
def clientthread(conn, nomi):
    logging.debug("clientthread was called " + str(conn))
    while True:
        #Gestione nuova connessione
        data = conn.recv(1024)       
        reply = reply_func( pars_data(data), nomi)
        if not data:
            logging.error("NO DATA: Condizione di errore: Connessone chiusa dall'host remoto")
            conn.close()
            break
        if data == u"ciao\r\n":
            conn.close()
            break
        logging.info('Messaggio inviato ---> '+ reply)
        conn.sendall(reply)

#Prende in ingresso una stringa e ritorna una lista, separatore == |
def pars_data(data):
    pos=1000
    data=data.replace(" ", "")
    logging.debug('DATA : ' + data)
    data_list=[]
    tmp_string=data
    while True:
        try:
            pos=tmp_string.index("|")
        except:
            data_list.append(tmp_string)
            logging.debug('parsing terminato')
            break
        logging.debug('POS : ' + str(pos))
        logging.debug('TMP : ' + tmp_string)
        logging.debug('tmp_string[:pos]' + tmp_string[:pos])
        data_list.append(tmp_string[:pos])
        tmp_string=tmp_string[pos+1:]
    for elemento in data_list:
        logging.debug('Data list : '+ elemento) 
    return data_list


def reply_func(data_list, nomi):
    if data_list[0] == "REG" and len(data_list)==4:   
        logging.debug('nomi[data_list[1]] = ' + data_list[1])
        if data_list[1] in nomi: return "409 | Name Conflict"
        logging.debug('nomi[data_list[1]] = ' + data_list[1] +', [data_list[2] = ' + data_list[2] + ' data_list[3] = ' + str(data_list[3]))
        print 'Dict_INSERT : {' + data_list[1] + ': ' + data_list[2] + ', ' + str(data_list[3])+'}'
        nomi[data_list[1]]=[data_list[2],data_list[3]]
        return "200 | OK"
    elif data_list[0] == "CONN" and len(data_list)==2:
        if data_list[1] in nomi:  return "200 | OK | "+ nomi[data_list[1]][0] + ' | ' +nomi[data_list[1]][1]  
        else : return "404 | NOT FOUND"
    else:
        return "400 | BAD REQUEST"
        


# Crea un socket (TCP/IP)
try:
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
except socket.error, msg:
    logging.error('Failed to create socket. Error code: '+ str(msg[0]) + ' , Error message : '+msg[1])
    sys.exit();
logging.info('Socket creato')

#Assegnare ad un socket un indirizzo e una porta
try: 
    s.bind((IP, PORT))
except socket.error , msg:
    logging.error('Bind failed. Error code : ' + str(msg[0]) + ' Message ' + str(msg[1]))
    PORT+=1
    logging.info('Provo a connettermi alla porta successiva ' + str(PORT))
    try:
        s.bind((IP, PORT))
    except socket.error , msg:
        print 'Bind failed. Error code : ' + str(msg[0]) + ' Message ' + str(msg[1])
        sys.exit()

print 'Effettuata la bind {IP : ' + IP + ' , PORT : ' + str(PORT) + ' }'


#Mettere in ascolto il socket
s.listen(10)
print 'Socket now listening. Buffer size is 10'

#Creo il dizionario dei nomi
#Coppia chiave valore dove:
#chiave il cliente
#Valore e una lista addr IP di quell'utente
nomi={}
nomi['myself']=[IP,PORT]
print 'Dizionario creato e inizializzato con chiave myself' + ' IP ' + nomi['myself'][0] + ' e porta ' + str(nomi['myself'][1])




while True:
    #Accettare la connessione in ingresso
    conn, addr = s.accept()

    #Quando una connessione è accettata la funzione si blocca
    #Questa ritorna un nuovo socket (conn) che è destinato unicamente per la comunicazionecon quel client 

    print 'Connected with ' + addr[0] + ':' + str(addr[1])
    #Lanciare la funzione
    t1 = threading.Thread(target=clientthread,args=(conn,nomi,))
    t1.start()

    #L'esecuzione del processo chiamante si mette in pausa aspettando la terminazione del thread
    #t1.join()

s.close()