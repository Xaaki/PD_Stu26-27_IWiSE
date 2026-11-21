# PD_Stu26-27_IWiSE

Repozytorium projektowe z przedmiotu **Inżynieria wiedzy i maszynowe uczenie** (UKW, Informatyka, II rok, 2026/2027).  
**Autor:** Piotr Dalewski (gr. 1)  
**Dziedzina:** System wspomagający alokację PIP (`SYS` / `ENG` / `WEP`) i zarządzanie energią statku w grze *Elite Dangerous*.

## Struktura repozytorium
- `app.py` — interfejs webowy systemu ekspertowego w Streamlit (formularz generowany z pliku JSON, wynik, „co to?”, „jak?”, raport weryfikacji)
- `se/silnik.py` — silnik wnioskujący w przód i wstecz oraz moduł wyjaśnień (`opisz_regule`, `wyjasnij_jak`, `coto`, obsługa `?`)
- `se/weryfikacja.py` — statyczny weryfikator bazy wiedzy (spójność, dziedziny, nieużywane elementy, duplikaty, sprzeczności, pochłanianie, osiągalność celu)
- `se/sprawdz_format.py` — walidator formatu bazy JSON
- `se/test_silnik.py`, `se/test_moja_dziedzina.py` — testy jednostkowe silnika i własnej bazy wiedzy
- `wiedza/moja_dziedzina.json` — własna baza wiedzy (3 poziomy atrybutów: dane wejściowe → `tryb` → `decyzja`)
- `wiedza/kawa.json` — wzorcowa baza wiedzy z zajęć
- `IWiMU_Z1_*`, `IWiMU_Z2_*`, `IWiMU_Z3_*` — materiały i sprawozdania z kolejnych laboratoriów

## Uruchomienie

### Konsola (silnik, testy, weryfikator)
```bash
python3 se/silnik.py
python3 se/test_silnik.py
python3 se/test_moja_dziedzina.py
python3 se/weryfikacja.py wiedza/moja_dziedzina.json
```

### Aplikacja Streamlit
```bash
source .venv/bin/activate
streamlit run app.py
```

## Zrealizowane etapy

### Zadanie Z1 — Reprezentacja wiedzy i drzewo decyzyjne
- Opracowanie dziedziny problemowej (alokacja mocy `SYS`/`ENG`/`WEP` w *Elite Dangerous*) oraz drzewa decyzyjnego (`IWiMU_Z1_Piotr_Dalewski.lrn`, `IWiMU_Z1_Piotr_Dalewski_drzewo.drawio`).

### Zadanie Z2 — Silnik wnioskujący i baza wiedzy JSON
- Implementacja `regula_spelniona`, `wnioskuj_w_przod` i `wnioskuj_wstecz` w `se/silnik.py` (`TODO 1–4`).
- Utworzenie bazy `wiedza/moja_dziedzina.json` z łańcuchem wnioskowania na 3 poziomach, polami `metafora` i `coto`.
- Zaliczone testy: `se/test_silnik.py` (`5/5`) oraz `se/test_moja_dziedzina.py` (`5/5`, w tym wartość graniczna i konflikt reguł).

### Zadanie Z3 — Wyjaśnienia, weryfikacja bazy i interfejs Streamlit (Kamień milowy A)
- Rozbudowa `se/silnik.py` o wyjaśnienia **„jak?”** (`wyjasnij_jak`, `opisz_regule`), **„dlaczego?”** (`?` w konsoli) oraz **„co to?”** (`coto`).
- Uzupełnienie `se/weryfikacja.py` (`TODO 3–7`): wykrywa `10/10` problemów w `kawa_z_bledami.json` (6 błędów, 4 uwagi) oraz `0` problemów w `kawa.json` i `moja_dziedzina.json`.
- Uruchomienie interfejsu `app.py` w Streamlit na bazie `wiedza/moja_dziedzina.json`.

#### Ograniczenia weryfikatora (`wiedza/moja_dziedzina.json`)
- Weryfikator nie wykrywa nakładających się przedziałów liczbowych (np. `R16_KRAŃCOWA_TARCZA` z `stan_oslon_proc == 0` oraz `R1`/`R2` z `stan_oslon_proc <= 25`, czy `R17_KRAŃCOWY_DYSTANS` z `dystans_do_celu >= 6000` oraz `R5`/`R6` z `dystans_do_celu > 1500` — w silniku wygrywa pierwsza pasująca reguła).
- Nie sprawdza pełnego pokrycia wszystkich kombinacji wartości wejściowych (np. w trybie `ucieczka` dla statku `Exploracyjny` i `Górniczy` decyzja nie zależy od `stan_oslon_proc` ani `dystans_do_celu`).
- Nie wykrywa cykli w grafie wniosków ani nie ocenia merytorycznej trafności wiedzy (walidacja ekspercka).
