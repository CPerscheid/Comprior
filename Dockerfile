# the first stage of our build will use a maven 3.6.1 parent image
FROM maven:3.6.1-jdk-8-alpine AS MAVEN_BUILD

# copy the pom and src code to the container
COPY code/Java/src /home/app/Java/src
COPY code/Java/pom.xml /home/app/Java

# package our application code
RUN mvn -f /home/app/Java/pom.xml clean package



# the second stage of our build will use open jdk 8 on alpine 3.9
#FROM openjdk:8-jre-alpine3.9

FROM ubuntu:latest

ENV DEBIAN_FRONTEND noninteractive

# copy only the artifacts we need from the first stage and discard the rest
#TODO: copy the WEKA_Evaluator and WEKA_FeatureSelector jars to the right location
COPY --from=MAVEN_BUILD /home/app/Java/target/WEKA_Evaluator.jar /home/app/code/Java/WEKA_Evaluator.jar

COPY --from=MAVEN_BUILD /home/app/Java/target/WEKA_FeatureSelector.jar /home/app/code/Java/WEKA_FeatureSelector.jar

#TODO: all the rest: install requirements for R and Python
RUN apt-get update && apt-get install -y libxml2-dev libssl-dev libcurl4-openssl-dev libblas-dev liblapack-dev libgfortran-10-dev gfortran default-jdk

RUN apt-get install -y --no-install-recommends build-essential r-base python3.6 python3-pip python3-setuptools python3-dev

WORKDIR /home/app

#copy R and Python code sources
COPY code/Python /home/app/code/Python
COPY code/R /home/app/code/R

RUN pip3 install -r /home/app/code/Python/requirements.txt

RUN Rscript /home/app/code/R/requirements.R

#create a directory for configs and copy the base config file
RUN mkdir /home/app/code/configs
COPY code/configs/config.ini /home/app/code/configs/config.ini

#adapt the config file to point to the correct home, R, and Java paths
RUN sed -i "5s#.*#homePath=$PWD/#" /home/app/code/configs/config.ini
RUN sed -i "17s#.*#RscriptLocation=Rscript#" /home/app/code/configs/config.ini
RUN sed -i "20s#.*#code = \${General:homePath}code/Java/#" /home/app/code/configs/config.ini
RUN sed -i "21s#.*#JavaLocation=java#" /home/app/code/configs/config.ini


#create the input/output directories
RUN mkdir /home/app/data
RUN mkdir /home/app/data/input
RUN mkdir /home/app/data/intermediate
RUN mkdir /home/app/data/results

#copy the example input files
COPY data/input/example/example_TCGA-BRCA_500samples_5000genes.csv /home/app/data/input/example_TCGA-BRCA_500samples_5000genes.csv
COPY data/input/example/example_TCGA-BRCA_metadata.csv /home/app/data/input/example_TCGA-BRCA_metadata.csv
COPY data/input/example/crossEval_TCGA-BRCA_610samples_5000genes_labeled.csv /home/app/data/input/crossEval_TCGA-BRCA_610samples_5000genes_labeled.csv

WORKDIR /home/app/code/Python/comprior

ENTRYPOINT ["python3", "pipeline.py" ] #for being able to pass arguments to the script
