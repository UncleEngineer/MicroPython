from tkinter import *
from tkinter import ttk

import time
import threading
import socket


serverip = '192.168.1.150'
port = 7500


def Runserver():
	while True:
		server = socket.socket()
		server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)

		server.bind((serverip,port))
		server.listen(5)
		print('Wating for client...')

		client, addr = server.accept()
		print('Connect from: ', str(addr))
		data = client.recv(1024).decode('utf-8')
		print('Message from client: ', data)
		v_temptext.set(data)
		client.send('We received your Message!'.encode('utf-8'))
		client.close()


def RunserverThread():
	task1 = threading.Thread(target=Runserver)
	task1.start()


GUI = Tk()
GUI.title('TEMP FROM MICROPYTHON')
GUI.geometry('600x300+200+150')
v_temptext = StringVar()
v_temptext.set('-----TEMP AND HUMID-----')
L1 = ttk.Label(GUI,textvariable=v_temptext,font=('Impact',30))
L1.pack(pady=100)


RunserverThread()
GUI.mainloop()