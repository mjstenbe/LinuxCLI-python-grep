#!/usr/bin/env python3
"""
Ylläpitäjä-skripti tehtävä-tiedostojen salaukseen, purkamiseen
ja opiskelijalle vietävän Markdown-listan luomiseen.

Käyttö:
  python manage_tasks.py decrypt     - Purkaa tehtavat.txt.enc -> tehtavat.txt
  python manage_tasks.py encrypt     - Salaa tehtavat.txt -> tehtavat.txt.enc (+ markdown-vienti)
  python manage_tasks.py student-md  - Luo tehtävistä Markdown-listan (ilman vastauksia)

Kommentit tehtavat.txt-tiedostossa:
  Rivit jotka alkavat '---' ohitetaan kommenttina. Esim:
    --- Grep-harjoitukset
    # Etsi kaikki rivit jotka sisältävät sanan 'foo'
    grep 'foo' data/file.txt
"""

import base64
import sys
import os

ENC_FILE = "data/tasks/tehtavat.txt.enc"
PLAIN_FILE = "data/tasks/tehtavat.txt"
STUDENT_MD = "./tehtavat_student.md"


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
    """Salaa tavallisen tiedoston ja exportaa opiskelijoiden Markdown-lista"""
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
    
    # Exportaa opiskelijoiden Markdown-lista automaattisesti salauksen jälkeen
    print("📝 Viedään opiskelijoiden Markdown-lista...")
    export_student_markdown()


def export_student_markdown(output=STUDENT_MD):
    """Luo Markdown-tiedosto, joka sisältää numeroidun listan tehtävistä ilman vastauksia.

    Lukee ensisijaisesti plain-tekstitiedoston (`PLAIN_FILE`). Jos sitä ei ole,
    yrittää purkaa sisällön `ENC_FILE`-tiedostosta ilman tallentamista.
    Ohittaa kommenttirivit jotka alkavat '---'.
    """
    # Lue sisältö joko plainista tai dekoodattuna enkoodatusta tiedostosta
    content = None
    if os.path.exists(PLAIN_FILE):
        with open(PLAIN_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
    elif os.path.exists(ENC_FILE):
        try:
            with open(ENC_FILE, 'r', encoding='utf-8') as f:
                encoded = f.read()
            content = base64.b64decode(encoded).decode('utf-8')
        except Exception as e:
            print(f"❌ Virhe lukemisessa {ENC_FILE}: {e}")
            sys.exit(1)
    else:
        print(f"❌ Ei löydy {PLAIN_FILE} tai {ENC_FILE}")
        sys.exit(1)

    lines = content.splitlines()
    tasks = []
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        # Ohita kommenttirivit jotka alkavat '---'
        if line.startswith('---'):
            i += 1
            continue
        # Odotetaan, että tehtävän kuvaus alkaa rivillä '#' ja seuraava ei-tyhjä rivi on vastaus
        if line.startswith('#'):
            desc = line.lstrip('#').strip()
            tasks.append(desc)
        i += 1

    # Rakennetaan markdown
    md_lines = ["# Tehtävät", "", "Seuraavat tehtävät — vastaukset jätetty pois.", ""]
    for idx, t in enumerate(tasks, start=1):
        md_lines.append(f"{idx}. {t}")
    md = "\n".join(md_lines) + "\n"

    # Varmista hakemisto
    out_dir = os.path.dirname(output)
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    try:
        with open(output, 'w', encoding='utf-8') as f:
            f.write(md)
        print(f"✅ Markdown luotu: {output}")
    except Exception as e:
        print(f"❌ Virhe kirjoitettaessa {output}: {e}")
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
    elif cmd in ("student-md", "export-md", "markdown"):
        export_student_markdown()
    elif cmd == "help" or cmd == "-h" or cmd == "--help":
        show_help()
    else:
        print(f"❌ Tuntematon komento: {cmd}")
        print()
        show_help()
        sys.exit(1)
