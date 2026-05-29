import streamlit as st
import datetime
import requests
import json
import base64  
import pandas as pd  
import os  

# 1. Pipeline Authorization Key Acquisition
if "github" in st.secrets:
    WEBHOOK_URL = st.secrets["github"]["webhook_url"]
else:
    WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbwuLXTiuSDkFFpRpWoY8PiREPZ6gBPFZI8WoBeT1DyYIRCY5Ha0vELh816gjnyJinCy3Q/exec"

# Coordinate Timezone Realignment (WIT - GMT+9)
WIT = datetime.timezone(datetime.timedelta(hours=9))

def get_now_wit():
    return datetime.datetime.now(datetime.timezone.utc).astimezone(WIT)

# Extract Corporate CSS UI Shading Layer
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
            color: #FCA5A5; font-size: 0.95rem;
        }
        .roster-card {
            background-color: #1E293B; border: 1px solid #334155;
            padding: 12px; border-radius: 6px; margin-bottom: 8px;
        }
    </style>
""", unsafe_allow_html=True)

# Initialize Persistent Session State Tokens
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_role" not in st.session_state:
    st.session_state.user_role = "Tier_1"
if "operator_name" not in st.session_state:
    st.session_state.operator_name = ""

USER_DB_PATH = "data/users.json"

# Helper function to access data/users.json file safely
def load_user_database():
    os.makedirs("data", exist_ok=True)
    if os.path.exists(USER_DB_PATH):
        with open(USER_DB_PATH, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

# 🛠️ REUSABLE ATTENDANCE LOG MODULE ENGINE
def render_attendance_form(display_title="📸 FIELD ATTENDANCE TRANSMISSION"):
    st.title(display_title)
    current_time = get_now_wit()
    
    # Isolate Native Lens Hardware (Gallery Input Bypassed)
    img_file = st.camera_input("Snap Live Identity Photo Verification")
    notes_input = st.text_area("Optional Field Notes / Incident Logs", placeholder="Type shift annotations here...")
    
    if st.button("Transmit Attendance Packet", key="transmit_btn_global"):
        if img_file is not None:
            bytes_data = img_file.getvalue()
            base64_image = base64.b64encode(bytes_data).decode("utf-8")
            img_payload_string = f"data:image/jpeg;base64,{base64_image}"
            
            hour = current_time.hour
            color_code = "GREEN"
            if not ((7 <= hour < 9) or (17 <= hour < 18)):
                color_code = "YELLOW"  
            
            payload = {
                "metadata": {
                    "payload_id": f"LOG-{current_time.strftime('%Y%m%d%H%M%S')}",
                    "transmission_timestamp": current_time.strftime("%Y-%m-%dT%H:%M:%SWIT")
                },
                "operator_identity": {
                    "operator_id": "OP-LOGGED",
                    "full_name": st.session_state.operator_name
                },
                "telemetry": {
                    "session_type": "CLOCK_IN" if hour < 12 else "CLOCK_OUT",
                    "timestamp_wit": current_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "gps_metrics": {"latitude": -3.6542, "longitude": 128.1906}
                },
                "payload_assets": {
                    "image_b64_string": img_payload_string,
                    "operator_notes": notes_input
                },
                "admin_state": {
                    "color_code": color_code
                }
            }
            
            with st.spinner("Piping data packet downstream to webhook array..."):
                try:
                    res = requests.post(WEBHOOK_URL, data=json.dumps(payload), headers={"Content-Type": "application/json"}, timeout=12.0)
                    if res.status_code == 200:
                        # Inspect the custom inner response text payload to verify Apps Script success
                        server_response = res.json()
                        if server_response.get("status") == "SUCCESS":
                            st.success("🟢 Ledger synchronized! Row successfully appended to Google Sheets.")
                        else:
                            st.markdown(f'<div class="error-box">🛑 Backend Exception: {server_response.get("message")}</div>', unsafe_allow_html=True)
                    else:
                        st.error(f"🛑 Transmission Error. Web App Server Code: {res.status_code}")
                except Exception as err:
                    st.error(f"💥 Network Anomaly Encountered: {str(err)}")
        else:
            st.warning("⚠️ Access Requirement: Photo verification asset must be captured to execute log.")

# --- GATEWAY IDENTITY LOGIN SCREEN ---
if not st.session_state.authenticated:
    st.title("🔒 CHRONOS IDENTITY GATEWAY")
    st.caption("Project Chronos Mobilized Attendance Interface — Seram Core")
    
    phone_input = st.text_input("📞 Enter Phone Number ID", placeholder="e.g., 0812XXXXXXXX")
    pin_input = st.text_input("🔑 Enter 4-Digit Security PIN", type="password", max_chars=4)
    
    if st.button("Verify System Credentials"):
        user_db = load_user_database()
        cleaned_phone = phone_input.strip()
        
        if cleaned_phone in user_db:
            target_user = user_db[cleaned_phone]
            if pin_input == target_user["pin"]:
                st.session_state.authenticated = True
                st.session_state.user_role = target_user["role"]
                st.session_state.operator_name = target_user["name"]
                st.rerun()
            else:
                st.markdown('<div class="error-box">❌ Access Denied: Incorrect Security PIN verification code.</div>', unsafe_allow_html=True)
        else:
            if cleaned_phone == "" or pin_input == "":
                st.markdown('<div class="error-box">⚠️ Input Requirement: Identity fields cannot remain unpopulated.</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="error-box">⚠️ Authentication Anomaly: Phone entry row not registered.</div>', unsafe_allow_html=True)

# --- POST-AUTHENTICATION ACTIVE ENVIRONMENT ---
else:
    current_time = get_now_wit()
    
    # ─── TIER 1 / TIER 2: STANDARD OPERATOR CONSOLE ───
    if st.session_state.user_role in ["Tier_1", "Tier_2"]:
        st.subheader(f"💼 Connected: {st.session_state.operator_name}")
        st.caption(f"Clearance Status: {st.session_state.user_role} | Time: {current_time.strftime('%Y-%m-%d %H:%M:%S')} WIT")
        render_attendance_form("📸 FIELD ATTENDANCE TRANSMISSION")

    # ─── TIER 3: SUPERVISOR CONTROL COCKPIT ───
    elif st.session_state.user_role == "Tier_3":
        # Global Navigation Split: Separate your personal logging from management views
        st.title("📊 CHRONOS ADMINISTRATIVE HUB")
        st.markdown(f"Welcome back, Administrator **{st.session_state.operator_name}**")
        
        admin_view = st.sidebar.radio("Console Mode", ["🚜 Personal Shift Logging", "🛠️ Corporate Management Ledger"])
        
        if admin_view == "🚜 Personal Shift Logging":
            st.caption(f"Admin Verification Tracking Running | Current Time: {current_time.strftime('%Y-%m-%d %H:%M:%S')} WIT")
            render_attendance_form("🚜 PERSONAL SHIFT RECORDING")
            
        elif admin_view == "🛠️ Corporate Management Ledger":
            tab1, tab2 = st.tabs(["📅 Live Visual Roster", "👥 Personnel Registration Panel"])
            
            with tab1:
                st.subheader("Visual Attendance Matrix Spread View")
                st.markdown(
                    '<div style="background-color: #1a1c23; border-left: 4px solid #00bcff; padding: 15px; border-radius: 4px; color: #cbd5e1;">'
                    'ℹ️ <strong>System Status:</strong> Operational ledger is actively listening to Google sheet rows via webapp webhook. '
                    'Ensure spreadsheet tab remains named <em>Log_Transactions</em>.'
                    '</div>', 
                    unsafe_allow_html=True
                )
                
            with tab2:
                st.subheader("Append Personnel Credentials")
                st.caption("Direct administrative injection interface into user database fuel matrix.")
                
                reg_phone = st.text_input("Operator Phone Number ID (Unique Key)", placeholder="e.g., 0812XXXXXXXX")
                reg_name = st.text_input("Operator Full Legal Name", placeholder="e.g., Kaka Rino")
                reg_pin = st.text_input("Assign 4-Digit Security PIN", max_chars=4, type="password")
                reg_role = st.selectbox("Assign System Authorization Level", ["Tier_1", "Tier_2", "Tier_3"])
                
                if st.button("🔐 Commit Operator to System Matrix"):
                    if reg_phone.strip() == "" or reg_name.strip() == "" or reg_pin.strip() == "":
                        st.warning("⚠️ Input Error: Personnel configuration fields cannot remain empty.")
                    elif len(reg_pin.strip()) != 4:
                        st.error("🛑 Security Exception: PIN code asset must be exactly 4 digits.")
                    else:
                        user_db = load_user_database()
                        user_db[reg_phone.strip()] = {
                            "pin": reg_pin.strip(),
                            "name": reg_name.strip(),
                            "role": reg_role
                        }
                        with open(USER_DB_PATH, "w") as f:
                            json.dump(user_db, f, indent=2)
                            
                        st.success(f"⚡ Success: Personnel credentials for '{reg_name}' saved!")
                        st.text("Refreshing roster data matrix...")
                        st.rerun()
                
                # 👥 REFINED VISUAL ROSTER SECTOR WITH LOCAL EVICTION BUTTONS
                st.write("---")
                st.subheader("👥 Active System Operational Roster")
                st.caption("Current authenticated system access tokens stored inside data/users.json database.")
                
                user_db = load_user_database()
                
                if user_db:
                    for phone, info in list(user_db.items()):
                        # Establish an alignment columns layout grid wrapper
                        col_id, col_details, col_action = st.columns([2, 3, 1.5])
                        
                        with col_id:
                            st.markdown(f"**📞 ID Key:**<br>`{phone}`", unsafe_allow_html=True)
                        with col_details:
                            st.markdown(f"👤 **Name:** {info['name']}<br>🛡️ **Clearance:** `{info['role']}`", unsafe_allow_html=True)
                        with col_action:
                            # Generate cell tracking state tags using the unique phone ID key
                            if st.button("🗑️ Evict User", key=f"evict_token_{phone}"):
                                del user_db[phone]
                                with open(USER_DB_PATH, "w") as f:
                                    json.dump(user_db, f, indent=2)
                                st.success(f"Successfully deleted token for {info['name']}.")
                                st.rerun()
                        st.markdown('<hr style="margin:8px 0; border:0; border-top:1px solid #334155;">', unsafe_allow_html=True)
                else:
                    st.info("No operators currently found registered inside the local JSON file database.")

    # Red Confirmation Boundary for Logout Safety Handshaking
    st.divider()
    if st.button("🚪 Terminate Session Portal"):
        st.markdown("""
            <div style="background-color: #450A0A; border: 2px solid #DC2626; padding: 20px; border-radius: 8px; text-align: center;">
                <p style="color: #FCA5A5; font-weight: bold; margin-bottom: 10px;">⚠️ CRITICAL SECURITY HANDSHAKE</p>
                <p style="color: white; margin-bottom: 15px;">Are you certain you want to drop your current session access token? Manual re-authentication will be required.</p>
            </div>
        """, unsafe_allow_html=True)
        if st.button("🔴 CONFIRM COMPLETE EVICTION", key="execute_logout_confirmed"):
            st.session_state.authenticated = False
            st.rerun()