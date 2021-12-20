import tkinter
from tkinter import font
from library_rizzi import *
import os

file_db = "INFO.txt"

pwd = os.getcwd()


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

		self.card_inserted = False

		self.logo = tkinter.PhotoImage(file=pwd + "/logo.png")
		self.logo = self.logo.subsample(5)

		self.label_logo = tkinter.Label(window, image=self.logo)
		self.label_logo.place(anchor='ne', relx =.07, rely=.01)


		label_status = tkinter.Label(window, bg="white", text="ROCK DANS SACLAY FESTIVAL 2K21",font="Times 40")
		label_status.place(anchor='center', relx =.5, rely=.06)

		window.configure(background = "White")


		self.connect_text = tkinter.StringVar()
		if self.card_inserted == False:
			self.connect_text.set("CONNECT")
		else:
			self.connect_text.set("DISCONNECT")

		btn_connect = tkinter.Button(window, command=self.press_connect, textvariable=self.connect_text, height=3, width=10)


		btn_connect.place(anchor='nw', relx =.9, rely=.02)


		btn_status = tkinter.Button(window, command=self.press_status, text="Status money card", bg="orange", fg="red", height=3, width=80)
		btn_status.place(anchor='center', relx =.5, rely=.2)
		btn_status['font'] = font.Font(family='Helvetica',size=30)

		btn_recharge = tkinter.Button(window, command=self.press_recharge, text="Recharge money on card", bg="orange", fg="red", height=3, width=80)
		btn_recharge.place(anchor='center', relx =.5, rely=.4)
		btn_recharge['font'] = font.Font(family='Helvetica',size=30)


		btn_pay = tkinter.Button(window, command=self.press_pay,text="Pay beer", bg="orange", fg="red", height=3, width=80)
		btn_pay.place(anchor='center', relx =.5, rely=.6)
		btn_pay['font'] = font.Font(family='Helvetica',size=30)


		btn_pay = tkinter.Button(window, command=self.press_transfer, text="Transfer money to a friend", bg="orange", fg="red", height=3, width=80)
		btn_pay.place(anchor='center', relx =.5, rely=.8)
		btn_pay['font'] = font.Font(family='Helvetica',size=30)

	def press_connect(self):
		if self.card_inserted == False:
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
			connect_window = tkinter.Toplevel(self.window)
			connect_window.attributes("-fullscreen",True)
			Connect_1(id, connect_window, self)
		else:
			self.card_inserted = False
			self.card.end_connection()
			self.connect_text.set("CONNECT")

	def press_status(self):
		if self.card_inserted:
			status = self.card.status_money()
			if status != 1:
				if status == 2:
					text_err = "YOU HAVE NOT STILL INSERTED THE CORRECT PIN"
				if status == 3:
					text_err = "ERROR IN STATUS REQUEST"
				if status == 4:
					text_err = "ERROR IN VERIFICATION OF STATUS REQUEST"
				if status == 5:
					text_err = "ERROR IN VERIFICATION STATUS CARD"
				self.show_error_message(text_err)
				return 0
			status_money = self.card.get_status()
			status_window = tkinter.Toplevel(self.window)
			status_window.attributes("-fullscreen",True)
			Status(status_window,status_money)
		else:
			text_err = "YOU HAVE TO CONNECT FIRST!!"
			self.show_error_message(text_err)


	def press_recharge(self):
		if self.card_inserted:
			recharge_window = tkinter.Toplevel(self.window)
			recharge_window.attributes("-fullscreen",True)
			Recharge_1(recharge_window, self)
		else:
			text_err = "YOU HAVE TO CONNECT FIRST!!"
			self.show_error_message(text_err)



	def press_pay(self):
		if self.card_inserted:
			pay_window = tkinter.Toplevel(self.window)
			pay_window.attributes("-fullscreen",True)
			Pay_1(pay_window, self)
		else:
			text_err = "YOU HAVE TO CONNECT FIRST!!"
			self.show_error_message(text_err)



	def press_transfer(self):
		if self.card_inserted:
			transfer_window = tkinter.Toplevel(self.window)
			transfer_window.attributes("-fullscreen",True)
			Transfer_1(transfer_window, self)
		else:
			text_err = "YOU HAVE TO CONNECT FIRST!!"
			self.show_error_message(text_err)


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


	def get_pin_festival(self, id):
		file = open(file_db,"r")
		values = file.readlines()
		file.close()
		for line in values:
			if line[0]!='#':
				i = line.split("|")
				if i[0] == id:
					return i[5].replace("\n","")
		return None


class Connect_1:
	def __init__(self, id, window, menu):
		self.id = id
		self.window = window

		self.menu = menu

		btn_home = tkinter.Button(window, text="HOME", command=self.return_home, height=3, width=10)
		btn_home.place(anchor='ne', relx =.1, rely=.1)

		label_status = tkinter.Label(window, text="INSERT YOUR PIN",font="Helvetica 50")
		label_status.place(anchor='center', relx =.5, rely=.5)

		self.pin_entry = tkinter.Entry(window, show="*", font="Helvetica 50", justify="center")
		self.pin_entry.place(anchor='center', width=700, height=100, relx =.5, rely=.6)

		btn_home = tkinter.Button(window, text="OK", command=self.send_pin, height=3, width=10)
		btn_home.place(anchor='center', relx =.5, rely=.8)



	def send_pin(self):
		pin = self.pin_entry.get()

		pin_array = []

		for i in pin:
			pin_array.append(int(i))


		pin_festival = self.menu.get_pin_festival(self.id)

		pin_festival_array = []

		for i in range(len(pin_festival)):
			if i % 2 != 0:
				pin_festival_array.append(int(pin_festival[i]))


		validated = self.menu.card.insert_pin(pin_array, pin_festival_array)
		text_err = "ERROR"


		if validated != 1:
			done = False
			if validated == 2:
				text_err = "WRONG PIN LENGTH"
			if validated == 3:
				text_err = "ERROR IN CONNECTION"
			if validated == 4:
				text_err = "ERROR IN CONNECTION!"
			if validated == 5:
				text_err = "ERROR IN DATABASE"
			if validated == 0:
				attempts_remaining = self.menu.card.get_remaining_trials()
				text_err = "WRONG PIN!\n"+str(attempts_remaining)+" ATTEMPTS LEFT"
				if attempts_remaining == 0:
					text_err += "\nGO TO REGISTER YOUR CARD AGAIN"
		else:
			text_err = "INSERTED RIGHT PIN!\nPRESS BUTTON HOME"
			done = True


		connect_window_2 = tkinter.Toplevel(self.window)
		connect_window_2.attributes("-fullscreen",True)
		Connect_2(connect_window_2,self.window,done, text_err, self.menu)

	def return_home(self):
		self.window.destroy()


class Connect_2:
	def __init__(self, window, window_parent, done, text_err, menu):
		self.window = window
		self.window_parent = window_parent


		btn_home = tkinter.Button(window, text="HOME", command=self.return_home, height=3, width=10)
		btn_home.place(anchor='ne', relx =.1, rely=.1)

		label_rech = tkinter.Label(window, text=text_err,font="Helvetica 50")
		label_rech.place(anchor='center', relx =.5, rely=.4)


		if done == True:
			menu.card_inserted = True
			menu.connect_text.set("DISCONNECT")


	def return_home(self):
		self.window.destroy()
		self.window_parent.destroy()




class Status:
	def __init__(self, window, status_money):
		self.window = window

		#self.home_logo = tkinter.PhotoImage(file=pwd + "/home_logo.png")
		#self.home_logo = self.home_logo.zoom(25)
		#self.home_logo = self.home_logo.subsample(15)
		btn_home = tkinter.Button(window, text="HOME", command=self.return_home, height=3, width=10)
		btn_home.place(anchor='ne', relx =.1, rely=.1)

		label_status = tkinter.Label(window, text="THE AMOUNT ON THE CARD IS €"+str(status_money),font="Helvetica 50")
		label_status.place(anchor='center', relx =.5, rely=.5)

	def return_home(self):
		self.window.destroy()



class Recharge_1:
	def __init__(self, window, menu):
		self.window = window

		self.menu = menu

		btn_home = tkinter.Button(window, text="HOME", command=self.return_home, height=3, width=10)
		btn_home.place(anchor='ne', relx =.1, rely=.1)

		label_rech = tkinter.Label(window, text="QUANTITY TO RECHARGE IN €",font="Helvetica 50")
		label_rech.place(anchor='center', relx =.5, rely=.4)

		self.value_entry = tkinter.Entry(window, font="Helvetica 50", justify="center")
		self.value_entry.place(anchor='center', width=700, height=100, relx =.5, rely=.6)

		btn_home = tkinter.Button(window, text="SEND", command=self.send_value, height=3, width=10)
		btn_home.place(anchor='center', relx =.5, rely=.8)


	def send_value(self):
		recharge = self.value_entry.get()

		recharged = self.menu.card.charge_money(recharge)

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
			message = "RECHARGE COMPLETED SUCCESSFULLY"

		recharge_window_2 = tkinter.Toplevel(self.window)
		recharge_window_2.attributes("-fullscreen",True)
		Recharge_2(recharge_window_2,self.window, message)

	def return_home(self):
		self.window.destroy()



class Recharge_2:
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



class Pay_1:
	def __init__(self, window, menu):
		self.window = window

		self.menu = menu

		btn_home = tkinter.Button(window, text="HOME", command=self.return_home, height=3, width=10)
		btn_home.place(anchor='ne', relx =.1, rely=.1)

		label_pay = tkinter.Label(window, text="QUANTITY TO PAY IN €",font="Helvetica 50")
		label_pay.place(anchor='center', relx =.5, rely=.4)

		self.value_entry = tkinter.Entry(window, font="Helvetica 50", justify="center")
		self.value_entry.place(anchor='center', width=700, height=100, relx =.5, rely=.6)

		btn_home = tkinter.Button(window, text="SEND", command=self.send_value, height=3, width=10)
		btn_home.place(anchor='center', relx =.5, rely=.8)



	def send_value(self):
		pay = self.value_entry.get()

		payed = self.menu.card.withdraw_money(pay)

		message = "ERROR"


		if payed != 1:
			if payed == 2:
				message = "WRONG MONEY INPUT"
			if payed == 3:
				message = "CONNECTION PROBLEMS!"
			if payed == 4:
				message = "AMOUNT ON THE CARD NOT ENOUGH!!"
			if payed == 5:
				message = "CONNECTION PROBLEM"
			if payed == 6:
				message = "PIN NOT VALIDATED"
		else:
			message = "PAYMENT COMPLETED SUCCESSFULLY"


		pay_window_2 = tkinter.Toplevel(self.window)
		pay_window_2.attributes("-fullscreen",True)
		Pay_2(pay_window_2,self.window,message)

	def return_home(self):
		self.window.destroy()



class Pay_2:
	def __init__(self, window, window_parent, message):
		self.window = window
		self.window_parent = window_parent

		btn_home = tkinter.Button(window, text="HOME", command=self.return_home, height=3, width=10)
		btn_home.place(anchor='ne', relx =.1, rely=.1)

		label_pay = tkinter.Label(window, text=message,font="Helvetica 50")
		label_pay.place(anchor='center', relx =.5, rely=.4)


	def return_home(self):
		self.window.destroy()
		self.window_parent.destroy()


class Transfer_1:
	def __init__(self, window, menu):
		self.window = window

		self.menu = menu

		btn_home = tkinter.Button(window, text="HOME", command=self.return_home, height=3, width=10)
		btn_home.place(anchor='ne', relx =.1, rely=.1)

		label_transfer = tkinter.Label(window, text="QUANTITY TO TRASNFER IN €",font="Helvetica 50")
		label_transfer.place(anchor='center', relx =.5, rely=.4)

		self.value_entry = tkinter.Entry(window, font="Helvetica 50", justify="center")
		self.value_entry.place(anchor='center', width=700, height=100, relx =.5, rely=.6)

		btn_home = tkinter.Button(window, text="SEND", command=self.send_value, height=3, width=10)
		btn_home.place(anchor='center', relx =.5, rely=.8)



	def send_value(self):
		take = int(self.value_entry.get())

		taken = self.menu.card.withdraw_money(take)

		message = "ERROR"


		if taken != 1:
			done = False
			if taken == 2:
				message = "WRONG MONEY INPUT"
			if taken == 3:
				message = "CONNECTION PROBLEMS!"
			if taken == 4:
				message = "AMOUNT ON THE CARD NOT ENOUGH!!"
			if taken == 5:
				message = "CONNECTION PROBLEM"
			if taken == 6:
				message = "PIN NOT VALIDATED"
		else:
			done = True
			self.menu.wallet += take
			self.menu.card.end_connection()
			message = "MONEY TAKEN SUCCESSFULLY\nINSERT THE OTHER CARD"


		list_windows = []
		list_windows.append(self.window)
		transfer_window_2 = tkinter.Toplevel(self.window)
		transfer_window_2.attributes("-fullscreen",True)
		list_windows.append(transfer_window_2)
		Transfer_2(list_windows, done, message, self.menu, take)

	def return_home(self):
		self.window.destroy()



class Transfer_2:
	def __init__(self, list_windows, done, message, menu, take):
		self.window = list_windows[-1]
		self.window_parent = list_windows[-2]
		self.list_w = list_windows


		self.menu = menu
		self.transfer = take

		self.card = self.menu.card


		btn_home = tkinter.Button(self.window, text="HOME", command=self.return_home, height=3, width=10)
		btn_home.place(anchor='ne', relx =.1, rely=.1)

		label_pay = tkinter.Label(self.window, text=message,font="Helvetica 50")
		label_pay.place(anchor='center', relx =.5, rely=.4)

		if done== True:
			self.received = True
			btn_home = tkinter.Button(self.window, text="TRANSFER", command=self.transfer_completed, height=3, width=10)
			btn_home.place(anchor='ne', relx =.5, rely=.5)

	def return_home(self):
		for i in self.list_w:
			i.destroy()

	def transfer_completed(self):


		connected = self.card.start_connection()
		if connected != 1:
			if connected == 2:
				text_err = "ERROR IN READING"
			if connected == 3:
				text_err = "ERROR IN CONNECTION INSTRUCTION"
			self.menu.show_error_message(text_err)
			return 0
		id = self.card.request_ID()
		if id != 1:
			if id == 2:
				text_err = "ERROR IN ID FORMAT RECEIVED"
			if id == 3:
				text_err = "ERROR IN ID REQUESTING INSTRUCTION"
			self.menu.show_error_message(text_err)
			return 0
		_id = self.card.get_ID()
		id = ""
		for i in _id:
			id += str(i)
		pk = self.menu.get_pk_from_list(id)
		if pk == None:
			self.menu.show_error_message("CARD NOT REGISTERED\nGO TO REGISTER YOURSELF")
			return 0
		self.card.set_pk_card(int(pk[0]),int(pk[1]))
		verified = self.card.verify_pk_card()
		if verified != 1:
			if verified == 2:
				text_err = "ERROR IN VALIDATION REQUEST"
			if verified == 3:
				text_err = "ERROR IN VALIDATION!\nGO TO REGISTER POINT"
			self.menu.show_error_message(text_err)
			return 0




		connect_window = tkinter.Toplevel(self.window)
		connect_window.attributes("-fullscreen",True)

		self.list_w.append(connect_window)

		Connect_1_transfer(id,connect_window, self.menu, self.list_w, self.transfer)


class Connect_1_transfer:
	def __init__(self, id, window, menu, list_w, transfer):
		self.id = id
		self.window = window

		self.menu = menu
		self.transfer = transfer

		self.list_w = list_w

		btn_home = tkinter.Button(window, text="BACK", command=self.return_home, height=3, width=10)
		btn_home.place(anchor='ne', relx =.1, rely=.1)

		label_status = tkinter.Label(window, text="INSERT YOUR PIN",font="Helvetica 50")
		label_status.place(anchor='center', relx =.5, rely=.5)

		self.pin_entry = tkinter.Entry(window, show="*", font="Helvetica 50", justify="center")
		self.pin_entry.place(anchor='center', width=700, height=100, relx =.5, rely=.6)

		btn_home = tkinter.Button(window, text="OK", command=self.send_pin, height=3, width=10)
		btn_home.place(anchor='center', relx =.5, rely=.8)



	def send_pin(self):
		pin = self.pin_entry.get()

		pin_array = []

		for i in pin:
			pin_array.append(int(i))

		pin_festival = self.menu.get_pin_festival(self.id)


		pin_festival_array = []

		for i in range(len(pin_festival)):
			if i % 2 != 0:
				pin_festival_array.append(int(pin_festival[i]))




		validated = self.menu.card.insert_pin(pin_array, pin_festival_array)
		text_err = "ERROR"


		if validated != 1:
			if validated == 2:
				text_err = "WRONG PIN LENGTH"
			if validated == 3:
				text_err = "ERROR IN CONNECTION"
			if validated == 4:
				text_err = "ERROR IN CONNECTION!"
			if validated == 5:
				text_err = "ERROR IN DATABASE"
			if validated == 0:
				attempts_remaining = self.menu.card.get_remaining_trials()
				text_err = "WRONG PIN!\n"+str(attempts_remaining)+" ATTEMPTS LEFT"
				if attempts_remaining == 0:
					text_err += "\nGO TO REGISTER YOUR CARD AGAIN"
		else:
			text_err = "INSERTED RIGHT PIN!\nPRESS BUTTON BACK"


		connect_window_2 = tkinter.Toplevel(self.window)
		connect_window_2.attributes("-fullscreen",True)

		self.list_w.append(connect_window_2)


		Connect_2_transfer(connect_window_2,self.window,text_err, self.menu, self.list_w, self.transfer)

	def return_home(self):
		self.window.destroy()


class Connect_2_transfer:
	def __init__(self, window, window_parent, text_err, menu, list_w, transfer):
		self.window = window
		self.window_parent = window_parent

		self.transfer = transfer
		self.menu = menu

		self.list_w = list_w

		btn_home = tkinter.Button(window, text="BACK", command=self.return_home, height=3, width=10)
		btn_home.place(anchor='ne', relx =.1, rely=.1)

		label_rech = tkinter.Label(window, text=text_err,font="Helvetica 50")
		label_rech.place(anchor='center', relx =.5, rely=.4)



	def return_home(self):
		message = "ERROR"

		recharged = self.menu.card.charge_money(self.transfer)

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
			self.menu.wallet -= self.transfer
			if self.menu.wallet < 0:
				self.menu.show_error_message("ERROR IN SYSTEM CALL TECHNICIAN")
				return 0

			message = "TRANSFER COMPLETED SUCCESSFULLY"


		transfer_window_3 = tkinter.Toplevel(self.window)
		transfer_window_3.attributes("-fullscreen",True)

		self.list_w.append(transfer_window_3)

		Transfer_3(transfer_window_3,self.window,self.window_parent,message, self.list_w)



class Transfer_3:
	def __init__(self, window, window_parent,window_parent_2, message, list_w):
		self.window = window
		self.window_parent = window_parent
		self.window_parent_2 = window_parent_2

		self.list_w = list_w

		btn_home = tkinter.Button(window, text="HOME", command=self.return_home, height=3, width=10)
		btn_home.place(anchor='ne', relx =.1, rely=.1)

		label_pay = tkinter.Label(window, text=message,font="Helvetica 50")
		label_pay.place(anchor='center', relx =.5, rely=.4)

	def return_home(self):
		for i in self.list_w:
			i.destroy()





window = tkinter.Tk()
menu = Menu(window)
window.mainloop()

