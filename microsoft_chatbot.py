import streamlit as st
import re
import pandas as pd
import altair as alt

# ----------------- Financial Data -----------------
financial_data = [
    {"Company": "Microsoft", "Year": 2022, "Total Revenue": 1.98E11, "Net Income": 72738000000, "Total Assets": 3.65E11,
     "Total Liabilities": 1.98E11, "Cash Flow": 89035000000},
    {"Company": "Microsoft", "Year": 2023, "Total Revenue": 2.12E11, "Net Income": 72361000000, "Total Assets": 4.12E11,
     "Total Liabilities": 2.06E11, "Cash Flow": 87582000000},
    {"Company": "Microsoft", "Year": 2024, "Total Revenue": 2.45E11, "Net Income": 88136000000, "Total Assets": 5.12E11,
     "Total Liabilities": 2.44E11, "Cash Flow": 1.19E11},
    {"Company": "Tesla", "Year": 2022, "Total Revenue": 81462000000, "Net Income": 12587000000, "Total Assets": 82338000000,
     "Total Liabilities": 36440000000, "Cash Flow": 14724000000},
    {"Company": "Tesla", "Year": 2023, "Total Revenue": 96773000000, "Net Income": 14973000000, "Total Assets": 1.07E11,
     "Total Liabilities": 43009000000, "Cash Flow": 13256000000},
    {"Company": "Tesla", "Year": 2024, "Total Revenue": 97690000000, "Net Income": 7153000000, "Total Assets": 1.22E11,
     "Total Liabilities": 48390000000, "Cash Flow": 14923000000},
    {"Company": "Apple", "Year": 2022, "Total Revenue": 3.94E11, "Net Income": 99803000000, "Total Assets": 3.53E11,
     "Total Liabilities": 3.02E11, "Cash Flow": 1.22E11},
    {"Company": "Apple", "Year": 2023, "Total Revenue": 3.83E11, "Net Income": 96995000000, "Total Assets": 3.53E11,
     "Total Liabilities": 2.90E11, "Cash Flow": 1.11E11},
    {"Company": "Apple", "Year": 2024, "Total Revenue": 3.91E11, "Net Income": 93736000000, "Total Assets": 3.65E11,
     "Total Liabilities": 3.08E11, "Cash Flow": 1.18E11},
]

valid_companies = ["Microsoft", "Tesla", "Apple"]

# ----------------- Helper Functions -----------------
def extract_companies(query):
    companies = []
    for comp in valid_companies:
        if comp.lower() in query.lower():
            companies.append(comp)
    return list(set(companies))

def extract_years(query):
    years = re.findall(r'\b(20\d{2})\b', query)
    return [int(y) for y in years] if years else []

# ----------------- Chatbot Logic -----------------
def financial_chatbot(query):
    query_lower = query.lower()
    companies = extract_companies(query)
    years = extract_years(query)

    # Detect invalid companies (mentioned but not in dataset)
    mentioned_words = re.findall(r"[A-Za-z]+", query)  # extract words
    invalid_companies = [w for w in mentioned_words if w.capitalize() not in valid_companies and w.lower() not in ["revenue", "income", "assets", "liabilities", "cash", "flow", "compare", "with", "in", "of", "and"]]

    if invalid_companies:
        return f"⚠️ You mentioned an unknown company: **{', '.join(set(invalid_companies))}**. Please compare only Microsoft, Tesla, or Apple."

    if not companies:
        return "⚠️ Please specify at least one company (Microsoft, Tesla, or Apple)."

    if "revenue" in query_lower:
        metric = "Total Revenue"
    elif "net income" in query_lower:
        metric = "Net Income"
    elif "total assets" in query_lower or "assets" in query_lower:
        metric = "Total Assets"
    elif "total liabilities" in query_lower or "liabilities" in query_lower:
        metric = "Total Liabilities"
    elif "cash flow" in query_lower or "cash" in query_lower:
        metric = "Cash Flow"
    else:
        return "⚠️ Sorry, I can only provide info on revenue, net income, assets, liabilities, or cash flow."

    # comparison (multiple companies)
    if len(companies) >= 2:
        data_companies = {
            comp: [item for item in financial_data if item["Company"] == comp and (not years or item["Year"] in years)]
            for comp in companies
        }
        if not any(data_companies.values()):
            return "No data found."
        all_years = sorted(set([d["Year"] for data in data_companies.values() for d in data]))
        df = pd.DataFrame({"Year": all_years})
        for comp in companies:
            df[comp] = [next((d[metric] for d in data_companies[comp] if d["Year"] == y), None) for y in all_years]
        return df

    # single company
    else:
        comp = companies[0]
        data = [item for item in financial_data if item["Company"] == comp and (not years or item["Year"] in years)]
        if not data:
            return "No data found."
        df = pd.DataFrame({
            "Year": [d["Year"] for d in data],
            f"{metric} ({comp})": [d[metric] for d in data]
        })
        return df

# ----------------- Streamlit App -----------------
st.set_page_config(page_title="Financial Data Chatbot", page_icon="💬", layout="wide")

st.title("💬 Financial Data Chatbot")

st.markdown("Ask about **Revenue, Net Income, Assets, Liabilities, or Cash Flow** for **Microsoft, Tesla, and Apple**.")

if "history" not in st.session_state:
    st.session_state.history = []

for q, r in st.session_state.history:
    st.markdown(f"**🧑 You:** {q}")
    if isinstance(r, pd.DataFrame):
        st.dataframe(r, use_container_width=True)

        if len(r.columns) > 2:  # comparison chart
            df_melt = r.melt("Year", var_name="Company", value_name="Value")
            chart = alt.Chart(df_melt).mark_line(point=True).encode(
                x="Year:O", y="Value:Q", color="Company:N"
            )
            st.altair_chart(chart, use_container_width=True)
        else:  # single company
            col_name = r.columns[1]
            chart = alt.Chart(r).mark_bar().encode(
                x="Year:O", y=col_name, color=alt.value("teal")
            )
            st.altair_chart(chart, use_container_width=True)
    else:
        st.warning(r)

query = st.chat_input("💡 Ask your question here...")

if query:
    response = financial_chatbot(query)
    st.session_state.history.append((query, response))
    st.rerun()
