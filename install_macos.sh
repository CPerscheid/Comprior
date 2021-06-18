#!/bin/sh
############################ PYTHON ############################
#REQUIREMENT: Python 3.5+ must be installed
pip3 install -r code/Python/requirements.txt

############################ R ############################
#REQUIREMENT: R 3.5+ must be installed
Rscript code/R/requirements.R

############################ JAVA ############################
#REQUIREMENT: Java JDK and Maven must be installed

#package the Java sources
cd code/Java
mvn package

#update necessary paths in config.ini so that the framework finds everything
cd ../..
#homePath
sed -i '' "5s#.*#homePath=$PWD/#" code/configs/config.ini

#Rscript
RSCRIPTHOME=$(which Rscript)
sed -i '' "17s#.*#RscriptLocation=$RSCRIPTHOME/#" code/configs/config.ini

#Java
JAVAHOME=$(which java)
sed -i '' "21s#.*#JavaLocation=$JAVAHOME/#" code/configs/config.ini
