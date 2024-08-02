#!/usr/bin/env bash
# Actualizar lista de paquetes
apt-get update

# Instalar dependencias necesarias
apt-get install -y build-essential cmake
apt-get install -y libopenblas-dev liblapack-dev
apt-get install -y libx11-dev libgtk-3-dev
apt-get install -y libboost-python-dev libboost-thread-dev
