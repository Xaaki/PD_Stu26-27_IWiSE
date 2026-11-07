"""Silnik wnioskujący — uzupełnione TODO 1-4 zgodnie z wymaganiami Z2."""
import json
import operator
from pathlib import Path

OPERATORY = {
    "==": operator.eq, "!=": operator.ne,
    ">": operator.gt, ">=": operator.ge,
    "<": operator.lt, "<=": operator.le,
}


def wczytaj_baze(sciezka):
    return json.loads(Path(sciezka).read_text(encoding="utf-8"))


def warunek_spelniony(warunek, fakty):
    """warunek to lista [atrybut, operator, wartość], np. ["stan_oslon_proc", ">", 25]."""
    atrybut, op, wartosc = warunek
    return atrybut in fakty and fakty[atrybut] is not None and OPERATORY[op](fakty[atrybut], wartosc)


def regula_spelniona(regula, fakty):
    # TODO 1: zwróć True, jeśli WSZYSTKIE warunki z regula["jesli"] są spełnione.
    return all(warunek_spelniony(w, fakty) for w in regula["jesli"])


def wnioskuj_w_przod(baza, fakty):
    """Zwraca (fakty po wnioskowaniu, lista id odpalonych reguł)."""
    fakty = dict(fakty)
    slad = []
    zmiana = True
    while zmiana:
        zmiana = False
        for regula in baza["reguly"]:
            atrybut, wartosc = regula["to"]
            # TODO 2: jeśli atrybutu jeszcze nie ma w faktach, a reguła jest spełniona
            if atrybut not in fakty and regula_spelniona(regula, fakty):
                fakty[atrybut] = wartosc
                slad.append(regula["id"])
                zmiana = True
    return fakty, slad


def wnioskuj_wstecz(baza, cel, fakty, zapytaj, slad=None, powod=None):
    """Ustala wartość atrybutu `cel`. Brakujące dane pobiera funkcją zapytaj(atrybut, powod)."""
    if slad is None:
        slad = []
    if cel in fakty:                                   # już wiemy — nie pytamy drugi raz
        return fakty[cel]
    if cel not in baza["atrybuty"]:
        raise ValueError(f"Niezadeklarowany atrybut: {cel}")

    reguly = [r for r in baza["reguly"] if r["to"][0] == cel]

    # Wniosek bez reguł to luka w bazie: nie pytamy użytkownika o gotową decyzję.
    if not reguly and baza["atrybuty"][cel]["typ"] == "wniosek":
        fakty[cel] = None
        return None

    # TODO 3: jeśli nie ma reguł (cel to dana wejściowa), zapytaj użytkownika
    if not reguly:
        fakty[cel] = zapytaj(cel, powod)
        return fakty[cel]

    for regula in reguly:
        spelniona = True
        for atrybut, op, wartosc in regula["jesli"]:
            # TODO 4: ustal atrybut tą samą funkcją (rekurencja)
            znana = wnioskuj_wstecz(baza, atrybut, fakty, zapytaj, slad, regula)
            if znana is None or not OPERATORY[op](znana, wartosc):
                spelniona = False
                break
        if spelniona:
            fakty[cel] = regula["to"][1]
            slad.append(regula["id"])
            return fakty[cel]

    fakty[cel] = None
    return None


def zapytaj_konsola(baza):
    """Pytanie w konsoli."""
    def zapytaj(atrybut, powod):
        opis = baza["atrybuty"].get(atrybut, {})
        podpowiedz = f" ({'/'.join(opis['wartosci'])})" if "wartosci" in opis else ""
        while True:
            odp = input(f"{opis.get('pytanie', atrybut)}{podpowiedz} ").strip()
            if opis.get("typ") == "liczba":
                try:
                    return float(odp.replace(",", "."))
                except ValueError:
                    print("   Podaj liczbę.")
                    continue
            if "wartosci" in opis and odp not in opis["wartosci"]:
                print("   Dozwolone:", ", ".join(opis["wartosci"]))
                continue
            return odp
    return zapytaj


if __name__ == "__main__":
    PLIK_BAZY = Path(__file__).parent.parent / "wiedza" / "moja_dziedzina.json"
    FAKTY = {
        "przeciwnik_obecny": "Tak",
        "typ_statku": "Bojowy",
        "stan_oslon_proc": 15,
        "stan_wep": "Pusty",
        "dystans_do_celu": 2000
    }

    baza = wczytaj_baze(PLIK_BAZY)
    cel = baza["cel"]

    print("=== Wnioskowanie w przód ===")
    fakty, slad = wnioskuj_w_przod(baza, FAKTY)
    print("Wynik:", fakty.get(cel), "| reguły:", " -> ".join(slad))

    print("\n=== Wnioskowanie wstecz ===")
    slad_wstecz = []
    print("Polecam:", wnioskuj_wstecz(baza, cel, {}, zapytaj_konsola(baza), slad_wstecz))
    print("Reguły:", " -> ".join(slad_wstecz))