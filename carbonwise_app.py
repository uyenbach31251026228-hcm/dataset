"""
CARBONWISE 110 | Vietnam ETS pilot (2025–2026)
Install: pip install streamlit pandas
Run: streamlit run carbonwise_app.py
Use alongside carbonwise_sector_quotas_2025_2026.csv
"""
from pathlib import Path
import pandas as pd
import streamlit as st

st.set_page_config(page_title="CARBONWISE 110", page_icon="🌿", layout="wide")
st.title("🌿 CARBONWISE 110")
st.caption("VietLeap 2026 · Data → Decision · Vietnam's carbon-market readiness")
st.info(
    "The quotas below are legal allowances, NOT measured emissions. "
    "MRV allocations are a what-if policy illustration, NOT official funding "
    "or estimated CO₂ reduction."
)

PATH = Path(__file__).parent / "carbonwise_sector_quotas_2025_2026.csv"
df = pd.read_csv(PATH)
df["year"] = df["year"].astype(int)
df["quota_million_tco2e_rounded"] = pd.to_numeric(df["quota_million_tco2e_rounded"])
df["facilities_count"] = pd.to_numeric(df["facilities_count"])
name_order = ["Nhiệt điện", "Sắt thép", "Xi măng (clinker)"]
q25 = df[df.year == 2025].set_index("sector").loc[name_order]
q26 = df[df.year == 2026].set_index("sector").loc[name_order]

with st.sidebar:
    st.header("Policy parameters")
    budget = st.number_input(
        "Hypothetical MRV-support budget (billion VND)", min_value=0.0,
        max_value=100000.0, value=30.0, step=5.0
    )
    weight = st.slider(
        "Weight on quota exposure (λ)", min_value=0.0, max_value=1.0,
        value=0.50, step=0.05
    )
    st.markdown("λ = 0: equal amount per facility.  λ = 1: proportional to sector quota.")
    year = st.selectbox("Inspect approved quota year", [2026, 2025], index=0)

d = (q26 if year == 2026 else q25).copy()
totalquota = d["quota_million_tco2e_rounded"].sum()
d["facility_share"] = d["facilities_count"] / d["facilities_count"].sum()
d["quota_share"] = d["quota_million_tco2e_rounded"] / totalquota
d["funding_share"] = (1-weight)*d["facility_share"] + weight*d["quota_share"]
d["allocated_billion_vnd"] = budget * d["funding_share"]
d["million_vnd_per_facility"] = d["allocated_billion_vnd"]*1000 / d["facilities_count"]
d["facility_share_pct"] = d["facility_share"] * 100
d["quota_share_pct"] = d["quota_share"] * 100
d["funding_share_pct"] = d["funding_share"] * 100

c1,c2,c3=st.columns(3)
c1.metric("Pilot facilities", f"{int(d.facilities_count.sum()):,}")
c2.metric("Quota (rounded sector sum)", f"{totalquota:,.1f} MtCO₂e")
c3.metric("Illustrative MRV support budget", f"{budget:,.1f} bn VND")
st.subheader("Decision: distribute budget under transparent policy objectives")
st.bar_chart(d["allocated_billion_vnd"],x_label="Sector",y_label="Budget (billion VND)")
shown=d[["facilities_count","quota_million_tco2e_rounded","facility_share_pct",
         "quota_share_pct","funding_share_pct","allocated_billion_vnd",
         "million_vnd_per_facility"]].rename(columns={
    "facilities_count":"Facilities","quota_million_tco2e_rounded":"Quota (MtCO₂e)",
    "facility_share_pct":"Facility share (%)","quota_share_pct":"Quota share (%)",
    "funding_share_pct":"Funding share (%)",
    "allocated_billion_vnd":"Funding (bn VND)",
    "million_vnd_per_facility":"Support per facility (mn VND)"
})
st.dataframe(shown.style.format(precision=2), use_container_width=True)
st.subheader("Three policy rules: comparison")
rows=[]
for x,label in [(0.0,"Equal per facility"),(0.5,"Balanced 50/50"),(1.0,"Proportional to quota")]:
    shares=(1-x)*d["facility_share"]+x*d["quota_share"]
    rows.append({"Rule":label,**{k:round(v*budget,2) for k,v in shares.items()}})
st.dataframe(pd.DataFrame(rows),hide_index=True,use_container_width=True)
st.write(
    f"Interpretation: λ={weight:.2f} gives {weight:.0%} weight to legal "
    "allowance-volume exposure and the rest to the number of regulated facilities. "
    "This is a **normative allocation rule**, not a causal effectiveness estimate."
)
st.warning(
    "Proportional-to-quota support is not automatically more effective. "
    "The model lacks verified facility emissions, actual MRV capability, "
    "marginal abatement costs, and project-level emissions savings. "
    "Do not claim this allocation reduces a quantified number of tonnes."
)
st.markdown("**Verified sources**")
st.markdown(
    "- [Decision 263/QĐ-TTg: exact annual quota totals]"
    "(https://chinhphu.vn/?classid=2&docid=216923&pageid=27160)\n"
    "- [Decision 699/QĐ-BNNMT: facility-level legal allocations]"
    "(https://thuvienphapluat.vn/van-ban/Tai-nguyen-Moi-truong/Quyet-dinh-699-QD-BNNMT-2026-thi-diem-phan-bo-han-ngach-phat-thai-khi-nha-kinh-cho-nam-2025-697010.aspx?tab=3)\n"
    "- [GIZ/IKI: sector aggregate values]"
    "(https://www.climatechange.vn/climate_news/viet-nam-advances-carbon-market-development-with-pilot-ghg-quota-allocation/)\n"
    "- [World Bank: Vietnam pilot ETS factsheet]"
    "(https://carbonpricingdashboard.worldbank.org/compliance-factsheet/ETS_VN)"
)
