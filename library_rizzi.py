#commands  $ant		$gp -delete 0102030405    $gp -install Project.cap 0102030405 --params 0A0B0C0D01102003

from Crypto.PublicKey import RSA
from Crypto.Hash import SHA1
from Crypto.Signature import pkcs1_15
from Crypto.Random import get_random_bytes

from Crypto.IO import PEM
from smartcard.System import readers
from smartcard.Exceptions import *

import os
import base64
import codecs

ID_LENGTH = 4
PIN_LENGTH = 4
MAX_MONEY = 65500
MAX_MONEY_LENGTH = 2

DEBUG = True  #in debug mode the results are printed

#define
CLA = 0xA0
INS_INSERT_PIN = 0x00
INS_INSERT_PIN_FESTIVAL = 0x01
INS_MODIFY_MONEY = 0x02
INS_RCV_ID = 0x03
INS_SHARE_PK_MOD = 0x06
INS_SHARE_PK_EXP = 0x07
INS_VERIFY_PK = 0x08
INS_STATUS_MONEY = 0x09
INS_SIGN_STATUS = 0x0A
INS_WRITE_INFO = 0x0B
INS_SEND_INFO = 0x0C
INS_SIGN_INFO = 0x0D

P1,P2 = 0x00, 0x00
Le = 0x00 # set to 0 means the client does not know the size of received data 
SELECT = [0x00,0xA4,0x04,0x00,0x08]
AID = [0x01,0x02,0x03,0x04,0x05,0x01,0x02,0x04]


def from_data_to_hex(data):
    value = ""
    for i in data:
            _tmp = hex(i)[2:]
            if len(_tmp) <2:
                    tmp = "0" + _tmp
            else:
                    tmp = _tmp
            value += tmp
    return value

def from_data_to_ascii(data):
    value = ""
    for i in data:
        value += chr(i)
    return value


class Card:
    def __init__(self):
        #all initialized to None for future implementations
        self.connection = None #first step is using start_connection function
        self.ID_card = None
        self.priv_key = None
        self.publ_key = None
        self.pk_card  = None
        self.remaining_trials = 0
        self.remaining_trials_festival = 0
        pass

    def start_connection(self):
        r=readers()
        self.connection=r[0].createConnection()
        try:
            self.connection.connect()
        except NoCardException:
            return 2        #error code for no card inserted in the reader

        #key creation 2048
        self.priv_key = RSA.generate(2048)
        self.publ_key = self.priv_key.publickey()
        f = open('pk.pem','wb')
        f.write(self.publ_key.exportKey())
        f.close()

        #Selection AID
        apdu = SELECT + AID
        data, sw1, sw2 = self.connection.transmit(apdu)
        if DEBUG:
            print(hex(sw1),hex(sw2),data)
        if hex(sw1) == "0x90" and hex(sw2) == "0x0":
            return 1
        else:
            return 3 #error in instruction



    def request_ID(self):
        #receive ID of the card
        data, sw1, sw2 = self.connection.transmit([CLA,INS_RCV_ID,P1,P2,Le])
        if DEBUG:
            print(hex(sw1),hex(sw2),data)
        if not(hex(sw1) == "0x90" and hex(sw2) == "0x0"):
            return 3   #error in instruction
        self.ID_card = data
        if(len(self.ID_card) != ID_LENGTH):
            if DEBUG:
                print("ERROR IN ID LENGTH")
            return 2  # error in ID length
        else:
            return 1

    def get_ID(self):
        return self.ID_card

    def request_pk_card(self):
        #receive mod pk of the card
        data,sw1, sw2 = self.connection.transmit([CLA,INS_SHARE_PK_MOD,P1,P2,Le])
        if hex(sw1) == "0xfa" and hex(sw2) == "0xce":
            return 2 #mod already requested
        if not(hex(sw1) == "0x90" and hex(sw2) == "0x0") or len(data) == 0:
            return 3  #error in requesting module
        self.mod_pk_card = int(from_data_to_hex(data),16)
        if DEBUG:
            print(hex(sw1),hex(sw2),data)
            print("KEY'S MODULE LENGTH:  ",end="")
            print(len(data))
            print("KEY MODULE:  ",end="")
            print(self.mod_pk_card)

        #receive exp pk of the card
        data,sw1, sw2 = self.connection.transmit([CLA,INS_SHARE_PK_EXP,P1,P2,Le])
        if hex(sw1) == "0xfa" and hex(sw2) == "0xce":
            return 4 #exp already requested
        if not(hex(sw1) == "0x90" and hex(sw2) == "0x0") or len(data) == 0:
            return 5  #error in requesting exponent
        self.exp_pk_card = int(from_data_to_hex(data),16)
        if DEBUG:
            print(hex(sw1),hex(sw2),data)
            print("KEY'S EXPONENT LENGTH:  ",end="")
            print(len(data))
            print("KEY EXPONENT:  ",end="")
            print(self.exp_pk_card)

        self.pk_card = RSA.construct((self.mod_pk_card,self.exp_pk_card))
        return 1

    def get_pk_card(self):
        return self.pk_card

    def set_pk_card(self, mod, exp):
        self.mod_pk_card = mod
        self.exp_pk_card = exp
        self.pk_card = RSA.construct((self.mod_pk_card,self.exp_pk_card))


    def verify_pk_card(self):
        #verify pk of the card
        chall = list(get_random_bytes(10))
        Lc = len(chall)
        data,sw1, sw2 = self.connection.transmit([CLA,INS_VERIFY_PK,P1,P2,Lc]+chall)
        if not(hex(sw1) == "0x90" and hex(sw2) == "0x0") or len(data) == 0:
            return 2  #error in requesting sign
        if DEBUG:
            print("SIGN CARD:")
            print(hex(sw1),hex(sw2),data)
            print(len(data))
        chall_sign = bytes(data)
        chall_b = bytes(chall)

        try:
            pkcs1_15.new(self.pk_card).verify(SHA1.new(chall_b),chall_sign)
        except ValueError:
            if DEBUG:
                print("ERROR!\nSignature not valid")
            return 3 #signature not valid
        if DEBUG:
            print("Signature validated for user")
        return 1

    def insert_pin(self, pin, pin_festival):
        if len(pin) != PIN_LENGTH or len(pin) != PIN_LENGTH:
            return 2 #wrong pin length
        #send PIN
        Lc = len(pin)
        data, sw1, sw2 = self.connection.transmit([CLA,INS_INSERT_PIN,P1,P2,Lc]+pin)
        if not(hex(sw1) == "0x90" and hex(sw2) == "0x0") or len(data) == 0:
            return 3 #error in sending PIN
        if DEBUG:
            print(hex(sw1),hex(sw2),data)
            if data[1] == 1:
                print("correct PIN!")
            else:
                print("Wrong PIN!\n"+str(data[0])+" attempts remaining")
        if data[1] != 1:
            self.remaining_trials = data[0]
            return 0
        #send PIN festival
        Lc = len(pin_festival)
        data, sw1, sw2 = self.connection.transmit([CLA,INS_INSERT_PIN_FESTIVAL,P1,P2,Lc]+pin_festival)
        if not(hex(sw1) == "0x90" and hex(sw2) == "0x0") or len(data) == 0:
            print(hex(sw1),hex(sw2),data)
            return 4 #error in sending PIN festival
        if DEBUG:
            print(hex(sw1),hex(sw2),data)
            if data[1] == 1:
                print("correct PIN FESTIVAL!")
            else:
                print("Wrong PIN FESTIVAL!\n"+str(data[0])+" attempts remaining")
        if data[1] == 1:
            return 1
        else:
            self.remaining_trials_festival= data[0]
            return 5

    def get_remaining_trials(self):
        return self.remaining_trials

    def get_remaining_trials_festiva(self):
        return self.remaining_trials_festival


    def status_money(self):
        #status money
        data, sw1, sw2 = self.connection.transmit([CLA,INS_STATUS_MONEY,P1,P2,Le])
        if hex(sw1) == "0xfa" and hex(sw2) == "0xce":
            return 2 #PIN not validated
        if not(hex(sw1) == "0x90" and hex(sw2) == "0x0") or len(data) != MAX_MONEY_LENGTH:
            return 3 #error getting status
        if DEBUG:
            print(hex(sw1),hex(sw2),data)
        tmp_status = data
        data,sw1, sw2 = self.connection.transmit([CLA,INS_SIGN_STATUS,P1,P2,Le])
        if not(hex(sw1) == "0x90" and hex(sw2) == "0x0") or len(data) == 0:
            return 4  #error in requesting sign
        if DEBUG:
            print("SIGN CARD:")
            print(hex(sw1),hex(sw2),data)
            print(len(data))
        chall_sign = bytes(data)
        chall_b = bytes(tmp_status)

        try:
            pkcs1_15.new(self.pk_card).verify(SHA1.new(chall_b),chall_sign)
        except ValueError:
            if DEBUG:
                print("ERROR!\nSignature not valid")
            return 5 #signature not valid
        if DEBUG:
            print("Signature validated for user")
        self.status = tmp_status[0] * 256 + tmp_status[1]
        return 1

    def get_status(self):
        return self.status


    def charge_money(self, _money):
        #charge money to the card

        money = int(_money)
        if not(isinstance(money, int) and money>=0 and money<MAX_MONEY):
            return 2 #wrong money input
        ret = self.status_money()
        if ret != 1:
            return 3 #error in getting status
        money_status = self.get_status()
        total = money_status + money
        if total > MAX_MONEY:
            return 4 #max amount storable error
        charge = []
        charge.append(int(total/256))
        charge.append(int(total%256))
        if DEBUG:
            print("NEW TOTAL : ",end="")
            print(charge)
        Lc = len(charge)
        data, sw1, sw2 = self.connection.transmit([CLA,INS_MODIFY_MONEY,P1,P2,Lc]+charge)
        if DEBUG:
            print(hex(sw1),hex(sw2),data)
        if hex(sw1) == "0xfa" and hex(sw2) == "0xce":
            return 6 #PIN not validated
        if not(hex(sw1) == "0x90" and hex(sw2) == "0x0"):
            return 5 #error setting money 
        return 1


    def withdraw_money(self, _money):
        #withdraw money from the card

        money = int(_money)
        if not(isinstance(money, int) and money>=0 and money<MAX_MONEY):
            return 2 #wrong money input
        ret = self.status_money()
        if ret != 1:
            return 3 #error in getting status
        money_status = self.get_status()
        total = money_status - money
        if total < 0:
            return 4 #not enough money
        charge = []
        charge.append(int(total/256))
        charge.append(int(total%256))
        if DEBUG:
            print("CHARGE : ",end="")
            print(charge)
        Lc = len(charge)
        data, sw1, sw2 = self.connection.transmit([CLA,INS_MODIFY_MONEY,P1,P2,Lc]+charge)
        if DEBUG:
            print(hex(sw1),hex(sw2),data)
        if hex(sw1) == "0xfa" and hex(sw2) == "0xce":
            return 6 #PIN not validated
        if not(hex(sw1) == "0x90" and hex(sw2) == "0x0"):
            return 5 #error taking money 
        return 1

    def write_info(self, name, surname):

        if not(isinstance(name, str) and isinstance(surname, str)):
            return 2 #wrong inputs
        _info = name + "|" + surname
        info = []
        for i in _info:
            info.append(ord(i))
        Lc = len(info)
        data, sw1, sw2 = self.connection.transmit([CLA,INS_WRITE_INFO,P1,P2,Lc]+info)
        if DEBUG:
            print(hex(sw1),hex(sw2),data)
        if hex(sw1) == "0xfa" and hex(sw2) == "0xce":
            return 3 #PIN not validated
        if not(hex(sw1) == "0x90" and hex(sw2) == "0x0"):
            return 4 #error sending info
        return 1

    def receive_info(self):

        data, sw1, sw2 = self.connection.transmit([CLA,INS_SEND_INFO,P1,P2,Le])
        if DEBUG:
            print(hex(sw1),hex(sw2),data)
        if not(hex(sw1) == "0x90" and hex(sw2) == "0x0"):
            return 2 #error requesting info
        tmp_info = data
        data,sw1, sw2 = self.connection.transmit([CLA,INS_SIGN_INFO,P1,P2,Le])
        if not(hex(sw1) == "0x90" and hex(sw2) == "0x0") or len(data) == 0:
            return 3  #error in requesting sign
        if DEBUG:
            print("SIGN CARD:")
            print(hex(sw1),hex(sw2),data)
            print(len(data))
        chall_sign = bytes(data)
        chall_b = bytes(tmp_info)

        try:
            pkcs1_15.new(self.pk_card).verify(SHA1.new(chall_b),chall_sign)
        except ValueError:
            if DEBUG:
                print("ERROR!\nSignature not valid")
            return 4 #signature not valid
        if DEBUG:
            print("Signature validated for user")
        info = ""
        for i in tmp_info:
            info += chr(i)
        sp = info.split("|")
        self.name = sp[0]
        self.surname = sp[1]
        return 1

    def get_info(self):
        return self.name, self.surname

    def end_connection(self):
        #Disconnect the reader
        self.connection.disconnect()
