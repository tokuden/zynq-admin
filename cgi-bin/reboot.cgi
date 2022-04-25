#!/bin/bash
echo "Content-Type: text/plain"
echo ""

echo $1 | sudo -S reboot 2>&1
#sudo reboot 2>&1
