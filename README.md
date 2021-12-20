# FESTIVAL APP

## Overview

The target of this project is providing a payment circuit for a festival "ROCK DANS SACLAY FESTIVAL".
The money transfer should take place using the smart card technology. The tool created is composed by
three parts: the code for the card called "Project.java" (written in javacard), the library for the client called
"library_rizzi.py" and the client written in java. This code is divided into two parts, one for the registering
point ("register_gui.py") and one for money transfer ("general_gui.py"). Both these codes use the python
module "tinker" to provide a friendly Graphic User Interface. The remaining part to develop for this project is
creating a code for database interaction. Until now the list of users is saved on a simple text file.

## Workflow

<img src="/tool_flow.png" width="500" height="350">

Steps:

1. Go to "LAPTOP A" and register your card. Enter your Name, Surname and the initial budget amount
after payment. The laptop will display your card ID number and your pin.

2. Once you are registered and you want to buy a beer, you have to go to "LAPTOP B". The host behind
the laptop will charge you of the amount needed to acquire a certain amount of beers. In case you need
a recharge or to check the status on your card this is the spot where to ask for it.

3. If you want to transfer the money of the card to one of your friends’ card, you and your friend have to go
to "LAPTOP B". There it will be possible to transfer money between the two smartcards "A" and "B"
if the amount on the card is enough.

4. If you have problems with your card go to "LAPTOP A". It will be possible to recover Name and Surname
of the owner of the card in case of lost card. If the number of maximum attempts for the pin trial (in this
implementation 3) has been reached, you have to re-register your card and all the money will be lost. So
DO NOT LOSE YOUR PASSWORD

## Pre-requisites

This project works with python3

	apt-get update
	apt-get install -y pcscd pcsc-tools python-pyscard python-six python-dev python3-dev python3-pyscard

	apt-get -y install git
	apt-get -y install openjdk-8-jre
	apt-get -y install openjdk-8-jdk
	apt-get -y install ant

	echo "alias gp='java -jar /home/carmine/Desktop/DevJavaCard/tools/GlobalPlatformPro/gp.jar'" >> ~/.bash_aliases
	
	pip3 install tinker

## Tutorial

To compile the Javacard code and to installing it on the smart card you can execute the following commands:

	$ ant
	$ gp -install Project.cap 0102030405 --params 0A0B0C0D01102003

The value followed by the params value is the PIN, ID and PIN_FESTIVAL of the card in sequence

If the program is already present on the smart card it has to be deleted before installing it using the following command:

	$ $gp -delete 0102030405

To run the register point code execute:

	python3 register_gui.py

Do not close and open the program as for now there is no database but only a simple file called "INFO.txt" where data are saved

Every time the program starts the id count restart from the beginning - this is only a temporary simple solution only to show the working principle od the App

To run the paying point code execute:

	python3 general_gui.py

Pay attention to the location of the gp function look at the register_gui.py file and the gp variable if it corresponds to your same domain

## Future implementations

As for now, this implementation does not connect a bank card reader to the client. A possible future imple-
mentation would send directly the amount transferred with this technology directly to the client software.

Another interesting develop would be the creation of the database to have a parallel
access to the same data using a centralized technology.

In case of exceeded the maximum trials on the PIN, it could be implemented some alternative way to recover
the money. For example recover the status using the PIN_FESTIVAL.

Another point would be the encryption in case the client and the card are not only connected with a usb
cable. In case this communication would go on a larger network an encryption would be fundamental to hide
the data exchanged.

In case a serious problem takes place during the money transfer, a variable called "wallet" is present in the
code. A possible feature would be make it easier to recover this money in case of failure during the money
transfer.

The last but not least alternative would be creating the same program but using Elliptic Curves at place of
RSA as crypto algorithm. EC is more efficient and faster than RSA. The only issue to take into consideration
is the limit of algorithms present inside the javacard of any possible smartcard.
