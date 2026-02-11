#!/usr/bin/env python3
import subprocess
import shlex
import json
import os
import sys
import base64
from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional

# Ladataan konfiguraatio `configs/config.json`. Jos sitä ei ole,
# käytetään kovakoodattuja oletuksia.
CONFIG_PATH = Path("configs/config.json")

def load_config(path: Path) -> Dict[str, Any]:
    defaults = {
        "tehtavat_tiedosto": "data/tasks/tehtavat.txt.enc",
        "tila_tiedosto": "configs/tila.json",
        "results_file": "output/results.json",
        "timeout_seconds": 3,
        "allowed_commands": ["grep", "wc", "sort", "uniq", "head", "tail", "cat"],
    }
    if not path.exists():
        return defaults
    try:
        cfg = json.loads(path.read_text(encoding="utf-8"))
        # merge defaults with provided config
        for k, v in defaults.items():
            cfg.setdefault(k, v)
        return cfg
    except Exception:
        return defaults


CONFIG = load_config(CONFIG_PATH)

TEHTAVAT_TIEDOSTO = CONFIG["tehtavat_tiedosto"]
TILA_TIEDOSTO = CONFIG["tila_tiedosto"]
RESULTS_FILE = CONFIG["results_file"]
TIMEOUT_SECONDS = int(CONFIG.get("timeout_seconds", 3))
SALLITUT_KOMENNOT = tuple(CONFIG.get("allowed_commands", []))

# ---------- Apufunktiot ----------

def lue_tehtavat(tiedosto: str) -> List[Tuple[str, str]]:
    """Lue tehtävät tiedostosta.

    Tiedosto voi olla base64-enkoodattu tai tavallinen tekstitiedosto.
    Tehtäväformaatti: kuvaus aloitetaan merkillä '#' ja seuraava
    ei-tyhjä rivi on oikea komento. Kommenttirivit alkavat '---' ja ohitetaan.
    Palauttaa listan `(kuvaus, oikea_komento)` -tupleja.
    """
    p = Path(tiedosto)
    if not p.exists():
        return []

    raw = p.read_text(encoding='utf-8')

    # Yritä dekoodata base64:lla, mutta jos epäonnistuu, käytä raakatekstiä
    try:
        decoded = base64.b64decode(raw).decode('utf-8')
    except Exception:
        decoded = raw

    lines = decoded.splitlines()
    tehtavat: List[Tuple[str, str]] = []

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

        # Uusi muoto: kuvaus-rivi alkaa '#'
        if line.startswith('#'):
            kuvaus = line.lstrip('#').strip()
            # etsi seuraava ei-tyhjä rivi komennoksi
            j = i + 1
            while j < n and not lines[j].strip():
                j += 1
            oikea = lines[j].strip() if j < n else ""
            tehtavat.append((kuvaus, oikea))
            i = j + 1
            continue

        # Muoto: kuvaus on jo käsitelty yllä (#-rivinä); muuten ohitetaan
        i += 1

    return tehtavat


def turvallinen_komento(cmd: str) -> bool:
    """Tarkista, että komento käyttää vain sallittuja ohjelmia.

    Sallitaan putkitetut ja ketjutetut komennot (esim. "grep ... | wc -l").
    Tarkistus hajottaa komentorivin pipe-merkistä ja varmistaa, että
    jokaisen vaiheen ensimmäinen ohjelma on sallittujen listalla.
    """
    # Jaa putket erillisiksi vaiheiksi
    for stage in (s.strip() for s in cmd.split('|')):
        if not stage:
            return False
        try:
            prog = shlex.split(stage, posix=True)[0]
        except Exception:
            return False
        if prog not in SALLITUT_KOMENNOT:
            return False
    return True


def aja_komento(cmd):
    try:
        # Käytä timeout-arvoa konfiguraatiosta
        res = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SECONDS,
        )
        # Palauta stdout ilman loppurivejä
        return res.stdout.strip()
    except Exception as e:
        return f"(virhe: {e})"


def lataa_tila():
    p = Path(TILA_TIEDOSTO)
    if p.exists():
        try:
            return json.loads(p.read_text(encoding='utf-8'))
        except Exception:
            return {}
    return {}


def tallenna_tila(tila):
    p = Path(TILA_TIEDOSTO)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(tila, ensure_ascii=False, indent=2), encoding='utf-8')

# ---------- CI / CHECK ----------

def check_mode():
    tehtavat = lue_tehtavat(TEHTAVAT_TIEDOSTO)
    tila = lataa_tila()

    oikein = 0
    yhteensa = len(tehtavat)
    changed = False

    print("🔍 CHECK-MODE - Validoidaan uudelleen")

    for i in range(yhteensa):
        task_status = tila.get(str(i))

        # Jos tehtävä on vastauksessa objektina (uusi muoto)
        if isinstance(task_status, dict):
            status = task_status.get("status")
            student_cmd = task_status.get("student_cmd")
            correct_cmd = tehtavat[i][1]  # Lue oikea komento tehtävät-tiedostosta

            if status == "oikein" and student_cmd and correct_cmd:
                # Validoi uudelleen ajamalla komennot
                student_res = aja_komento(student_cmd)
                correct_res = aja_komento(correct_cmd)

                student_set = set(student_res.splitlines()) if student_res else set()
                correct_set = set(correct_res.splitlines()) if correct_res else set()

                if student_set == correct_set:
                    oikein += 1
                else:
                    # Validointi epäonnistui - merkitse väärin
                    tila[str(i)]["status"] = "väärin"
                    changed = True
            elif status == "oikein":
                oikein += 1
        # Vanha muoto (string)
        elif task_status == "oikein":
            oikein += 1

    # Jos jotain muuttui tilassa, tallenna se
    if changed:
        tallenna_tila(tila)

    # Rakenna koneellisesti luettava tulos
    per_task = []
    for i in range(yhteensa):
        ts = tila.get(str(i))
        if isinstance(ts, dict):
            status = ts.get("status")
            student_cmd = ts.get("student_cmd")
        else:
            status = ts if ts is not None else "ei_vastattu"
            student_cmd = None
        per_task.append({"id": i, "status": status, "student_cmd": student_cmd})

    results = {"score": oikein, "total": yhteensa, "per_task": per_task}

    # Kirjoita tulos tiedostoon ja stdoutiin
    try:
        with open(RESULTS_FILE, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

    print(json.dumps(results, ensure_ascii=False))

    print(f"Oikein: {oikein}/{yhteensa}")

    if oikein == yhteensa:
        print("✅ Kaikki tehtävät oikein")
        sys.exit(0)
    else:
        print("❌ Kaikki tehtävät eivät ole oikein")
        sys.exit(1)

# ---------- Interaktiivinen ----------

def interactive_mode():
    tehtavat = lue_tehtavat(TEHTAVAT_TIEDOSTO)
    tila = lataa_tila()
    skipped_this_session = set()

    def is_completed(task_id):
        """Tarkista onko tehtävä valmis"""
        status = tila.get(str(task_id))
        if isinstance(status, dict):
            return status.get("status") == "oikein"
        return status == "oikein"

    while True:
        ratkaisemattomat = [
            i for i in range(len(tehtavat))
            if not is_completed(i) and i not in skipped_this_session
        ]

        if not ratkaisemattomat:
            # Tarkista onko kaikki tehtävät todella suoritettu oikein
            remaining = [i for i in range(len(tehtavat)) if not is_completed(i)]
            if not remaining:
                print("\n🎉 Kaikki tehtävät suoritettu!")
            else:
                print(f"\nℹ️  Tehtäviä tekemättä: {len(remaining)}. Voit palata niihin käynnistämällä ohjelman uudestaan.")
            return

        i = ratkaisemattomat[0]
        kuvaus, oikea = tehtavat[i]

        print(f"\n📝 Tehtävä {i+1}/{len(tehtavat)}")
        print(f"{i+1}. {kuvaus}")

        cmd = input("💻 Komento (skip / exit / lista): ").strip()

        if not cmd:
            print("⚠️  Syötä komento tai käytä skip/exit/lista")
            continue

        if cmd == "exit":
            tallenna_tila(tila)
            print("💾 Tila tallennettu.")
            # Näytä montako tehtävää on vielä tekemättä ja ohje palata niihin
            remaining = [i for i in range(len(tehtavat)) if not is_completed(i)]
            tehdyt = sum(1 for i in range(len(tehtavat)) if is_completed(i))
            total = len(tehtavat)
            if remaining:
                print(f"ℹ️  Tehty: {tehdyt}/{total}. Tehtäviä tekemättä: {len(remaining)}. Voit palata niihin käynnistämällä ohjelman uudestaan.")
            else:
                print(f"\n🎉 Kaikki tehtävät suoritettu! Tehty: {tehdyt}/{total}")
            return

        if cmd == "lista":
            print("\n📋 Tehtävien status:")
            for j in range(len(tehtavat)):
                task_status = tila.get(str(j))
                # Jos tehtävä on tallennettu objektina
                if isinstance(task_status, dict):
                    if task_status.get("status") == "oikein":
                        status_msg = "✅ Oikein"
                    elif task_status.get("status") == "väärin":
                        status_msg = "❌ Väärin"
                    else:
                        status_msg = "⏳ Skipattu"
                else:
                    # Ei tallennettua tilaa
                    if j in skipped_this_session:
                        status_msg = "⏳ Skipattu"
                    elif task_status is None:
                        status_msg = "⏳ Ei vastattu"
                    elif task_status == "oikein":
                        status_msg = "✅ Oikein"
                    elif task_status == "väärin":
                        status_msg = "❌ Väärin"
                    else:
                        status_msg = "⏳ Ei vastattu"

                print(f"{status_msg:<15} {j+1}. {tehtavat[j][0]}")
            print()
            continue

        if cmd == "skip":
            skipped_this_session.add(i)
            print(f"⏭️  Tehtävä {i+1} skipattu. Seuraavaan...")
            continue

        if not turvallinen_komento(cmd):
            print("❌ Komento ei ole sallittu tässä harjoituksessa.")
            continue

        # Suoritetaan komennot
        opiskelija_res = aja_komento(cmd)
        oikea_res = aja_komento(oikea)

        # Jos komento epäonnistui (returncode != 0) tai stdout tyhjä, merkitään väärin
        if not opiskelija_res:
            print("❌ Sinun komennollasi ei tullut tulosta tai se epäonnistui.")
            tila[str(i)] = {
                "status": "väärin",
                "student_cmd": cmd
            }
        else:
            # Verrataan rivit set-muodossa, jotta rivijärjestys ei pilaa vertailua
            opiskelija_set = set(opiskelija_res.splitlines())
            oikea_set = set(oikea_res.splitlines()) if oikea_res else set()

            # Tulostetaan tulokset ja vertailu
            print("— Oikea vastaus —")
            print(oikea_res)
            print("— Sinun vastaus —")
            print(opiskelija_res)
            print("— Vertailtavat rivit (set-muodossa) —")
            print("Oikea:", sorted(oikea_set))
            print("Sinun:", sorted(opiskelija_set))

            if opiskelija_set == oikea_set:
                print("✅ Oikein")
                tila[str(i)] = {
                    "status": "oikein",
                    "student_cmd": cmd
                }
            else:
                print("❌ Väärin")
                # Näytetään erot riveittäin
                only_oikea = sorted(oikea_set - opiskelija_set)
                only_sinu = sorted(opiskelija_set - oikea_set)
                if only_oikea:
                    print("Rivejä vain oikeassa tuloksessa:")
                    for r in only_oikea:
                        print(f"+ {r}")
                if only_sinu:
                    print("Rivejä vain sinun tuloksessasi:")
                    for r in only_sinu:
                        print(f"- {r}")
                tila[str(i)] = {
                    "status": "väärin",
                    "student_cmd": cmd
                }

        tallenna_tila(tila)


# ---------- MAIN ----------

if __name__ == "__main__":
    if "--check" in sys.argv or "--ci" in sys.argv:
        check_mode()
    else:
        interactive_mode()
