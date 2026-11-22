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

### Zadanie Z4 — Generator danych i drzewo decyzyjne
- **`ml/generator.py`**: generuje `ml/dane.csv` (2500 przypadków, 2500 unikalnych wejść, ziarno `42`, 0 luk w `ml/luki.json`, brak szumu etykiet) oraz grupowany, warstwowy podział `StratifiedGroupKFold(n_splits=5)` w `ml/podzial.json` (trening: 2000, test: 500 — nieużywany do Z6). Wszystkie 12 klas ma od 25 do 864 unikalnych przypadków.
- **`ml/trening.py`**: uczy `Pipeline` (`ColumnTransformer` + `OneHotEncoder` + `DecisionTreeClassifier(criterion="gini", max_depth=6, random_state=42)`) wyłącznie na zbiorze treningowym; zapisuje `ml/drzewo.txt` (głębokość 5, 14 liści, korzeń `przeciwnik_obecny_Tak <= 0.5`) i `ml/drzewo.png`.

#### Porównanie drzewa z regułami eksperta (`ml/drzewo.txt` vs `wiedza/moja_dziedzina.json`)
1. **Odtworzenie progu osłon (`stan_oslon_proc <= 25.5`):** dla `przeciwnik_obecny == "Nie"` i `typ_statku == "Exploracyjny"` drzewo dzieli po `stan_oslon_proc <= 25.5` na `PIP_3SYS_3ENG_0WEP` i `PIP_1SYS_4ENG_1WEP`, co dokładnie odpowiada `P3 + R11` / `R12` (`<= 25` / `> 25`), mimo braku cechy pośredniej `tryb`.
2. **Uproszczenie dwóch reguł w jedną gałąź:** dla `przeciwnik_obecny == "Tak"` i `typ_statku_Bojowy <= 0.5` drzewo od razu przypisuje `PIP_2SYS_4ENG_0WEP`, łącząc reguły `P2_1 + R7` (`Exploracyjny`) oraz `P2_2 + R8` (`Górniczy`), które mają wspólną konkluzję.
3. **Przybliżenie progu dystansu z próbki (`dystans_do_celu <= 1500`):** w trzech gałęziach próg `1500` z `R3–R6` i `R14–R15` został wyuczony jako `1482.5`, `1489.0` oraz `1541.5` — wynika to z losowego próbkowania i mniejszej liczebności podzbiorów (np. 20 przypadków treningowych dla `PIP_2SYS_0ENG_4WEP`).

#### Ograniczenia
- Zgodność drzewa z etykietami z silnika mierzy wyłącznie to, jak dobrze model odtwarza reguły z `moja_dziedzina.json`, a nie ich merytoryczną trafność (walidacja wymagałaby etykiet eksperta).
- Przy losowym próbkowaniu jednorodnym klasy o wąskich warunkach (np. `R3`, `R4`) są znacznie rzadsze (25–28 przykładów) niż klasy ogólne (`R7`/`R8` — 864 przykłady), co obniża precyzję estymacji progów liczbowych.
- Reguły krańcowe `R16_KRAŃCOWA_TARCZA` i `R17_KRAŃCOWY_DYSTANS` nie występują w danych z `wnioskuj_w_przod`, bo wyprzedzają je wcześniejsze reguły `R1`/`R2` i `R5`/`R6`.

