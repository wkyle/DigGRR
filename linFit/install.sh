#!/bin/bash

$SUDO apt-get install python3-dev
$SUDO apt-get install python3-scipy
$SUDO apt-get install python3-pip
$SUDO pip3 install matplotlib
$SUDO apt-get install libgtk-3-dev
$SUDO apt-get install python3-cairo-dev
$SUDO apt-get install python3-gi-cairo
$SUDO apt-get install gir1.2-poppler-0.18

$SUDO cp /usr/local/DigGRR/linFit/DigGRR.desktop /usr/share/applications
