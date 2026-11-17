import pandas as pd
import streamlit as st

st.set_page_config(page_title="Financial Calculator", page_icon="💰", layout="wide")

st.title("💰 Financial Calculator")

# ---------- Sidebar ----------
st.sidebar.header("Settings")
cur = st.sidebar.text_input("Currency label", value="PKR")
tool = st.sidebar.radio(
    "Choose a calculator",
    ["Loan / EMI", "Investment Growth (SIP)", "Savings Goal", "CAGR / ROI"],
)


def money(x: float) -> str:
    return f"{cur} {x:,.0f}"


# ---------- 1. Loan / EMI ----------
def loan_calculator():
    st.subheader("Loan / EMI Calculator")
    c1, c2, c3 = st.columns(3)
    principal = c1.number_input("Loan amount", min_value=0.0, value=1_000_000.0, step=10_000.0)
    rate = c2.number_input("Annual interest rate (%)", min_value=0.0, value=12.0, step=0.1)
    years = c3.number_input("Tenure (years)", min_value=1, value=5, step=1)

    n = int(years * 12)
    i = rate / 1200
    emi = principal / n if i == 0 else principal * i * (1 + i) ** n / ((1 + i) ** n - 1)
    total = emi * n
    interest = total - principal

    m1, m2, m3 = st.columns(3)
    m1.metric("Monthly EMI", money(emi))
    m2.metric("Total payment", money(total))
    m3.metric("Total interest", money(interest))

    rows, balance = [], principal
    for month in range(1, n + 1):
        int_part = balance * i
        prin_part = emi - int_part
        balance = max(balance - prin_part, 0)
        rows.append({"Month": month, "EMI": emi, "Principal": prin_part,
                     "Interest": int_part, "Balance": balance})
    df = pd.DataFrame(rows)

    st.write("**Remaining balance over time**")
    st.line_chart(df.set_index("Month")["Balance"])
    with st.expander("Full amortization schedule"):
        st.dataframe(df.round(2), use_container_width=True)
        st.download_button("Download CSV", df.to_csv(index=False), "amortization.csv")


# ---------- 2. Investment growth ----------
def investment_calculator():
    st.subheader("Investment Growth (lump sum + monthly SIP)")
    c1, c2, c3, c4 = st.columns(4)
    start = c1.number_input("Initial amount", min_value=0.0, value=100_000.0, step=10_000.0)
    monthly = c2.number_input("Monthly contribution", min_value=0.0, value=10_000.0, step=1_000.0)
    rate = c3.number_input("Expected annual return (%)", min_value=0.0, value=10.0, step=0.1)
    years = c4.number_input("Years", min_value=1, value=10, step=1)

    i = rate / 1200
    balance, invested = start, start
    rows = [{"Year": 0, "Invested": invested, "Value": balance}]
    for month in range(1, int(years) * 12 + 1):
        balance = balance * (1 + i) + monthly
        invested += monthly
        if month % 12 == 0:
            rows.append({"Year": month // 12, "Invested": invested, "Value": balance})
    df = pd.DataFrame(rows)

    m1, m2, m3 = st.columns(3)
    m1.metric("Total invested", money(invested))
    m2.metric("Final value", money(balance))
    m3.metric("Gains", money(balance - invested))

    st.area_chart(df.set_index("Year")[["Invested", "Value"]])
    with st.expander("Year-by-year table"):
        st.dataframe(df.round(2), use_container_width=True)


# ---------- 3. Savings goal ----------
def goal_calculator():
    st.subheader("Savings Goal: how much to save monthly?")
    c1, c2, c3, c4 = st.columns(4)
    target = c1.number_input("Target amount", min_value=0.0, value=5_000_000.0, step=100_000.0)
    current = c2.number_input("Current savings", min_value=0.0, value=200_000.0, step=10_000.0)
    rate = c3.number_input("Expected annual return (%)", min_value=0.0, value=8.0, step=0.1)
    years = c4.number_input("Years to goal", min_value=1, value=10, step=1)

    n = int(years) * 12
    i = rate / 1200
    fv_current = current * (1 + i) ** n
    needed = max(target - fv_current, 0)
    pmt = needed / n if i == 0 else needed * i / ((1 + i) ** n - 1)

    m1, m2 = st.columns(2)
    m1.metric("Required monthly saving", money(pmt))
    m2.metric("Current savings will grow to", money(fv_current))
    if needed == 0:
        st.success("Your current savings alone are projected to reach the goal.")


# ---------- 4. CAGR / ROI ----------
def cagr_calculator():
    st.subheader("CAGR / ROI Calculator")
    c1, c2, c3 = st.columns(3)
    begin = c1.number_input("Beginning value", min_value=0.01, value=100_000.0, step=10_000.0)
    end = c2.number_input("Ending value", min_value=0.0, value=250_000.0, step=10_000.0)
    years = c3.number_input("Years", min_value=0.1, value=5.0, step=0.5)

    roi = (end - begin) / begin * 100
    cagr = ((end / begin) ** (1 / years) - 1) * 100

    m1, m2, m3 = st.columns(3)
    m1.metric("Absolute gain", money(end - begin))
    m2.metric("Total ROI", f"{roi:,.2f}%")
    m3.metric("CAGR", f"{cagr:,.2f}% / yr")


# ---------- Router ----------
{
    "Loan / EMI": loan_calculator,
    "Investment Growth (SIP)": investment_calculator,
    "Savings Goal": goal_calculator,
    "CAGR / ROI": cagr_calculator,
}[tool]()

st.caption("For educational estimates only. Not financial advice.")
