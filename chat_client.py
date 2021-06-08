#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 25 11:12:28 2020

@author: rocco
"""

import socket #libreria for sockets
import sys #libreria di systema
import argparse #pasrsing
from cmd import Cmd
import threading
import logging


#HELP
parser = argparse.ArgumentParser(version='0.1', description='Chat CLIENT application')
parser.add_argument('-i', '--ip', type=str, help='Remote Chat Server IP, default=127.0.0.1', default="127.0.0.1")
parser.add_argument('-p', '--port', type=int, help='Remote Chat Server PORT, default=8888', default=8888)
parser.add_argument('-n', '--name', type=str, help='My Name, default=Guglielmo', default='Guglielmo')
args = parser.parse_args()

#DATI
IPserver=args.ip
PORTserver=args.port

remote_UDP_IP="-1"
remote_UDP_PORT=-1

my_UDP_IP = "127.0.0.1"
my_UDP_PORT = 4000
amico="Sconosciuto"

MYNAME=args.name

#LOG
logging.basicConfig(level=logging.INFO)


class MyPrompt(Cmd):
    prompt = '>>> '
    intro = "Welcome! Type help"
    
    def do_quit(self, inp):
        print("Bye")
        return True
    
    def do_connect(self, inp):
        logging.info( 'connect  to : ' + inp)
        global remote_UDP_IP
        global remote_UDP_PORT
        global udp_socket
        global amico
        amico=str(inp)
#Inviao il messaggio di Registazione
        MESSAGE="CONN | " + amico
        reply=tcp_send_func (IPserver, PORTserver, MESSAGE)
        print '\r\n+ + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + +'
        print 'TCP_SENT  {'+ IPserver +':'+str(PORTserver)+'} : ' + MESSAGE
        print 'TCP_RECEIVED : ' + reply
        print '+ + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + +\r\n'                
        
        MESSAGE = check_message(pars_data(reply))

        check_list = pars_data(reply)
        if MESSAGE == "START_CHAT":
            remote_UDP_IP=check_list[2]
            remote_UDP_PORT=check_list[3]
            udp_send_func(remote_UDP_IP , int(remote_UDP_PORT), MESSAGE+' | '+MYNAME)
            print '\r\n+ + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + +'
            print 'UDP_SENT { '+amico + ':'+ remote_UDP_IP +':'+str(remote_UDP_PORT)+' } : ' + MESSAGE 
            print '+ + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + +\r\n'                


    def help_connect(self):
        print("connect <nome_clien>\n\rAvvia una chat con l'utente nome_client")

    def do_chat(self, inp):
        print '**********************************************'
        global remote_UDP_IP
        global remote_UDP_PORT
        global udp_socket
        if remote_UDP_IP=="-1":
            print 'ERROR: Nessun peer è connesso'
            return
        while True:
            MESSAGE = raw_input('chat: ')
            if MESSAGE == "END_CHAT":
                print '***************END_CHAT************************'
                break
            else:
                udp_socket.sendto(MESSAGE, (remote_UDP_IP, remote_UDP_PORT))
                print 'UDP_SENT {'+amico+': '+ remote_UDP_IP +':'+str(remote_UDP_PORT)+'}  : ' + MESSAGE 
        
    def help_chat(self):
        print("type <chat> to start a chat")
        

#Definico una funzione che:
# 1) Si aggancia al socket UDP
# 2) manda un messaggio
def udp_send_func (remote_UDP_IP , remote_UDP_PORT, MESSAGE):
    logging.debug('udp_send_func con paramentri : ' + MESSAGE + ' : ' + remote_UDP_IP + ' : ' + str(remote_UDP_PORT))
    global udp_socket
    udp_socket.sendto(MESSAGE, (remote_UDP_IP, remote_UDP_PORT))
    print '\r\n+ + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + +'
    print 'UDP_SENT {'+amico + ':'+remote_UDP_IP+':'+str(remote_UDP_PORT)+'} : ' + MESSAGE
    print '+ + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + +\r\n'                
    
       
#Funzione che crea un socket UDP
def getUdpSocket(current_UDP_IP, current_UDP_PORT):
    #Creo socket   
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    while True:
        try: 
            udp_sock.bind((current_UDP_IP, current_UDP_PORT))
            break
        except socket.error , msg:
            print 'Bind failed. Error code : ' + str(msg[0]) + ' Message ' + str(msg[1])
            current_UDP_PORT+=1
            print 'Provo a connettermi alla porta successiva ' + str(current_UDP_PORT)
    print 'Bind OK : Sono in ascolto su : ' + current_UDP_IP + ' : ' + str(current_UDP_PORT) 
    return udp_sock, current_UDP_IP, current_UDP_PORT
    
    
#Funzione del thread t1 che riceve e parsa messaggi UDP
def clientthread(sock):

    while True:
        data, addr = sock.recvfrom(1024)
        print 'Connected with ' + addr[0] + ':' + str(addr[1])
        data_list=pars_data(data)
        global remote_UDP_IP
        global remote_UDP_PORT
        global amico
        remote_UDP_IP=addr[0]
        remote_UDP_PORT=addr[1]        
            
        if data_list[0] == "START_CHAT" and len(data_list)==2:
            udp_send_func(addr[0] , addr[1], " 600 | OK ") 
            amico = data_list[1]
            print '\r\n+ + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + +'
            print 'UDP_RECEIVED { '+ amico + ':'+addr[0]+':'+str(addr[1])+' } : ' + data
            print '+ + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + +\r\n'                
            print '***************CHAT:'+amico+'************************'
            print '*******digit command <chat> to start**********'
            print '****digit <END_CHAT> to return to shell*******'
            print '**********************************************'
        elif data_list[0] == "600":
            print '\r\n+ + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + +'
            print 'UDP_RECEIVED { '+ amico + ':'+addr[0]+':'+str(addr[1])+' } : ' + data
            print '+ + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + +\r\n'                
            print '***************CHAT:'+amico+'************************'
            print '*******digit command <chat> to start**********'
            print '****digit <END_CHAT> to return to shell*******'
            print '**********************************************'
        else:
            print '\r\n+ + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + +'
            print 'UDP_RECEIVED { '+ amico + ':'+addr[0]+':'+str(addr[1])+' } : ' + data
            print '+ + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + +\r\n'                

                

#Definico una funzione che:
# 1) apre un socketTCP
# 2) manda un messaggio
# 3) ritorna il messaggio di risposta
def tcp_send_func (IPserver , PORTserver, MESSAGE):

# Crea uno stream socket (TCP/IP)
    try:
        tcp_sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    except socket.error, msg:
        print 'Failed to create socket. Error code: '+ str(msg[0]) + ' , Error message : '+msg[1]
        sys.exit();

#Connettersi ad un server
#Primo argomento IP Addressdell'host remoto
#Secondo argomento porta associato al processo server
    try:
        tcp_sock.connect((IPserver , PORTserver))
        print 'Socket Connect to server ' + str(PORTserver) + ' on ip ' + IPserver
    except:
        print 'Connection failed: Il server remoto non risponde'
        print 'EXIT'
        sys.exit()

#Inviare messaggio
    try :
        tcp_sock.sendall(MESSAGE)
    except socket.error:
        print 'Send failed'
        sys.exit()

#Ricevere Dati
#L'argomento della funzione è il numero massimo dei dati che può essere ricevuto
#Il ritorno della funzione rappresenta i dati ricevuti    
    reply= tcp_sock.recv(4096)
    tcp_sock.close
    return reply


#FUNZIONE che prende in ingresso una stringa e ritorna una lista, separatore == |
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
        logging.debug( 'POS : ' + str(pos))
        logging.debug( 'TMP : ' + tmp_string)
        logging.debug( 'tmp_string[:pos]' + tmp_string[:pos])
        data_list.append(tmp_string[:pos])
        tmp_string=tmp_string[pos+1:]
    for elemento in data_list:
        logging.debug( 'Data list : '+ elemento )
    return data_list

#FUNZIONE che prende in ingresso una lista formattatta da pars_data e ritorna il messagio di risposta
def check_message(data_list):
    if data_list[0] == "200" and len(data_list)==2:   
        return "SUCCESS"
    elif data_list[0] == "200" and len(data_list)==4:
        return "START_CHAT" 
    elif data_list[0] == "409" and len(data_list)==2:
        return "ERR"
    else:
        return "ERR"

#Creo sosket UDP 
udp_socket, my_UDP_IP, my_UDP_PORT = getUdpSocket(my_UDP_IP, my_UDP_PORT)

t1 = threading.Thread(target=clientthread,args=(udp_socket,))
t1.start()    

#Inviao il messaggio TCP di Registazione
MESSAGE="REG | " + MYNAME + " | " + my_UDP_IP + " | " + str(my_UDP_PORT)
reply=tcp_send_func (IPserver, PORTserver, MESSAGE)

print '\r\n+ + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + +'
print 'SENT : ' + MESSAGE
print 'RECEIVED : ' + reply
print '+ + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + +\r\n'

MyPrompt().cmdloop()

print 'Chiudo il socket'
udp_socket.close()
sys.exit()