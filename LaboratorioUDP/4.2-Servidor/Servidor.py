# -*- coding: utf-8 -*-
"""
Created on Tue Mar 15 18:33:41 2022

@author: Seccion 2 Grupo 1
"""
import socket
import threading
import os
import logging
import datetime
import time

class Server:
    def __init__(self):
        self.s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.accept_connections()
    
    def accept_connections(self):
        #ip = socket.gethostbyname(socket.gethostname())
        ip = '0.0.0.0'
        port = int(input('Ingresar puerto para el servidor --> '))
        buffer_size=int(input('Ingrese el tamaño del buffer (max 64KB) --> '))

        self.s.bind((ip,port))
        #self.s.listen(100)

        print('Servidor corriendo en: ' + ip)
        print('En el puerto: ' + str(port))

        arch = input('Ingresar archivo a trasmitir: (i.e. 100MB.txt) ')
        numClientes = int(input('Ingrese cantidad de clientes que tiene que estar conectados para empezar a trasmitir '))
        
        p = 1 
        now = datetime.datetime.now()
        logName = 'Logs/'+ str(now.year) + '-' + str(now.month) + '-' + str(now.day)+ '-' + str(now.hour)+ '-' +  str(now.minute)+ '-' + str(now.second) + 'prueba' + str(p) + '-log.log'
        #file = open(logName, "w")
        #file.close()
        b = os.path.getsize(arch)
        
        logging.basicConfig(filename=logName, level=logging.INFO)
        logging.info('Inicio de envio de archivos')
        logging.info('Nombre archivo: ' + arch)
        logging.info('Tamaño del archivo: ' + str(b) + " bytes")
        logging.info('Cantidad de clientes: ' + str(numClientes))
        
        threads = list()
        conectClient = 0

        while 1:
            #c, addr = self.s.accept()
            bytesAddressPair = self.s.recvfrom(buffer_size)
            c = bytesAddressPair[1][0]
            addr = bytesAddressPair[1][1]
            
            print('Conexion recibida numero:', (conectClient + 1))
            
            #print(addr)
            print('C:',c,'addr:', addr)
            #print(addr[1])
            
            threads.append(threading.Thread(target=self.handle_client,args=(c,addr,arch,buffer_size,conectClient + 1,numClientes,)))
            conectClient += 1
            
            if conectClient == numClientes:
                for t in threads:
                    t.start()
                    
                for t in threads:
                    t.join()
                threads = list()
                conectClient = 0
                arch = input('Ingresar archivo a trasmitir: (i.e. 100MB.txt) ')
                numClientes = int(input('Ingrese cantidad de clientes que tiene que estar conectados para empezar a trasmitir '))
                p += 1
                logName = str(now.year) + '-' + str(now.month) + '-' + str(now.day)+ '-' + str(now.hour)+ '-' +  str(now.minute)+ '-' + str(now.second) + 'prueba' + str(p) + '-log.log'
                logging.basicConfig(filename=logName, level=logging.INFO)
                b = os.path.getsize(arch)
                logging.info('Inicio de envio de archivos')
                logging.info('Nombre archivo: ' + arch)
                logging.info('Tamaño del archivo: ' + str(b) + " bytes")
                logging.info('Cantidad de clientes: ' + numClientes)
                
                
    def handle_client(self,c,addr,data,buffer_size,numClient, totConex):
        #data = c.recv(1024).decode()
        logging.info('Cliente ' + str(c))
        if not os.path.exists(data):
            #c.send("El Archivo no existe".encode())
            self.s.sendto('El Archivo no existe'.encode(),(c,addr))

        else:
            #c.send("iniciando-envio".encode())
            self.s.sendto('iniciando-envio'.encode(),(c,addr))
            nom = str(numClient) + '-Prueba-' + str(totConex) + '.txt'#data
            #c.send(nom.encode())
            self.s.sendto(nom.encode(),(c,addr))
            
            
            #if c.recv(buffer_size).decode() == 'Nombre recibido correctamente':
            if self.s.recvfrom(buffer_size)[0].decode() == 'Nombre recibido correctamente':
                print('Enviando: ',data)
                
                file = open(data,'rb')
                hashVal = str(hash(file))
                
                start = time.time()
                
                if data != '':
                    
                    data = file.read(buffer_size)
                    while data:
                        #c.send(data)
                        self.s.sendto(data,(c,addr))
                        data = file.read(buffer_size)   
                    #c.send("EOF".encode())
                    self.s.sendto("EOF".encode(),(c,addr))
                    
                #confirm = c.recv(buffer_size).decode()
                confirm = self.s.recvfrom(buffer_size)[0].decode()
                
                if confirm == 'OK':
                    logging.info('Archivo entregado exitosamente a cliente: ' + str(addr))
                    end=time.time()
                    logging.info('Tiempo de entrega: ' + str(end-start))
                    #c.send(hashVal.encode())
                    
    
                    c.shutdown(socket.SHUT_RDWR)
                    c.close()
                
        

server = Server()