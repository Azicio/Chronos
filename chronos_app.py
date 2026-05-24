import streamlit as st
import datetime
import requests
import json
import base64  # Fixed: Resolves Budi login camera conversion crash
import pandas as pd  # Fixed: Resolves Azicio matrix_mock definition error

# Abstracted Pipeline Link via Streamlit Secrets Manager
# Bypasses public GitHub visibility completely
WEBHOOK_URL = st.secrets["github"] ["webhook_url"]

# 1. Coordinate Timezone Realignment (WIT - GMT+9)
WIT = datetime.timezone(datetime.timedelta(hours=9))

def get_now_wit():
    return datetime.datetime.now(datetime.timezone.utc).astimezone(WIT)

# 2. Extract Corporate CSS UI Shading Layer
st.set_page_config(page_title="Project Chronos Core Console", layout="centered")
st.markdown("""
    <style>
        .stApp { background-color: #0F172A; color: #F8FAFC; }
        .stButton>button {
            background-color: #0284C7; color: white;
            border: 2px solid #38BDF8; border-radius: 8px;
            font-weight: bold; width: 100%; height: 3rem;
        }
        .error-box {
            background-color: #7F1D1D; border-left: 5px solid #F87171;
            padding: 15px; border-radius: 4px; margin-bottom: 15px;
        }
    </style>
""", unsafe_allow_html=True)

# 3. Dynamic Session State Verification
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_role" not in st.session_state:
    st.session_state.user_role = "Tier_1"
if "operator_name" not in st.session_state:
    st.session_state.operator_name = ""

# --- LOGIN SCREEN INTERFACE ---
if not st.session_state.authenticated:
    st.title("🔒 CHRONOS SECURITY GATEWAY")
    st.caption("Systemic Attendance & Logging Engine — Teluk Ambon Registry")
    
    phone_input = st.text_input("📞 Enter Phone Number", placeholder="e.g., 0812XXXXXXXX")
    pin_input = st.text_input("🔑 Enter 4-Digit Security PIN", type="password", max_chars=4)
    
    # --- UPGRADED DYNAMIC LOGIN CHECK LOOP ---
if st.button("Verify Credentials"):
    try:
        # Load user fuel ledger matrix dynamically
        with open("data/users.json", "r") as f:
            user_db = json.load(f)
            
        if phone_input.strip() in user_db:
            target_user = user_db[phone_input.strip()]
            if pin_input == target_user["pin"]:
                st.session_state.authenticated = True
                st.session_state.user_role = target_user["role"]
                st.session_state.operator_name = target_user["name"]
                st.rerun()
            else:
                st.markdown('<div class="error-box">❌ Access Denied: Incorrect Security PIN code.</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="error-box">⚠️ Authentication Anomaly: Phone Number not registered in system database.</div>', unsafe_allow_html=True)
            
    except Exception as db_err:
        st.error(f"Failed to access database registry file: {str(db_err)}")

# --- POST-AUTHENTICATION ACTIVE COCKPIT ---
else:
    current_time = get_now_wit()
    
    # Header Panel Layout
    st.subheader(f"👋 Welcome, {st.session_state.operator_name}")
    st.caption(f"Clearance Level: {st.session_state.user_role} | Time: {current_time.strftime('%Y-%m-%d %H:%M:%S')} WIT")
    
    # ─── TIER 1/2: OPERATOR FORM LAYOUT ───
    if st.session_state.user_role in ["Tier_1", "Tier_2"]:
        st.title("🚜 DAILY LOG ENTRY")
        
        # Isolate Native Lens Hardware (Gallery Bypass Active)
        img_file = st.camera_input("Snap Attendance Photo")
        notes_input = st.text_area("Optional Operator Notes / Site Incident Reports", placeholder="Type details here...")
        
        if st.button("Submit Daily Log Packet"):
            if img_file is not None:
                # Convert Binary Image Stream to Base64 Text Payload
                bytes_data = img_file.getvalue()
                base64_image = base64.b64encode(bytes_data).decode("utf-8")
                img_payload_string = f"data:image/jpeg;base64,{base64_image}"
                
                # Asynchronous Time-Gate Flag Assignment Rules
                hour = current_time.hour
                color_code = "GREEN"
                if not ((7 <= hour < 9) or (17 <= hour < 18)):
                    color_code = "YELLOW"  # Automated Late / Out-of-Bounds Flag Trigger
                
                # Construct JSON Payload Matrix
                payload = {
                    "metadata": {
                        "payload_id": f"LOG-{current_time.strftime('%Y%m%d%H%M%S')}",
                        "transmission_timestamp": current_time.strftime("%Y-%m-%dT%H:%M:%SWIT")
                    },
                    "operator_identity": {
                        "operator_id": "OP-024",
                        "full_name": st.session_state.operator_name
                    },
                    "telemetry": {
                        "session_type": "CLOCK_IN" if hour < 12 else "CLOCK_OUT",
                        "timestamp_wit": current_time.strftime("%Y-%m-%d %H:%M:%S"),
                        "gps_metrics": {"latitude": -3.6542, "longitude": 128.1906}  # Mock GPS Template
                    },
                    "payload_assets": {
                        "image_b64_string": img_payload_string,
                        "operator_notes": notes_input
                    },
                    "admin_state": {
                        "color_code": color_code
                    }
                }
                
                with st.spinner("Piping encrypted packet to Google Drive via API Webhook..."):
                    try:
                        res = requests.post(WEBHOOK_URL, data=json.dumps(payload), headers={"Content-Type": "application/json"}, timeout=10.0)
                        if res.status_code == 200:
                            st.success("🟢 Sync Success! Photo routed to Drive, log row appended cleanly.")
                        else:
                            st.error(f"🛑 Transmission Failure. Webhook Server Code: {res.status_code}")
                    except Exception as err:
                        st.error(f"💥 Network Anomaly Encountered: {str(err)}")
            else:
                st.warning("⚠️ Verification Requirement: You must take a live photo to execute a clock-in transaction.")

    # ─── TIER 3: DYNAMIC ADMINISTRATIVE OVERRIDE UI ───
    elif st.session_state.user_role == "Tier_3":
        st.title("📊 CHRONOS MANAGEMENT PANEL")
        st.caption("Active Visual Attendance Matrix & Operational Notes Archive")
        
        # Tab View Navigation Model
        tab1, tab2 = st.tabs(["📅 Daily Visual Grid", "📖 Operator Field Notes"])
        
        with tab1:
            st.subheader("Rolling Attendance Spreadsheet Matrix")
            # Mock Data View reflecting intended sheet tracking outputs
            matrix_mock = pd.DataFrame({
                "Operator Name": ["Azicio", "Driver_Budi", "Operator_Eko"],
                "2026-05-22": ["GREEN", "GREEN", "RED"],
                "2026-05-23": ["GREEN", "YELLOW", "GREEN"],
                "2026-05-24": ["GREEN", "PENDING", "BLUE"]
            })
            st.dataframe(matrix_mock)
            
        with tab2:
            st.subheader("Unresolved Field Logs Queue")
            # Inline Action Row Control Design Model
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.text("📝 Driver_Budi (23 Mei): Delayed due to mud track block at quarry block C.")
            with col2:
                if st.button("Mark Noticed", key="note_1"):
                    st.success("Archived to tab.")
            with col3:
                st.button("Under Review", key="review_1")

    # High-Alert Red Confirmation Box for Logout Safety Handshaking
    st.divider()
    if st.button("🚪 Force Logout Session"):
        st.markdown("""
            <div style="background-color: #450A0A; border: 2px solid #DC2626; padding: 20px; border-radius: 8px; text-align: center;">
                <p style="color: #FCA5A5; font-weight: bold; margin-bottom: 10px;">⚠️ CRITICAL SECURITY WARNING</p>
                <p style="color: white; margin-bottom: 15px;">Are you certain you want to clear your local session token cache? Non-technical users will require manual re-authentication.</p>
            </div>
        """, unsafe_allow_html=True)
        if st.button("🔴 YES, CONFIRM EVICITON", key="confirm_logout"):
            st.session_state.authenticated = False
            st.rerun()
