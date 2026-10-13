"""
AEGIS Multi-Jurisdiction Climate Regulatory Corpus
Authoritative statutory clauses, disclosure mandates, and physical resilience standards across:
- India (SEBI BRSR Core, MoF Carbon Surcharge, NDMA Urban Flood SOP, RBI Climate Guidelines, NAPCC)
- Türkiye (SPK Sustainability Principles Compliance Framework, AFAD Disaster Law No. 7269)
- USA / California (California SB 253 Climate Accountability Act, California SB 261 Financial Risk Act)
- European Union / Estonia (EU CSDDD 2024/1760 Corporate Due Diligence, EU Taxonomy 2020/852 Climate Adaptation)
"""
from typing import List, Dict, Any

GLOBAL_REGULATORY_CORPUS: List[Dict[str, Any]] = [
    # -------------------------------------------------------------------------
    # 1. INDIA (SEBI, RBI, NDMA, MoF)
    # -------------------------------------------------------------------------
    {
        "id": "sebi-brsr-principle6",
        "title": "SEBI BRSR Core Mandate — Principle 6 (Climate & Environmental Disclosure)",
        "sector": "Enterprise & Financial",
        "region": "India",
        "country_iso": "IN",
        "text": (
            "Under SEBI Business Responsibility and Sustainability Reporting (BRSR) Core, the top 1000 listed "
            "entities in India must quantify capital expenditure allocated to acute physical weather adaptation "
            "and chronic infrastructure degradation. Facilities in flood-prone corridors face mandatory tier-2 "
            "third-party ESG audits. Failure to disclose acute flood vulnerabilities exceeding ₹50 Crores results in "
            "regulatory penalty surcharges and credit rating downgrade warnings."
        )
    },
    {
        "id": "mof-carbon-tax-2026",
        "title": "Ministry of Finance — Heavy Carbon Transition & Environmental Risk Surcharge 2026",
        "sector": "Industrial & Energy",
        "region": "India",
        "country_iso": "IN",
        "text": (
            "Industrial logistics hubs, thermal plants, and chemical manufacturing zones face progressive carbon "
            "surcharges of ₹2,500 to ₹6,500 per tonne of emissions. Facilities where stormwater drainage failures "
            "cause hazardous effluent runoff into municipal waterways are subject to statutory environmental "
            "remediation penalties and immediate suspension of operating licenses under the Water Act."
        )
    },
    {
        "id": "ndma-urban-flood-sop-sec14",
        "title": "NDMA Standard Operating Procedure — Urban Flood Management & Critical Lifeline Protections",
        "sector": "Civic & Infrastructure",
        "region": "India",
        "country_iso": "IN",
        "text": (
            "Section 14 mandates that electrical substations, hospital auxiliary power systems, water treatment plants, "
            "and metro rail corridors must maintain a minimum 1.5-meter freeboard clearance above the 100-year flood line. "
            "Assets lacking certified flood barriers cannot claim civic municipal insurance indemnification in the event of "
            "monsoon inundation damage."
        )
    },
    {
        "id": "rbi-climate-risk-guidelines",
        "title": "Reserve Bank of India — Regulatory Framework on Climate Risk & Sustainable Finance",
        "sector": "Banking & Lending",
        "region": "India",
        "country_iso": "IN",
        "text": (
            "Commercial banks and NBFCs must stress-test collateral assets against physical flood risks. Properties "
            "located in chronic inundation zones with 10-year degradation probabilities exceeding 40% are subjected to "
            "mandatory loan-to-value (LTV) haircuts of 15% to 25%, categorizing exposed commercial infrastructure as "
            "high-risk transition assets."
        )
    },
    {
        "id": "napcc-urban-mission",
        "title": "National Action Plan on Climate Change (NAPCC) — National Mission on Sustainable Habitat",
        "sector": "Urban Planning",
        "region": "India",
        "country_iso": "IN",
        "text": (
            "Promotes climate-resilient infrastructure design across 500 AMRUT and Smart Cities in Bharat. Recommends "
            "nature-based stormwater retention vaults, permeable pavements, and mandatory GIS mapping of flood inundation "
            "zones with real-time sensor integration."
        )
    },

    # -------------------------------------------------------------------------
    # 2. TÜRKIYE (SPK, AFAD, Environment Ministry) - Host Nation
    # -------------------------------------------------------------------------
    {
        "id": "spk-sustainability-principles-tr",
        "title": "SPK Sustainability Principles Compliance Framework (Sürdürülebilirlik İlkeleri Uyum Çerçevesi)",
        "sector": "Enterprise & Financial",
        "region": "Turkey",
        "country_iso": "TR",
        "text": (
            "The Capital Markets Board of Türkiye (Sermaye Piyasası Kurulu - SPK) mandates that publicly traded "
            "companies on Borsa Istanbul (BIST) declare acute physical climate vulnerabilities and flood exposure "
            "in annual corporate governance reports. Entities with industrial facilities in high-risk basins such as "
            "the Marmara Sea coastal perimeter and Black Sea valleys must perform independent physical stress tests "
            "and quantify enterprise adaptation budgets in accordance with TCFD and ISSB standards."
        )
    },
    {
        "id": "tr-climate-disaster-law-7269",
        "title": "Türkiye Disaster and Emergency Management Framework (Law No. 7269 & AFAD Flood Directives)",
        "sector": "Civic & Infrastructure",
        "region": "Turkey",
        "country_iso": "TR",
        "text": (
            "Under Law No. 7269 on Measures and Assistance Regarding Natural Disasters, municipal authorities and industrial "
            "operators in high-hazard zones (including Kastamonu Bozkurt Ezine Stream basin and Istanbul Golden Horn corridors) "
            "are prohibited from constructing critical substations or logistics nodes within statutory 100-year riparian floodways. "
            "Breach of stream buffer zones triggers immediate demolition orders and civil liability for downstream asset damage."
        )
    },

    # -------------------------------------------------------------------------
    # 3. UNITED STATES / CALIFORNIA (SB 253, SB 261) - Judge Jurisdiction
    # -------------------------------------------------------------------------
    {
        "id": "california-sb253-climate-act",
        "title": "California Climate Corporate Data Accountability Act (SB 253 / CARB Mandate)",
        "sector": "Enterprise & Financial",
        "region": "USA",
        "country_iso": "US",
        "text": (
            "California Senate Bill 253 requires US public and private commercial partnerships doing business in California "
            "with annual revenues exceeding $1 billion to publicly disclose full Scope 1, 2, and supply-chain Scope 3 emissions. "
            "Furthermore, enterprises with critical logistics centers or physical supply assets located in vulnerable flood zones "
            "(such as Orange County Newport coastal basin and LA floodplain) must submit audited physical resilience plans "
            "certified by independent accredited assurance providers."
        )
    },
    {
        "id": "california-sb261-financial-risk",
        "title": "California Climate-Related Financial Risk Act (SB 261 / TCFD Alignment)",
        "sector": "Banking & Lending",
        "region": "USA",
        "country_iso": "US",
        "text": (
            "Senate Bill 261 mandates biennial reporting on climate-related financial risk for corporations with revenues "
            "exceeding $500 million operating within California. Reports must disclose material physical risks from atmospheric "
            "river storms, sea-level rise inundation in Southern California coastal zones, and business interruption liabilities. "
            "Non-compliance incurs administrative penalties up to $50,000 per reporting cycle assessed by the Air Resources Board."
        )
    },

    # -------------------------------------------------------------------------
    # 4. EUROPEAN UNION / ESTONIA (CSDDD, EU Taxonomy) - Judge Jurisdiction
    # -------------------------------------------------------------------------
    {
        "id": "eu-csddd-corporate-due-diligence",
        "title": "EU Corporate Sustainability Due Diligence Directive (CSDDD Directive 2024/1760)",
        "sector": "Enterprise & Financial",
        "region": "Estonia",
        "country_iso": "EE",
        "text": (
            "The European Union Corporate Sustainability Due Diligence Directive (CSDDD) requires large EU undertakings and "
            "Baltic market operators to adopt and execute a transition plan for climate change mitigation aligned with the 1.5°C "
            "Paris Agreement objective. Undertakings must identify and remediate acute physical climate threats—specifically "
            "Baltic coastal storm surges and river delta flash inundations in hubs like Pärnu and Tallinn—with strict corporate "
            "civil liability for foreseeable infrastructure failures."
        )
    },
    {
        "id": "eu-taxonomy-climate-adaptation",
        "title": "EU Taxonomy Regulation (Regulation 2020/852) — Climate Change Adaptation Criteria",
        "sector": "Civic & Infrastructure",
        "region": "European Union",
        "country_iso": "EU",
        "text": (
            "The EU Taxonomy Climate Delegated Act sets technical screening criteria determining whether economic activities "
            "qualify as substantially contributing to climate change adaptation. Infrastructure investments must demonstrate "
            "state-of-the-art physical climate risk assessments (CRAs) spanning 10-to-30 year IPCC SSP trajectories, requiring "
            "dedicated flood barriers, stormwater attenuation basins, and resilient electrical backup systems."
        )
    }
]
