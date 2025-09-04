import pandas as pd
import streamlit as st

st.title("Boardgame Priority Comparator")


st.markdown("""
This is a simple app to compare your Spiel priorities with your friends.  

**Usage:**
1. Prioritize all the games you care about in the Boardgamegeek Spiel Preview.
2. Clear all Filters.
3. Export as CSV.
4. Gather all CSV files.
5. Upload them to the app.
""")

uploaded_files = st.file_uploader("Select all csv files to process", type="csv", accept_multiple_files=True)

if uploaded_files:
    dfs = []
    for i, f in enumerate(uploaded_files):
        df = pd.read_csv(f, sep=",", quotechar='"')
        df["Priority"] = pd.to_numeric(df["Priority"], errors="coerce").fillna(5).astype(int)
        if "Show Price" not in df.columns and "MSRP" in df.columns:
            df["Show Price"] = df["MSRP"]
        elif "Show Price" in df.columns:
            df["Show Price"] = df["Show Price"].fillna(df["MSRP"]) if "MSRP" in df.columns else df["Show Price"]
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
