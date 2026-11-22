"""Uczenie drzewa decyzyjnego w Pipeline wyłącznie na zbiorze treningowym (Zadanie Z4)."""
import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.tree import DecisionTreeClassifier, export_text, plot_tree

ROOT = Path(__file__).resolve().parent.parent
ML_DIR = ROOT / "ml"
BAZA_PATH = ROOT / "wiedza" / "moja_dziedzina.json"

MAX_DEPTH = 6
CRITERION = "gini"
RANDOM_STATE = 42


def main():
    baza = json.loads(BAZA_PATH.read_text(encoding="utf-8"))
    podzial = json.loads((ML_DIR / "podzial.json").read_text(encoding="utf-8"))
    df = pd.read_csv(ML_DIR / "dane.csv", encoding="utf-8")

    # Wyłącznie zbiór treningowy — zbiór testowy pozostaje nieużywany do Z6
    train_df = df[df["sample_id"].isin(podzial["train_ids"])].copy()

    wejscia = podzial["cechy_wejsciowe"]
    cel = podzial["cel"]
    symb = [n for n in wejscia if baza["atrybuty"][n]["typ"] == "wybor"]

    X_train = train_df[wejscia]
    y_train = train_df[cel]

    kod = ColumnTransformer(
        [("sym", OneHotEncoder(handle_unknown="ignore", sparse_output=False), symb)],
        remainder="passthrough",
    )
    model = Pipeline([
        ("kod", kod),
        ("drzewo", DecisionTreeClassifier(
            criterion=CRITERION,
            max_depth=MAX_DEPTH,
            random_state=RANDOM_STATE,
        )),
    ])
    model.fit(X_train, y_train)

    drzewo = model.named_steps["drzewo"]
    nazwy_cech = list(model.named_steps["kod"].get_feature_names_out())
    # Skrócenie prefiksów ColumnTransformer dla czytelności
    nazwy_cech = [n.replace("sym__", "").replace("remainder__", "") for n in nazwy_cech]

    tekst = export_text(drzewo, feature_names=nazwy_cech, decimals=1)
    drzewo_txt = ML_DIR / "drzewo.txt"
    drzewo_txt.write_text(tekst, encoding="utf-8")

    fig, ax = plt.subplots(figsize=(28, 14), dpi=180)
    plot_tree(
        drzewo,
        feature_names=nazwy_cech,
        class_names=list(drzewo.classes_),
        filled=True,
        rounded=True,
        fontsize=8,
        ax=ax,
    )
    fig.tight_layout()
    drzewo_png = ML_DIR / "drzewo.png"
    fig.savefig(drzewo_png, dpi=180)
    plt.close(fig)

    print(f"Dopasowano drzewo na {len(X_train)} przypadkach treningowych.")
    print(f"Kryterium: {CRITERION} | Głębokość: {drzewo.get_depth()} | Liczba liści: {drzewo.get_n_leaves()}")
    print(f"Korzeń: {nazwy_cech[drzewo.tree_.feature[0]]} <= {drzewo.tree_.threshold[0]:.2f}")
    print(f"Zapisano: {drzewo_txt} oraz {drzewo_png}")


if __name__ == "__main__":
    main()
