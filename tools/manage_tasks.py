#!/usr/bin/env python3
"""
Ylläpitäjä-skripti tehtävä-tiedostojen salaukseen ja purkamiseen.

Käyttö:
  python manage_tasks.py decrypt  - Purkaa tehtavat.txt.enc -> tehtavat.txt
  python manage_tasks.py encrypt  - Salaa tehtavat.txt -> tehtavat.txt.enc
"""

import base64
import sys
import os

ENC_FILE = "app/tehtavat.txt.enc"
PLAIN_FILE = "app/tehtavat.txt"


def decrypt():
    """Purkaa salatun tiedoston"""
    if not os.path.exists(ENC_FILE):
        print(f"❌ Tiedostoa {ENC_FILE} ei löydy")
        sys.exit(1)
    
    try:
        with open(ENC_FILE, 'r') as f:
            encoded = f.read()
        
        decoded = base64.b64decode(encoded)
        
        with open(PLAIN_FILE, 'wb') as f:
            f.write(decoded)
        
        print(f"✅ Tiedosto purettu: {ENC_FILE} -> {PLAIN_FILE}")
    except Exception as e:
        print(f"❌ Virhe purkamisessa: {e}")
        sys.exit(1)


def encrypt():
    """Salaa tavallisen tiedoston"""
    if not os.path.exists(PLAIN_FILE):
        print(f"❌ Tiedostoa {PLAIN_FILE} ei löydy")
        sys.exit(1)
    
    try:
        with open(PLAIN_FILE, 'rb') as f:
            content = f.read()
        
        encoded = base64.b64encode(content).decode('ascii')
        
        with open(ENC_FILE, 'w') as f:
            f.write(encoded)
        
        print(f"✅ Tiedosto salattu: {PLAIN_FILE} -> {ENC_FILE}")
    except Exception as e:
        print(f"❌ Virhe salaamessa: {e}")
        sys.exit(1)


def show_help():
    """Näytä ohje"""
    print(__doc__)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        show_help()
        sys.exit(0)
    
    cmd = sys.argv[1].lower()
    
    if cmd == "decrypt":
        decrypt()
    elif cmd == "encrypt":
        encrypt()
    elif cmd == "help" or cmd == "-h" or cmd == "--help":
        show_help()
    else:
        print(f"❌ Tuntematon komento: {cmd}")
        print()
        show_help()
        sys.exit(1)
