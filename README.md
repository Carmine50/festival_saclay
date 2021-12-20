FESTIVAL APP 

to run the register point code execute:
#python3 register_gui.py

do not close and open the program as for now there is no database but only a simple file called "INFO.txt" where data are saved

every time the program starts the id count restart from the beginning - this is only a temporary simple solution only to show the working principle od the App

to run the paying point code execute:
#python3 general_gui.py



pay attention to the location of the gp function look at the register_gui.py file and the gp variable if it corresponds to your same domain

the only python3 package to download is tinker

the commands needed before executing the code are the following:

apt-get update
apt-get install -y pcscd pcsc-tools python-pyscard python-six python-dev python3-dev python3-pyscard

apt-get -y install git
apt-get -y install openjdk-8-jre
apt-get -y install openjdk-8-jdk
apt-get -y install ant

echo "alias gp='java -jar /home/carmine/Desktop/DevJavaCard/tools/GlobalPlatformPro/gp.jar'" >> ~/.bash_aliases
