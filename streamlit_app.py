import pandas as pd
import streamlit as st

st.title("Boardgame Priority Comparator")

uploaded_files = st.file_uploader("Select all csv files to process", type="csv", accept_multiple_files=True)

if uploaded_files:
    dfs = []
    for i, f in enumerate(uploaded_files):
        df = pd.read_csv(f, sep=",", quotechar='"')
        df["Priority"] = pd.to_numeric(df["Priority"], errors="coerce").fillna(5).astype(int)
        df = df[["Title", "Publisher", "Location", "Show Price", "Notes", "Priority"]].copy()
        df.rename(columns={"Priority": f"Priority_{i+1}"}, inplace=True)
        dfs.append(df)

    merged = dfs[0]
    for df in dfs[1:]:
        merged = pd.merge(merged, df, on=["Title","Publisher","Location","Show Price","Notes"], how="outer")

    priority_cols = [c for c in merged.columns if c.startswith("Priority_")]
    merged["MeanPriority"] = merged[priority_cols].mean(axis=1)
    merged = merged.sort_values("MeanPriority")

    st.dataframe(merged)

    csv = merged.to_csv(index=False, quoting=1).encode("utf-8")
    st.download_button("Download results", csv, "priorities.csv", "text/csv")
