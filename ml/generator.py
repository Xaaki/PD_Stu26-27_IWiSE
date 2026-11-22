"""Generator danych z silnika wnioskującego oraz podział train/test bez przecieku (Zadanie Z4)."""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedGroupKFold

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "se"))
from silnik import wczytaj_baze, wnioskuj_w_przod  # noqa: E402

SEED = 42
N_SAMPLES = 2500
BAZA_PATH = ROOT / "wiedza" / "moja_dziedzina.json"
ML_DIR = ROOT / "ml"


def main():
    baza = wczytaj_baze(BAZA_PATH)
    atrybuty = baza["atrybuty"]
    cel = baza["cel"]
    wejscia = [n for n, opis in atrybuty.items() if opis["typ"] != "wniosek"]

    rng = np.random.default_rng(SEED)
    wiersze = []
    luki = []

    for i in range(1, N_SAMPLES + 1):
        x = {}
        for nazwa in wejscia:
            opis = atrybuty[nazwa]
            if opis["typ"] == "liczba":
                lo, hi = opis["zakres"]
                x[nazwa] = int(rng.integers(lo, hi + 1))
            else:
                x[nazwa] = str(rng.choice(opis["wartosci"]))

        fakty, _ = wnioskuj_w_przod(baza, x)
        decyzja = fakty.get(cel)
        if decyzja is None:
            luki.append(x)
            continue

        wiersze.append({
            "sample_id": i,
            **x,
            cel: decyzja,
            "label_source": "rule_engine",
        })

    df = pd.DataFrame(wiersze)
    ML_DIR.mkdir(parents=True, exist_ok=True)

    dane_path = ML_DIR / "dane.csv"
    luki_path = ML_DIR / "luki.json"
    podzial_path = ML_DIR / "podzial.json"

    df.to_csv(dane_path, index=False, encoding="utf-8")
    luki_path.write_text(json.dumps(luki, ensure_ascii=False, indent=2), encoding="utf-8")

    # Grupowany i warstwowy podział (identyczne wejścia w tej samej części)
    grupy = df[wejscia].astype(str).agg("|".join, axis=1)
    splitter = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=SEED)
    train_idx, test_idx = next(splitter.split(df[wejscia], df[cel], grupy))

    train_df = df.iloc[train_idx]
    test_df = df.iloc[test_idx]

    statystyki_klas = {}
    for klasa, grupa_df in df.groupby(cel):
        statystyki_klas[klasa] = {
            "przypadki": int(len(grupa_df)),
            "unikalne_wejscia": int(grupa_df[wejscia].drop_duplicates().shape[0]),
            "trening": int((train_df[cel] == klasa).sum()),
            "test": int((test_df[cel] == klasa).sum()),
        }

    podzial = {
        "metadane": {
            "seed": SEED,
            "sposob_probkowania": "jednorodne losowanie niezależne z dziedzin atrybutów",
            "n_wygenerowanych": N_SAMPLES,
            "liczba_wierszy": int(len(df)),
            "unikalne_wejscia": int(df[wejscia].drop_duplicates().shape[0]),
            "liczba_luk": len(luki),
            "szum_etykiet": 0.0,
            "metoda_podzialu": "StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)",
            "udzial_testu": round(len(test_df) / len(df), 4),
        },
        "cechy_wejsciowe": wejscia,
        "cel": cel,
        "statystyki_klas": statystyki_klas,
        "train_ids": train_df["sample_id"].astype(int).tolist(),
        "test_ids": test_df["sample_id"].astype(int).tolist(),
    }
    podzial_path.write_text(json.dumps(podzial, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Zapisano {dane_path} ({len(df)} wierszy, {podzial['metadane']['unikalne_wejscia']} unikalnych wejść)")
    print(f"Luki: {len(luki)} -> {luki_path}")
    print(f"Podział: trening={len(train_df)}, test={len(test_df)} -> {podzial_path}")
    print("\nRozkład klas:")
    for klasa, s in sorted(statystyki_klas.items()):
        print(f"  {klasa:20s} | razem={s['przypadki']:4d} | unikalne={s['unikalne_wejscia']:4d} | train={s['trening']:4d} | test={s['test']:4d}")


if __name__ == "__main__":
    main()
