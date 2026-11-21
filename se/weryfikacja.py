"""Weryfikacja bazy wiedzy (odpowiednik programu Cake z pakietu SPHINX) — spotkanie 3.
Uruchom: python se/weryfikacja.py wiedza/kawa_z_bledami.json
"""
import sys
from pathlib import Path

from silnik import OPERATORY, wczytaj_baze


def weryfikuj(baza):
    """Zwraca listę (poziom, komunikat); poziom to 'BŁĄD' albo 'UWAGA'."""
    raport = []
    atrybuty = baza["atrybuty"]
    reguly = baza["reguly"]

    # Test 1: powtórzone identyfikatory reguł
    ids = [r["id"] for r in reguly]
    for id_ in sorted({i for i in ids if ids.count(i) > 1}):
        raport.append(("BŁĄD", f"Powtórzony identyfikator reguły {id_}"))

    # Test 2: niezadeklarowane atrybuty i nieznane operatory w warunkach
    for r in reguly:
        for atr, op, wart in r["jesli"]:
            if atr not in atrybuty:
                raport.append(("BŁĄD", f"{r['id']}: niezadeklarowany atrybut '{atr}'"))
            if op not in OPERATORY:
                raport.append(("BŁĄD", f"{r['id']}: nieznany operator '{op}'"))

    # TODO 3: wartości spoza dziedziny — dla atrybutów z listą "wartosci"
    #         sprawdź warunki z operatorem == lub != (BŁĄD).
    for r in reguly:
        for atr, op, wart in r["jesli"]:
            if atr in atrybuty and "wartosci" in atrybuty[atr] and op in ("==", "!="):
                if wart not in atrybuty[atr]["wartosci"]:
                    raport.append(("BŁĄD", f"{r['id']}: wartość {wart!r} spoza dziedziny '{atr}'"))

    # TODO 4: nieużywane atrybuty wejściowe (typ inny niż "wniosek", nieobecne w żadnym warunku)
    #         oraz nieużywane wartości atrybutów typu "wybor" (UWAGA).
    uzyte_atrybuty = {atr for r in reguly for atr, _, _ in r["jesli"]}
    uzyte_wartosci = {(atr, wart) for r in reguly for atr, op, wart in r["jesli"] if op in ("==", "!=")}
    for nazwa, opis in atrybuty.items():
        if opis.get("typ") != "wniosek" and nazwa not in uzyte_atrybuty:
            raport.append(("UWAGA", f"Atrybut '{nazwa}' nie jest używany w żadnej regule"))
        if opis.get("typ") == "wybor":
            for wart in opis.get("wartosci", []):
                if (nazwa, wart) not in uzyte_wartosci:
                    raport.append(("UWAGA", f"Wartość {wart!r} atrybutu '{nazwa}' nieużywana"))

    # TODO 5: warunek niemożliwy do spełnienia — warunek atr == wart, gdzie atr jest typu "wniosek",
    #         a żadna reguła nie ma wniosku ["atr", "wart"] (BŁĄD).
    wytwarzane = {tuple(r["to"]) for r in reguly}
    for r in reguly:
        for atr, op, wart in r["jesli"]:
            if atr in atrybuty and atrybuty[atr].get("typ") == "wniosek" and op == "==":
                if (atr, wart) not in wytwarzane:
                    raport.append(("BŁĄD", f"{r['id']}: warunek {atr} == {wart!r} nigdy niespełniony"))

    # TODO 6: porównaj każdą parę reguł (warunki zamień na zbiory krotek: {tuple(w) for w in r["jesli"]}):
    #   - te same warunki i ten sam wniosek       -> duplikat (UWAGA)
    #   - te same warunki, inna wartość wniosku   -> sprzeczność (BŁĄD)
    #   - ten sam wniosek, warunki A ⊂ warunki B  -> B jest pochłaniana przez A (UWAGA)
    for i, ra in enumerate(reguly):
        wa = {tuple(w) for w in ra["jesli"]}
        ta = tuple(ra["to"])
        for rb in reguly[i + 1:]:
            wb = {tuple(w) for w in rb["jesli"]}
            tb = tuple(rb["to"])
            if wa == wb and ta == tb:
                raport.append(("UWAGA", f"{ra['id']} i {rb['id']} są identyczne (duplikat)"))
            elif wa == wb and ta[0] == tb[0] and ta[1] != tb[1]:
                raport.append(("BŁĄD", f"{ra['id']} i {rb['id']} są sprzeczne: te same warunki"))
            elif ta == tb and wa < wb:
                raport.append(("UWAGA", f"{rb['id']} jest pochłaniana przez {ra['id']} (zbędna)"))
            elif ta == tb and wb < wa:
                raport.append(("UWAGA", f"{ra['id']} jest pochłaniana przez {rb['id']} (zbędna)"))

    # TODO 7: cel główny baza["cel"] musi być wnioskiem co najmniej jednej reguły (BŁĄD).
    if not any(r["to"][0] == baza["cel"] for r in reguly):
        raport.append(("BŁĄD", f"Cel główny '{baza['cel']}' nie jest wnioskiem żadnej reguły"))

    return raport


if __name__ == "__main__":
    plik = sys.argv[1] if len(sys.argv) > 1 else Path(__file__).parent.parent / "wiedza" / "kawa.json"
    wyniki = weryfikuj(wczytaj_baze(plik))
    if not wyniki:
        print("Baza wiedzy nie zawiera wykrytych problemów.")
    for poziom, komunikat in wyniki:
        print(f"[{poziom}] {komunikat}")
    print(f"\nZnaleziono: {len(wyniki)} (w kawa_z_bledami.json jest 10 problemów do wykrycia)")
