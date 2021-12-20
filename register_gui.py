import tkinter
from tkinter import font
from library_rizzi import *
import os
import re
import random


file_db = "INFO.txt"

pwd = os.getcwd()

gp = "java -jar " + pwd + "/../tools/GlobalPlatformPro/gp.jar"

AID = "0102030405"

ID_max_length = 4
pin_max_length = 4
pin_max = pow(10,pin_max_length) - 1
MAX_MONEY = 65500

def exitFullScreen(event):
	window.attributes("-fullscreen",False)
	window.geometry('900x600')


class Menu:
	def __init__(self,window):

		self.window = window
		self.window.title("ROCK DANS SACLAY FESTIVAL")
		self.window.attributes("-fullscreen",True)
		self.window.bind("<Escape>",exitFullScreen)

		self.wallet = 0

		self.card = Card()

		self.ID_CARD_cnt = 0


		self.logo = tkinter.PhotoImage(file=pwd + "/logo.png")
		self.logo = self.logo.subsample(5)

		self.label_logo = tkinter.Label(window, image=self.logo)
		self.label_logo.place(anchor='ne', relx =.07, rely=.01)


		label_status = tkinter.Label(window, bg="white", text="ROCK DANS SACLAY FESTIVAL 2K21",font="Times 40")
		label_status.place(anchor='center', relx =.5, rely=.06)

		window.configure(background = "White")



		btn_start = tkinter.Button(window, command=self.press_start, text="START CONFIGURATION", bg="orange", fg="red", height=3, width=80)
		btn_start.place(anchor='center', relx =.5, rely=.4)
		btn_start['font'] = font.Font(family='Helvetica',size=30)


		btn_start = tkinter.Button(window, command=self.press_get, text="GET NAME AND SURNAME", bg="orange", fg="red", height=3, width=80)
		btn_start.place(anchor='center', relx =.5, rely=.6)
		btn_start['font'] = font.Font(family='Helvetica',size=30)

	def press_start(self):
		res = os.system(gp + " -delete "+AID)
		if res != 0:
			self.show_error_message("CARD NOT INSERTED")
			return 0
		ID = ""
		_ID = str(self.ID_CARD_cnt)
		diff = ID_max_length - len(_ID)
		_ID = diff*"0"+_ID
		for i in _ID:
			ID += "0"+i


		pin = ""
		_pin = str(random.randrange(0,pin_max))
		diff = pin_max_length - len(_pin)
		_pin = diff*"0"+_pin
		for i in _pin:
			pin += "0"+i



		pin_festival = ""
		_pin = str(random.randrange(0,pin_max))
		diff = pin_max_length - len(_pin)
		_pin = diff*"0"+_pin
		for i in _pin:
			pin_festival += "0"+i


		res = os.system(gp + " -install Project.cap "+AID+" --params " + pin+ID+pin_festival)
		#format params= PIN + ID + PIN_FESTIVAL

		self.ID_CARD_cnt += 1

		info_window = tkinter.Toplevel(self.window)
		info_window.attributes("-fullscreen",True)
		Info_1(info_window, self, pin, ID, pin_festival)




	def update_file(self, id, mod, exp, name, surname, pin_festival):
		sep = "|"
		text = id+sep+mod+sep+exp+sep+name+sep+surname+sep+pin_festival+"\n"

		file = open(file_db,"a")
		file.write(text)
		file.close()


	def press_get(self):


		connected = self.card.start_connection()
		if connected != 1:
			if connected == 2:
				text_err = "ERROR IN READING"
			if connected == 3:
				text_err = "ERROR IN CONNECTION INSTRUCTION"
			self.show_error_message(text_err)
			return 0
		id = self.card.request_ID()
		if id != 1:
			if id == 2:
				text_err = "ERROR IN ID FORMAT RECEIVED"
			if id == 3:
				text_err = "ERROR IN ID REQUESTING INSTRUCTION"
			self.show_error_message(text_err)
			return 0
		_id = self.card.get_ID()

		id = ""
		for i in _id:
			id += str(i)
		pk = self.get_pk_from_list(id)
		if pk == None:
			self.show_error_message("CARD NOT REGISTERED\nGO TO REGISTER YOURSELF")
			return 0
		self.card.set_pk_card(int(pk[0]),int(pk[1]))
		verified = self.card.verify_pk_card()
		if verified != 1:
			if verified == 2:
				text_err = "ERROR IN VALIDATION REQUEST"
			if verified == 3:
				text_err = "ERROR IN VALIDATION!\nGO TO REGISTER POINT"
			self.show_error_message(text_err)
			return 0


		info = self.card.receive_info()
		if info != 1:
			if info == 2:
				text_err = "ERROR IN INFO REQUEST"
			if info == 3:
				text_err = "ERROR IN SIGN INFO REQUEST"
			if info == 3:
				text_err = "ERROR IN INFO VALIDATION"
			self.show_error_message(text_err)
			return 0
		name, surname = self.card.get_info()

		message = "NAME ASSOCIATED TO THE CARD: "+name + "\nSURNAME ASSOCIATED TO THE CARD: "+surname

		get_window = tkinter.Toplevel(self.window)
		get_window.attributes("-fullscreen",True)
		Get_1(get_window, message)



	def show_error_message(self,text_err):
		error_window = tkinter.Toplevel(self.window, width=500, height=200)
		label_error = tkinter.Label(error_window, text=text_err,font="Helvetica 20", fg="#f00")
		label_error.place(anchor='center', relx =.5, rely=.5)

	def get_pk_from_list(self, id):
		file = open(file_db,"r")
		values = file.readlines()
		file.close()
		for line in values:
			if line[0]!='#':
				i = line.split("|")
				if i[0] == id:
					return i[1],i[2]
		return None



class Info_1:
	def __init__(self, window, menu, pin, ID, pin_festival):
		self.window = window

		self.menu = menu

		self.pin = pin
		self.pin_festival = pin_festival
		self.id = ID


		btn_home = tkinter.Button(window, text="HOME", command=self.return_home, height=3, width=10)
		btn_home.place(anchor='ne', relx =.1, rely=.1)

		label_name = tkinter.Label(window, text="INSERT YOUR NAME",font="Helvetica 50")
		label_name.place(anchor='center', relx =.5, rely=.2)

		self.name_entry = tkinter.Entry(window, font="Helvetica 50", justify="center")
		self.name_entry.place(anchor='center', width=700, height=100, relx =.5, rely=.3)

		label_surname = tkinter.Label(window, text="INSERT YOUR SURNAME",font="Helvetica 50")
		label_surname.place(anchor='center', relx =.5, rely=.4)

		self.surname_entry = tkinter.Entry(window, font="Helvetica 50", justify="center")
		self.surname_entry.place(anchor='center', width=700, height=100, relx =.5, rely=.5)

		label_amount = tkinter.Label(window, text="INSERT YOUR FIRST AMOUNT ON THE CARD",font="Helvetica 50")
		label_amount.place(anchor='center', relx =.5, rely=.6)

		self.amount_entry = tkinter.Entry(window, font="Helvetica 50", justify="center")
		self.amount_entry.place(anchor='center', width=700, height=100, relx =.5, rely=.7)


		btn_home = tkinter.Button(window, text="OK", command=self.send_info, height=3, width=10)
		btn_home.place(anchor='center', relx =.5, rely=.8)


	def send_info(self):
		name = self.name_entry.get()
		surname = self.surname_entry.get()
		amount = int(self.amount_entry.get())

		p = re.compile("^[a-zA-Z'-]+$")

		if not(p.match(name)) or not(p.match(surname)):
			self.menu.show_error_message("NAME/SURNAME INPUT NOT VALID")
			return 0

		if amount<0 or amount > MAX_MONEY:
			self.menu.show_error_message("AMOUNT INPUT NOT VALID")
			return 0

		connected = self.menu.card.start_connection()
		if connected != 1:
			if connected == 2:
				text_err = "ERROR IN READING"
			if connected == 3:
				text_err = "ERROR IN CONNECTION INSTRUCTION"
			self.menu.show_error_message(text_err)
			return 0


		id = ""
		for i in range(len(self.id)):
			if i % 2 != 0:
				id += self.id[i]

		pk_available = self.menu.card.request_pk_card()
		if pk_available != 1:
			if pk_available == 2:
				text_err = "ERROR!\nPUBLIC KEY ALREADY REQUESTED!"
			if pk_available == 3:
				text_err = "ERROR IN REQUESTING PK INSTRUCTION!"
			if pk_available == 4:
				text_err = "ERROR!\nPUBLIC KEY ALREADY REQUESTED"
			if pk_available == 5:
				text_err = "ERROR IN REQUESTING PK INSTRUCTION"
			self.menu.show_error_message(text_err)
			return 0
		pk = self.menu.card.get_pk_card()

		verified = self.menu.card.verify_pk_card()
		if verified != 1:
			if verified == 2:
				text_err = "ERROR IN VALIDATION REQUEST"
			if verified == 3:
				text_err = "ERROR IN VALIDATION!\nGO TO REGISTER POINT"
			self.menushow_error_message(text_err)
			return 0


		self.menu.update_file(id,str(pk.n),str(pk.e),name,surname,self.pin_festival)

		pin_array = []

		for i in range(len(self.pin)):
			if i % 2 != 0:
				pin_array.append(int(self.pin[i]))


		pin_festival_array = []

		for i in range(len(self.pin_festival)):
			if i % 2 != 0:
				pin_festival_array.append(int(self.pin_festival[i]))


		validated = self.menu.card.insert_pin(pin_array, pin_festival_array)


		sent = self.menu.card.write_info(name, surname)

		if sent != 1:
			if sent == 2:
				message = "WRONG NAME/SURNAME INPUT"
			if sent == 3:
				message = "PIN NOT VALIDATED"
			if sent == 4:
				message = "ERROR SENDING INFO"
			self.menu.show_error_message(message)
			return 0

		recharged = self.menu.card.charge_money(amount)

		message = "ERROR"


		if recharged != 1:
			if recharged == 2:
				message = "WRONG MONEY INPUT"
			if recharged == 3:
				message = "CONNECTION PROBLEMS!"
			if recharged == 4:
				message = "AMOUNT TO RECHARGE TOO ELEVATED"
			if recharged == 5:
				message = "CONNECTION PROBLEM"
			if recharged == 6:
				message = "PIN NOT VALIDATED"
		else:
			pin_str = ""
			for i in pin_array:
				pin_str += str(i)
			message = "SUBSCRIPTION COMPLETED SUCCESSFULLY\nTHE ID OF YOUR CARD IS "+str(id)+"\nTHE PIN OF YOUR CARD IS "+str(pin_str)


		info_window_2 = tkinter.Toplevel(self.window)
		info_window_2.attributes("-fullscreen",True)
		Info_2(info_window_2,self.window, message)

	def return_home(self):
		self.window.destroy()


class Info_2:
	def __init__(self, window, window_parent, message):
		self.window = window
		self.window_parent = window_parent

		btn_home = tkinter.Button(window, text="HOME", command=self.return_home, height=3, width=10)
		btn_home.place(anchor='ne', relx =.1, rely=.1)

		label_rech = tkinter.Label(window, text=message,font="Helvetica 50")
		label_rech.place(anchor='center', relx =.5, rely=.4)


	def return_home(self):
		self.window.destroy()
		self.window_parent.destroy()


class Get_1:
	def __init__(self, window, message):
		self.window = window

		btn_home = tkinter.Button(window, text="HOME", command=self.return_home, height=3, width=10)
		btn_home.place(anchor='ne', relx =.1, rely=.1)

		label_status = tkinter.Label(window, text=message,font="Helvetica 50")
		label_status.place(anchor='center', relx =.5, rely=.5)

	def return_home(self):
		self.window.destroy()


window = tkinter.Tk()
menu = Menu(window)
window.mainloop()

