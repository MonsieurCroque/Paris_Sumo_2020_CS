# Paris_Sumo_2020_CS

## Project abstract

For a number of measurements, such as air pollution, road quality and possible anomalies, deploying and installing static sensors seems to be too costly and unrealistic. Relying on data detected via moving vehicles seems to be an efficient and inexpensive solution to carry out these measurements.

As part of our project with AXA "Quantifying the probing and sensing power of vehicles". We are seeking to distribute sensors on various vehicles (buses, taxis, private cars, bicycles, etc.).
Our project can be divided into 3 stages. First, generating the traces of movements (position of the vehicles at each moment) as we do not have this data. Then we have to think about possible applications with such sensors. Finally, define metrics associated with these applications to choose the most appropriate mode of transport for the measurement of a chosen application. 

Detection applications can be diverse: monitoring road conditions, traffic congestion, free parking lot detection and air quality. The objective of the work is to define and measure some space-time metrics to compare the detection power between private vehicles, public transport vehicles (buses, trams, ...), fleet vehicles (taxis, post office) and new mobility paradigms (electric bicycles, electric scooters, ...). 

## Getting Started

The backup can be found here :

### 0) Prerequisites

Please first install SUMO.

And then and python libraries dependencies

```
pip install sumolib rtree
conda install sumolib rtree
```

### 1) Generate the model of deplacement with public data

Make sure for this part to first import the Data folder. It should contain csv files and documents to generate a model.

For each paradigm of mobility, run the script named paradigm.py : It will create an XML file (Origine-Destination Matrix) stored in the OD directory and that can be read by the simulator.

### 2) Run Sumo 

Make sure that the OD directory contains the XML file (By doing step 1 or by uploading the backup)

Go to Sumo directory and run the bash file ( ex. generateBike.bat ) corresponding to the paradigm that you want to generate movement and trace file. The trace file will be stored in the Traces folder 

### 3) Check Traces

Run the script plot.py to pick random trips and verify they are coherent with id name.

### 4) Run Trace2Metrics

Calculate metrics with traces data. It is possible to add or remove metrics directly in the script names trace.py.

### 5) Read and interpret metrics 

To be continued

