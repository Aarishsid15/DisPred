import streamlit as st
import requests
import json
import joblib
import os

API_URL = "http://localhost:8000"
# API_URL = "http://127.0.0.1:8000"


# backend_url = os.getenv("BACKEND_URL")

# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "token" not in st.session_state:
    st.session_state["token"] = None
if "username" not in st.session_state:
    st.session_state["username"] = None
if "name" not in st.session_state:
    st.session_state["name"] = None
if "show_history" not in st.session_state:
    st.session_state["show_history"] = False
if "last_result" not in st.session_state:
    st.session_state["last_result"] = None
if "last_symptoms" not in st.session_state:
    st.session_state["last_symptoms"] = []
if "prediction_saved" not in st.session_state:
    st.session_state["prediction_saved"] = False


def home():
    with st.container(border=True):
        l, m, r = st.columns([1, 1, 1])
        with m:
            st.title('DisPred🩺')

        le, me, re = st.columns([1, 5, 1])
        with me:
            st.subheader('Predict your disease by entering your symptoms.')

        lef, med, rig = st.columns([1, 4, 1])
        with med:
            name = st.text_input("Enter your Name: ")
        if name:
            st.session_state["name"] = name
            left, medium, right = st.columns([1, 1, 1])
            with medium:
                st.write(f"{name} Welcome to DisPred😊")


def register_and_login():
    ls, ms, rs = st.columns([1, 4, 1])
    with ms:
        lside, rside = st.columns(2)

        # ── Register ──────────────────────────
        if st.session_state["name"]:
            with lside:
                register = st.toggle("Register")
                if register:
                    with st.container(border=True):
                        st.subheader("📝 Register")

                        reg_username = st.text_input("Username", key="reg_username", placeholder="Enter username")
                        reg_email    = st.text_input("Email", key="reg_email", placeholder="Enter email")
                        reg_password = st.text_input("Password", key="reg_password", type="password", placeholder="Enter password")
                        reg_confirm  = st.text_input("Confirm Password", key="reg_confirm", type="password", placeholder="Confirm password")

                        if st.button("Register", key="btn_register"):
                            if not reg_username or not reg_email or not reg_password:
                                st.error("Please fill all fields!")
                            elif reg_password != reg_confirm:
                                st.error("Passwords do not match!")
                            elif len(reg_password) < 6:
                                st.error("Password must be at least 6 characters!")
                            else:
                                try:
                                    # Step 1 — Register
                                    reg_response = requests.post(
                                        f"{API_URL}/register",
                                        json={
                                            "username": reg_username,
                                            "email"   : reg_email,
                                            "password": reg_password
                                        }
                                    )
                                    if reg_response.status_code == 200:
                                        # Step 2 — Auto login after register to get token
                                        login_response = requests.post(
                                            f"{API_URL}/login",
                                            data={
                                                "username": reg_username,
                                                "password": reg_password
                                            }
                                        )
                                        if login_response.status_code == 200:
                                            token = login_response.json()["access_token"]
                                            st.session_state["token"]     = token
                                            st.session_state["logged_in"] = True
                                            st.session_state["username"]  = reg_username
                                            st.rerun()
                                        else:
                                            st.success("✅ Registered! Please login now.")

                                    elif reg_response.status_code == 400:
                                        error_msg = reg_response.json().get("detail", "Registration failed")
                                        st.error(f"❌ {error_msg}")
                                    else:
                                        st.error("❌ Something went wrong. Try again!")
                                except requests.exceptions.ConnectionError:
                                    st.error("❌ Cannot connect to server!")

            # ── Login ─────────────────────────────
            with rside:
                login = st.toggle("Login")
                if login:
                    with st.container(border=True):
                        st.subheader("🔐 Login")

                        login_username = st.text_input("Username", key="login_username", placeholder="Enter username")
                        login_password = st.text_input("Password", key="login_password", type="password",
                                                    placeholder="Enter password")

                        if st.button("Login", key="btn_login"):
                            if not login_username or not login_password:
                                st.error("Please fill all fields!")
                            else:
                                try:
                                    response = requests.post(
                                        f"{API_URL}/login",
                                        data={
                                            "username": login_username,
                                            "password": login_password
                                        }
                                    )
                                    if response.status_code == 200:
                                        token = response.json()["access_token"]
                                        st.session_state["token"] = token
                                        st.session_state["logged_in"] = True
                                        st.session_state["username"] = login_username
                                        st.rerun()

                                    elif response.status_code == 401:
                                        st.error("❌ Incorrect username or password!")
                                    else:
                                        st.error("❌ Something went wrong. Try again!")
                                except requests.exceptions.ConnectionError:
                                    st.error("❌ Cannot connect to server!")


def home_page():
    st.title(f"✅ Welcome back {st.session_state['name']}!")
    st.markdown("---")
    col1, col2, col3 = st.columns([1,1,4])
    with col1:
        if st.button("Logout"):
            st.session_state.clear()
            st.rerun()
    with col2:
        if st.button("Saved"):
            st.session_state["show_history"] = True
            st.rerun()

    # st.markdown("---")

    with st.container(border=True):
        st.subheader("Select Your Symptoms")

        all_symptoms = joblib.load("dp_backend/symptom_columns.pkl")

        input_method = st.radio(
            "How would you like to enter symptoms?",
            ["Search and Select", "Type Manually"],
            horizontal=True
        )

        selected_symptoms = []

        if input_method == "Search and Select":
            selected_symptoms = st.multiselect(
                "Search and select your symptoms:",
                options=all_symptoms,
                placeholder="Type to search symptoms..."
            )
        else:
            typed = st.text_area(
                "Type your symptoms (comma separated):",
                placeholder="e.g. fever, cough, fatigue, headache"
            )
            if typed:
                selected_symptoms = [s.strip().lower() for s in typed.split(",") if s.strip()]
                st.info(f"Symptoms entered: {selected_symptoms}")

        if selected_symptoms:
            st.markdown("**Selected symptoms:**")
            tag_html = " ".join([
                f'<span style="background-color:#1f77b4; color:white; padding:4px 10px; border-radius:15px; margin:3px; display:inline-block">{s}</span>'
                for s in selected_symptoms
            ])
            st.markdown(tag_html, unsafe_allow_html=True)
            st.markdown(f"**Total selected: {len(selected_symptoms)}**")

        st.markdown("---")

        # ✅ Predict button — only saves result to session state
        if st.button(" Predict Disease", type="primary"):
            if not selected_symptoms:
                st.warning("⚠️ Please select at least one symptom!")
            else:
                with st.spinner("Analyzing symptoms..."):
                    try:
                        response = requests.post(
                            f"{API_URL}/predict",
                            json={"symptoms": selected_symptoms},
                            headers={"Authorization": f"Bearer {st.session_state['token']}"}
                        )
                        if response.status_code == 200:
                            st.session_state["last_result"]      = response.json()
                            st.session_state["last_symptoms"]    = selected_symptoms
                            st.session_state["prediction_saved"] = False

                        elif response.status_code == 401:
                            st.error("❌ Session expired. Please login again!")
                            st.session_state.clear()
                            st.rerun()
                        else:
                            st.error("❌ Prediction failed. Try again!")

                    except requests.exceptions.ConnectionError:
                        st.error("❌ Cannot connect to server!")

    # ✅ Results shown OUTSIDE container — persists across reruns
    if st.session_state.get("last_result"):
        result   = st.session_state["last_result"]
        symptoms = st.session_state["last_symptoms"]

        st.markdown("---")
        st.subheader("🏥 Prediction Results")

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Predicted Disease", result["top_prediction"].title())
            st.markdown("---")
        with col2:
            st.metric("Confidence", f"{result['confidence']}%")
            st.markdown("---")

        st.markdown("**Top 3 Predictions:**")
        for i, pred in enumerate(result["top_3_predictions"], 1):
            st.write(f"{i}. {pred['disease'].title()} — {pred['confidence']}%")

        st.markdown("---")
        st.subheader("💊 Recommended Medicines")
        for med in result["medicines"]:
            st.write(f"• {med}")

        st.markdown("---")
        st.subheader("📋 Prescription")
        col_do, col_dont = st.columns(2)
        with col_do:
            st.markdown("**✅ Do's**")
            for do in result["prescription"]["do"]:
                st.write(f"🟢 {do}")
        with col_dont:
            st.markdown("**❌ Don'ts**")
            for dont in result["prescription"]["dont"]:
                st.write(f"🔴 {dont}")

        st.markdown("---")

        # ✅ Save button OUTSIDE predict block — always visible
        if not st.session_state.get("prediction_saved", False):
            if st.button("💾 Save Prediction", key="save_btn"):
                try:
                    save_response = requests.post(
                        f"{API_URL}/save-prediction",
                        json={
                            "symptoms"         : symptoms,
                            "predicted_disease": result["top_prediction"],
                            "confidence"       : result["confidence"],
                            "medicines"        : result["medicines"],
                            "prescription_do"  : result["prescription"]["do"],
                            "prescription_dont": result["prescription"]["dont"]
                        },
                        headers={"Authorization": f"Bearer {st.session_state['token']}"}
                    )
                    if save_response.status_code == 200:
                        st.session_state["prediction_saved"] = True
                        st.success("✅ Prediction saved successfully!")
                        st.rerun()
                    elif save_response.status_code == 401:
                        st.error("❌ Session expired. Please login again!")
                        st.session_state.clear()
                        st.rerun()
                    else:
                        st.error(f"❌ Failed! {save_response.json()}")
                except requests.exceptions.ConnectionError:
                    st.error("❌ Cannot connect to server!")
        else:
            st.success("✅ Prediction already saved!")
            if st.button("🔄 New Prediction", key="new_pred_btn"):
                st.session_state["last_result"]      = None
                st.session_state["last_symptoms"]    = []
                st.session_state["prediction_saved"] = False
                st.rerun()


def history_page():
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("Prediction"):
            st.session_state["show_history"] = False
            st.rerun()

    st.title("📋 Saved Predictions")
    st.markdown("---")

    try:
        response = requests.get(
            f"{API_URL}/history",
            headers={"Authorization": f"Bearer {st.session_state['token']}"}
        )

        if response.status_code == 200:
            history = response.json()

            if not history:
                st.info("📭 No saved predictions yet. Go predict a disease first!")
                return

            st.markdown(f"**Total saved predictions: {len(history)}**")
            st.markdown("---")

            for i, record in enumerate(history, 1):
                with st.container(border=True):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.subheader(f"🏥 {record['predicted_disease'].title()}")
                    with col2:
                        st.metric("Confidence", f"{record['confidence']}%")

                    st.caption(f"🕐 Saved on: {record['created_at'][:19].replace('T', ' ')}")
                    st.markdown("---")

                    st.markdown("**🤒 Symptoms:**")
                    symptoms_list = record["symptoms"].split(", ")
                    tag_html = " ".join([
                        f'<span style="background-color:#1f77b4; color:white; padding:3px 8px; border-radius:12px; margin:2px; display:inline-block; font-size:13px">{s}</span>'
                        for s in symptoms_list
                    ])
                    st.markdown(tag_html, unsafe_allow_html=True)
                    st.markdown("---")

                    col_med, col_pres = st.columns(2)

                    with col_med:
                        st.markdown("**💊 Medicines:**")
                        try:
                            medicines = json.loads(record.get("medicines", "[]"))
                            for med in medicines:
                                st.write(f"• {med}")
                        except:
                            st.write("No medicines available")

                    with col_pres:
                        st.markdown("**📋 Prescription:**")
                        try:
                            dos   = json.loads(record.get("prescription_do","[]"))
                            donts = json.loads(record.get("prescription_dont", "[]"))
                            if dos:
                                st.markdown("**✅ Do's:**")
                                for do in dos:
                                    st.write(f"🟢 {do}")
                            if donts:
                                st.markdown("**❌ Don'ts:**")
                                for dont in donts:
                                    st.write(f"🔴 {dont}")
                        except:
                            st.write("Prescription data unavailable")

                st.markdown("")

        elif response.status_code == 401:
            st.error(" Session expired. Please login again!")
            st.session_state.clear()
            st.rerun()
        else:
            st.error(" Failed to fetch history!")

    except requests.exceptions.ConnectionError:
        st.error("⚠️ Cannot connect to server!")


# ── Main app flow ──────────────────────────────────
if st.session_state["logged_in"]:
    if st.session_state["show_history"]:
        history_page()
    else:
        home_page()
else:
    home()
    register_and_login()