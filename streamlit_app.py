import json
from pathlib import Path
from collections import Counter

import streamlit as st

st.set_page_config(
    page_title="Roulette Lab Live",
    page_icon="🎯",
    layout="wide"
)

HISTORY_FILE = Path("roulette_history.json")


def load_history():
    if HISTORY_FILE.exists():
        try:
            return json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return []
    return []


def save_history(history):
    HISTORY_FILE.write_text(
        json.dumps(history),
        encoding="utf-8"
    )


if "history" not in st.session_state:
    st.session_state.history = load_history()

st.title("🎯 Roulette Lab Live")
st.caption("Analiză statistică a rezultatelor introduse manual")

st.info(
    "Scorurile sunt clasamente statistice bazate pe istoricul "
    "introdus. Nu prezic sigur următoarea rotire."
)

st.subheader("1. Adaugă un rezultat")

with st.form("add_result", clear_on_submit=True):
    number = st.number_input(
        "Numărul ieșit la ruletă (0–36)",
        min_value=0,
        max_value=36,
        value=0,
        step=1
    )
    submitted = st.form_submit_button("➕ Adaugă rezultatul")

if submitted:
    st.session_state.history.append(int(number))
    save_history(st.session_state.history)
    st.success(f"Rezultatul {number} a fost salvat.")
    st.rerun()

history = st.session_state.history

st.subheader("2. Istoricul rezultatelor")

left, middle, right = st.columns(3)
left.metric("Total rezultate", len(history))
middle.metric("Ultimele 100", min(100, len(history)))
right.metric("Ultimele 500", min(500, len(history)))

window = st.radio(
    "Alege istoricul pentru analiză",
    ["Ultimele 100", "Ultimele 500", "Tot istoricul"],
    horizontal=True
)

if window == "Ultimele 100":
    data = history[-100:]
elif window == "Ultimele 500":
    data = history[-500:]
else:
    data = history[:]

st.subheader("3. Cele 5 numere candidate")

if len(data) < 5:
    st.warning("Introdu cel puțin 5 rezultate pentru a începe analiza.")
else:
    counts = Counter(data)
    total = len(data)

    ranked = sorted(
        range(37),
        key=lambda n: (counts[n], -n),
        reverse=True
    )[:5]

    st.caption(
        f"Analiză pe {total} rezultate. Scorul reprezintă frecvența "
        "observată, nu probabilitatea reală a următoarei rotiri."
    )

    for position, candidate in enumerate(ranked, start=1):
        score = counts[candidate] / total * 100
        label = "⭐ FAVORIT STATISTIC" if position == 1 else f"Candidat {position}"
        st.write(f"**{label}: numărul {candidate}**")
        st.progress(min(1.0, score / 100))
        st.write(
            f"Scor de frecvență: {score:.2f}% "
            f"({counts[candidate]} apariții din {total})"
        )

    st.subheader("4. Frecvența tuturor numerelor")
    frequency_rows = [
        {"Număr": n, "Apariții": counts[n]}
        for n in range(37)
    ]
    st.dataframe(
        frequency_rows,
        use_container_width=True,
        hide_index=True
    )

st.subheader("5. Ultimele rezultate")
if history:
    st.write(" → ".join(map(str, history[-30:])))
else:
    st.write("Nu ai introdus încă rezultate.")

st.divider()

if "confirm_delete" not in st.session_state:
    st.session_state.confirm_delete = False

if st.button("⚠️ Șterge tot istoricul"):
    st.session_state.confirm_delete = True

if st.session_state.confirm_delete:
    st.warning("Ești sigur că vrei să ștergi toate rezultatele?")
    if st.button("Confirm ștergerea"):
        st.session_state.history = []
        save_history([])
        st.session_state.confirm_delete = False
        st.rerun()
