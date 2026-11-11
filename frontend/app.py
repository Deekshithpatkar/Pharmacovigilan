import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Pharmacovigilance Case Processing", layout="wide", page_icon="💊")

st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Go to",
    ["Submit Report", "Case Status Lookup", "Reviewer Dashboard"]
)

# -------------------------------------------------------------
# PAGE 1: SUBMIT REPORT
# -------------------------------------------------------------
if page == "Submit Report":
    st.title("💊 Submit Adverse Drug Event Report")
    st.write("Report suspected side effects or adverse drug reactions for clinical safety evaluation.")

    # TOGGLE: Mode selection
    investigation_mode = st.radio(
        "🧠 Select Processing Engine:",
        ["Standard Production Engine (Fast & Deterministic)", "Autonomous ReAct Agent (Shows Live Thoughts & Tool Calls)"],
        horizontal=True
    )

    with st.form("adverse_event_form"):
        col1, col2 = st.columns(2)
        with col1:
            reporter_type = st.selectbox(
                "Reporter Role",
                ["patient", "nurse", "doctor", "pharmacist", "other"]
            )
            patient_age = st.number_input("Patient Age", min_value=0, max_value=125, value=35)
            patient_sex = st.selectbox("Patient Sex", ["Male", "Female", "Other", "Unknown"])

        with col2:
            suspected_drug = st.text_input("Suspected Drug Name", placeholder="e.g. Amoxicillin, Metformin, Paracetamol")
            outcome = st.selectbox("Current Outcome", ["recovering", "recovered", "not_recovered", "fatal", "unknown"])

        reaction_description = st.text_area(
            "Reaction Description",
            placeholder="Describe what happened, symptoms experienced, onset time, and severity...",
            height=120
        )
        additional_info = st.text_input("Additional Notes (Optional)", placeholder="Other medications taken, allergies, etc.")

        submitted = st.form_submit_button("Submit Adverse Event Report")

    if submitted:
        if not suspected_drug.strip():
            st.error("Please provide the suspected drug name.")
        elif len(reaction_description.strip()) < 5:
            st.error("Please enter a detailed reaction description (at least 5 characters).")
        else:
            payload = {
                "reporter_type": reporter_type,
                "patient_age": int(patient_age),
                "patient_sex": patient_sex,
                "suspected_drug": suspected_drug.strip(),
                "reaction_description": reaction_description.strip(),
                "outcome": outcome,
                "additional_information": additional_info.strip() if additional_info else None
            }

            try:
                if "Autonomous ReAct" in investigation_mode:
                    with st.spinner("🤖 Autonomous ReAct Agent investigating with dynamic tool calls (may take ~30-45s)..."):
                        agent_res = requests.post(f"{API_URL}/cases/agent-investigate", json=payload, timeout=120)
                    if agent_res.status_code == 200:
                        agent_data = agent_res.json()
                        st.success("ReAct Agent Investigation Completed!")
                        
                        st.subheader("Agent Clinical Safety Verdict")
                        st.markdown(agent_data.get("final_verdict", "No summary provided."))

                        st.subheader("Autonomous Chain-of-Thought & Tool Calls")
                        for i, step in enumerate(agent_data.get("agent_steps", []), 1):
                            if step["type"] == "ACTION / TOOL_CALL":
                                st.markdown(f"**Step {i} — Action (Tool Call):** `{step['tool']}`")
                                st.json(step.get("args", {}))
                            else:
                                st.markdown(f"**Step {i} — Tool Observation:**")
                                st.info(step.get("content", ""))
                    else:
                        st.error(f"Agent Error ({agent_res.status_code}): {agent_res.text}")
                else:
                    res = requests.post(f"{API_URL}/cases", json=payload, timeout=10)
                    if res.status_code == 201:
                        data = res.json()
                        st.success(f"Report Submitted Successfully! Case ID: **{data['case_id']}**")
                        
                        st.subheader("Automated Safety Triage Summary")
                        c1, c2, c3 = st.columns(3)
                        c1.metric("Status", data.get("status", "N/A").upper())
                        c2.metric("Triage Priority", data.get("triage_priority", "N/A"))
                        c3.metric("Requires Human Review", "YES" if data.get("requires_human_review") else "NO")

                        st.info(data.get("message"))

                        # Display Extracted AI Info
                        if data.get("extracted_info"):
                            st.markdown("#### Extracted Clinical Info")
                            st.json(data["extracted_info"])

                        # Display Retrieved Evidence
                        if data.get("evidence"):
                            st.markdown("#### Drug Label Evidence Grounding")
                            st.json(data["evidence"])
                    else:
                        st.error(f"Error {res.status_code}: {res.text}")
            except Exception as e:
                st.error(f"Could not connect to FastAPI backend at {API_URL}. Is the server running? Details: {e}")

# -------------------------------------------------------------
# PAGE 2: CASE STATUS LOOKUP
# -------------------------------------------------------------
elif page == "Case Status Lookup":
    st.title("🔍 Case Status & Audit Lookup")
    st.write("Enter a Case ID to inspect case details, extracted entities, and safety triage decisions.")

    case_id_input = st.text_input("Enter Case ID (e.g. PV-XXXXXXX)", placeholder="PV-...")
    if st.button("Search Case"):
        if not case_id_input.strip():
            st.warning("Please enter a valid Case ID.")
        else:
            try:
                res = requests.get(f"{API_URL}/cases/{case_id_input.strip()}", timeout=10)
                if res.status_code == 200:
                    case = res.json()
                    st.success(f"Case Found: **{case['case_id']}**")
                    st.write(f"**Current Status:** `{case['status']}`")

                    if case.get("duplicate_of"):
                        st.warning(f"Linked as potential duplicate of: {case['duplicate_of']}")

                    tabs = st.tabs(["Summary", "Audit History", "Extracted Information", "Drug Label Evidence"])
                    with tabs[0]:
                        c1, c2 = st.columns(2)
                        c1.write(f"**Suspected Drug:** {case.get('extracted_info', {}).get('drugs', ['N/A'])[0] if case.get('extracted_info') else 'N/A'}")
                        c1.write(f"**Reactions:** {', '.join(case.get('extracted_info', {}).get('reactions', [])) if case.get('extracted_info') else 'N/A'}")
                        c2.write(f"**Severity:** {case.get('extracted_info', {}).get('severity', 'N/A')}/5")
                        c2.write(f"**Outcome:** {case.get('extracted_info', {}).get('outcome', 'Unknown')}")

                    with tabs[1]:
                        st.subheader("Immutable Audit Trail")
                        try:
                            audit_res = requests.get(f"{API_URL}/cases/{case['case_id']}/audit", timeout=5)
                            if audit_res.status_code == 200:
                                audit_logs = audit_res.json()
                                if audit_logs:
                                    for log in audit_logs:
                                        st.markdown(f"⏱️ **{log['timestamp'][:19]}** — `[{log['action']}]` by **{log['actor']}**")
                                        st.write(f"Status transition: `{log['previous_status']}` ➔ `{log['new_status']}`")
                                        if log.get("details"):
                                            st.caption(f"Details: {log['details']}")
                                        st.divider()
                                else:
                                    st.info("No audit logs recorded for this case.")
                            else:
                                st.warning("Could not fetch audit history.")
                        except Exception:
                            st.warning("Audit service temporarily unavailable.")

                    with tabs[2]:
                        st.json(case.get("extracted_info") or {})
                    with tabs[3]:
                        st.json(case.get("evidence") or [])
                else:
                    st.error(f"Case not found ({res.status_code}): {res.text}")
            except Exception as e:
                st.error(f"Failed to connect to backend: {e}")

# -------------------------------------------------------------
# PAGE 3: REVIEWER DASHBOARD
# -------------------------------------------------------------
elif page == "Reviewer Dashboard":
    st.title("🩺 Medical Safety Reviewer Dashboard")
    st.write("Cases flagged as **URGENT** or requiring human review due to unexpected safety signals or potential duplicates.")

    try:
        res = requests.get(f"{API_URL}/review/pending", timeout=10)
        if res.status_code == 200:
            pending_cases = res.json()
            st.metric("Total Pending Reviews", len(pending_cases))

            if not pending_cases:
                st.info("✅ No pending reviews at this time. All cases are processed!")
            else:
                for c in pending_cases:
                    with st.expander(f"Case {c['case_id']} - Drug: {c['suspected_drug']} (Reported by: {c['reporter_type']})"):
                        st.write(f"**Reaction Description:** {c['reaction_description']}")
                        st.write(f"**Clinical Severity:** {c.get('severity', 'Unknown')}/5")
                        st.write(f"**Current Status:** `{c['status']}`")
                        if c.get("duplicate_of_id"):
                            st.warning(f"Potential duplicate of: {c['duplicate_of_id']}")

                        # Adjudication form
                        with st.form(f"adjudicate_form_{c['case_id']}"):
                            reviewer_notes = st.text_area(
                                "Safety Officer Clinical Notes",
                                placeholder="Enter clinical assessment, regulatory escalation notes, or merge decision..."
                            )
                            adjudicated_status = st.selectbox(
                                "Set Final Decision",
                                ["completed", "needs_information"],
                                key=f"status_{c['case_id']}"
                            )
                            submit_review = st.form_submit_button("Confirm Clinical Adjudication")

                        if submit_review:
                            if not reviewer_notes.strip():
                                st.error("Please provide reviewer clinical notes before submitting.")
                            else:
                                adj_payload = {
                                    "reviewer_notes": reviewer_notes.strip(),
                                    "adjudicated_status": adjudicated_status
                                }
                                adj_res = requests.post(
                                    f"{API_URL}/review/{c['case_id']}/adjudicate",
                                    json=adj_payload,
                                    timeout=10
                                )
                                if adj_res.status_code == 200:
                                    st.success(f"Case {c['case_id']} successfully adjudicated!")
                                    st.rerun()
                                else:
                                    st.error(f"Error submitting review: {adj_res.text}")
        else:
            st.error(f"Error fetching pending cases: {res.text}")
    except Exception as e:
        st.error(f"Could not connect to FastAPI backend at {API_URL}: {e}")

