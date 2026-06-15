#!/usr/bin/env python3
"""Avvia l'applicazione Smart Home con interfaccia grafica PyQt6."""

import sys
import os

# Aggiunge la directory corrente al path per trovare il package smart_home
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from smart_home.main_gui import main

main()
