#!/usr/bin/env python3
import subprocess
import shlex
import json
import os
import sys

TEHTAVAT_TIEDOSTO = "data/tehtavat.txt"
TILA_TIEDOSTO = "data/tila.json"

SALLITUT_KOMENNOT = ("grep", "wc", "sort", "uniq", "head", "tail", "cat")

# ---------- Apufunktiot ----------

def lue_tehtavat(tiedosto):
    tehtavat = []
    with open(tiedosto, encoding="utf-8") as f:
        for rivi in f:
            rivi = rivi.strip()
            if not rivi or ":::" not in rivi:
                continue
            kuvaus, oikea = map(str.strip, rivi.split(":::", 1))
            tehtavat.append((kuvaus, oikea))
    return tehtavat


def turvallinen_komento(cmd):
    return cmd.split()[0] in SALLITUT_KOMENNOT


def aja_komento(cmd):
    try:
        args = shlex.split(cmd)
        res = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=3
        )
        return res.stdout.strip()
    except Exception as e:
        return f"(virhe: {e})"


def lataa_tila():
    if os.path.exists(TILA_TIEDOSTO):
        with open(TILA_TIEDOSTO, encoding="utf-8") as f:
            return json.load(f)
    return {}


def tallenna_tila(tila):
    with open(TILA_TIEDOSTO, "w", encoding="utf-8") as f:
        json.dump(tila, f, ensure_ascii=False, indent=2)

# ---------- CI / CHECK ----------

def check_mode():
    tehtavat = lue_tehtavat(TEHTAVAT_TIEDOSTO)
    tila = lataa_tila()

    oikein = sum(1 for v in tila.values() if v == "oikein")
    yhteensa = len(tehtavat)

    print("🔍 CHECK-MODE")
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

    while True:
        ratkaisemattomat = [
            i for i in range(len(tehtavat))
            if tila.get(str(i)) != "oikein"
        ]

        if not ratkaisemattomat:
            print("\n🎉 Kaikki tehtävät suoritettu!")
            return

        i = ratkaisemattomat[0]
        kuvaus, oikea = tehtavat[i]

        print(f"\n📝 Tehtävä {i+1}/{len(tehtavat)}")
        print(kuvaus)

        cmd = input("💻 Komento (skip / exit): ").strip()

        if cmd == "exit":
            tallenna_tila(tila)
            print("💾 Tila tallennettu.")
            return

        if cmd == "skip":
            tila[str(i)] = "skip"
            tallenna_tila(tila)
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
            tila[str(i)] = "väärin"
        else:
            # Verrataan rivit set-muodossa, jotta rivijärjestys ei pilaa vertailua
            opiskelija_set = set(opiskelija_res.splitlines())
            oikea_set = set(oikea_res.splitlines()) if oikea_res else set()

            if opiskelija_set == oikea_set:
                print("✅ Oikein")
                tila[str(i)] = "oikein"
            else:
                print("❌ Väärin")
                print("— Oikea tulos —")
                print(oikea_res or "(ei tulosta)")
                print("— Sinun tuloksesi —")
                print(opiskelija_res or "(ei tulosta)")
                tila[str(i)] = "väärin"

        tallenna_tila(tila)


# ---------- MAIN ----------

if __name__ == "__main__":
    if "--check" in sys.argv or "--ci" in sys.argv:
        check_mode()
    else:
        interactive_mode()
