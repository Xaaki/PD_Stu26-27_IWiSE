"""Własne testy bazy wiedzy w Elite Dangerous (Zadanie Z2)."""
from pathlib import Path
from silnik import wczytaj_baze, wnioskuj_w_przod, wnioskuj_wstecz

baza = wczytaj_baze(Path(__file__).parent.parent / "wiedza" / "moja_dziedzina.json")

PRZYPADKI = [
    # T1: Typowy przypadek walki na bliskim dystansie
    (
        {
            "przeciwnik_obecny": "Tak",
            "typ_statku": "Bojowy",
            "stan_oslon_proc": 80,
            "stan_wep": "Pusty",
            "dystans_do_celu": 1200
        },
        "PIP_2SYS_0ENG_4WEP",
        ["P1", "R3"]
    ),
    # T2: Typowy przypadek ucieczki statkiem eksploracyjnym
    (
        {
            "przeciwnik_obecny": "Tak",
            "typ_statku": "Exploracyjny",
            "stan_oslon_proc": 100,
            "stan_wep": "Optymalny",
            "dystans_do_celu": 3000
        },
        "PIP_2SYS_4ENG_0WEP",
        ["P2_1", "R7"]
    ),
    # T3: Wartość graniczna (stan_oslon_proc na progu 25%)
    (
        {
            "przeciwnik_obecny": "Tak",
            "typ_statku": "Bojowy",
            "stan_oslon_proc": 25,
            "stan_wep": "Pusty",
            "dystans_do_celu": 1000
        },
        "PIP_3SYS_1ENG_2WEP",
        ["P1", "R1"]
    ),
    # T4: Brak wyniku (niekompletne lub niespójne wejście niezdefiniowane w bazie)
    (
        {
            "przeciwnik_obecny": "Nie",
            "typ_statku": "InnyNiezdefiniowany",
            "stan_oslon_proc": 50,
            "stan_wep": "Pusty",
            "dystans_do_celu": 5000
        },
        None,
        None
    ),
    # T5: Konflikt reguł (stan_oslon_proc == 0 aktywuje R16_KRAŃCOWA_TARCZA, wygrywającą z ogólną R1)
    (
        {
            "przeciwnik_obecny": "Tak",
            "typ_statku": "Bojowy",
            "stan_oslon_proc": 0,
            "stan_wep": "Pusty",
            "dystans_do_celu": 1000
        },
        "PIP_3SYS_1ENG_2WEP",
        ["P1", "R1"]
    )
]

ok = 0
for wejscie, oczekiwane, oczekiwany_slad in PRZYPADKI:
    fakty, slad = wnioskuj_w_przod(baza, wejscie)
    w_przod_ok = fakty.get("decyzja") == oczekiwane and (oczekiwany_slad is None or slad == oczekiwany_slad)

    zadane = []
    def zapytaj(atrybut, powod):
        zadane.append(atrybut)
        return wejscie.get(atrybut)

    wstecz = wnioskuj_wstecz(baza, "decyzja", {}, zapytaj, [])
    wstecz_ok = wstecz == oczekiwane and len(zadane) == len(set(zadane))

    status = "OK " if w_przod_ok and wstecz_ok else "BŁĄD"
    ok += w_przod_ok and wstecz_ok
    print(f"[{status}] {wejscie} -> w przód: {fakty.get('decyzja')}, wstecz: {wstecz}, pytań: {len(zadane)}")

print(f"\nZaliczone przypadki: {ok}/{len(PRZYPADKI)}")