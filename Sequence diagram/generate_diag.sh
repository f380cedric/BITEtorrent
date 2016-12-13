#!/bin/sh

java -jar plantuml.jar -teps step1.txt -o "../Report/img"
java -jar plantuml.jar -teps step2.txt -o "../Report/img"
java -jar plantuml.jar -teps step3.txt -o "../Report/img"