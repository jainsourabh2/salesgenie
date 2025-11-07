import os
import json
import base64
import requests
import uuid 
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from flask import Flask, request, jsonify
from flask_cors import CORS

# ==============================================================================
# 1. FIXED DATA AND CONSTANTS
# ==============================================================================

# Fields expected to be encrypted and are mandatory
ENCRYPTED_FIELDS = ["mileID", "mobileNumber", "dealerCode", "parentCode"]
MANDATORY_FIELDS = ENCRYPTED_FIELDS 

# The fixed JSON response requested by the user. (Used as a FALLBACK if API fails)
FIXED_RESPONSE_DATA = {
    "ai_summary": "Customer Sales Summary: Punjab Patil PATIL**1. Customer Persona Snapshot:**- Full Name: Punjab Patil PATIL- Gender: M- Location: Nanded, Maharashtra- Work Style: Self-employed / Business owner- Opportunity Stage: Enquiry- Primary Product Interest: XUV700 (BS6.2 AX7 P MT)- Purchase Type: Exchange buy**2. Interests & Needs (Psychographic & Customer Priorities):**- Primary Product Interest: XUV700 (BS6.2 AX7 P MT)- Competitive Product Consideration: MG Motors Hector- Explicit Needs & Preferences:  - Primary Vehicle Use: Family travel (multiple passengers)  - Typical Passengers: 4 to 5 (family)  - Key Features Desired: Safety features (Airbags, ABS, etc.), Comfort & space, Fuel efficiency / EV range  - Daily Driving Kilometers: 20 to 50 km per day (or 600 to 1,500 km per month)  - Profession/Work Style: Self-employed / Business owner",
    "ai_pitch": "Punjab Patil PATIL, XUV700 (BS6.2 AX7 P MT)**Key Highlights for You, Punjab:****Cutting-Edge Safety*** 5-Star BNCAP Safety* 6 Airbags protection* Advanced Driver Assistance Systems**Unmatched Comfort & Space*** 7-seater configuration* Dual-Zone Climate Control**Dynamic Performance*** 2.0L Turbocharged Petrol Engine* 200PS Power**Smart Convenience*** 10.25-inch touchscreen infotainment* Wireless Android Auto/CarPlay* Alexa built-in**Available Colors:** Everest White, Midnight Black, Valyrian Silver, Stealth Black, Deep Forest, Burnt SiennaXUV700 BS6.2 AX7 P MT Vs MG Motors Hector1. **Powertrain Performance**: The XUV700's 2.0L turbo petrol engine delivers a peak power of 197 bhp and 380 Nm of torque, significantly higher than the MG Hector's 1.5L turbo petrol engine, which produces 141 bhp and 250 Nm of torque.2. **Safety Rating**: The XUV700 holds a 5-star Global NCAP safety rating for adult occupant protection and a 4-star rating for child occupant protection. In contrast, the MG Hector has been rated 4 stars for adult occupant protection and 3 stars for child occupant protection in some reports, while other sources indicate it is yet to be officially rated by Global NCAP or Bharat NCAP.3. **Seating Capacity**: The XUV700 AX7 P MT variant offers a 7-seater configuration. The standard MG Hector is available with a 5-seater capacity.",
    "customer_details_mdp": {
        "mobilephone": "9001223534",
        "first_name": "Maanvendra",
        "last_name": "singh",
        "gender": "M",
        "city": "JAIPUR",
        "state": "Rajasthan",
        "occupation": 49,
        "lead_create_date": "2024-12-14 14:05:13.000000 UTC",
        "lead_product_interested": "BOLERO",
        "opportunity_create_date": "2024-09-27 09:19:09.000000 UTC",
        "opportunity_product_interested": "BOLERO",
        "opportunity_completed_stages": "Enquiry",
        "opportunity_customer_comments": "XUV700 ax7 DIESEL 7 MNSentiment -ok Purchase Intent < 15 daysTest Drive -yesTD Date & Time - no slots customer insight:informedexchange:NO watsapp:nofinance scheme:noremarks::cx interested in XUV700 AX7 diesel MN 7",
        "opportunity_customer_remarks": "Interested in Additional Purchase;Interested in Dealer Discussion;Interested In Purchase;Interested In Test Drive;Needs Price Information",
        "opportunity_purchase_type": "Additional Buy",
        "opportunity_first_mahindra_consideration": "Yes",
        "test_drive_location": "None"
    }
}


# ==============================================================================
# 2. SECURITY & ENVIRONMENT CONFIGURATION (Strict Validation)
# ==============================================================================

# Global flag to track environment setup validity
IS_ENV_CONFIG_VALID = True
IS_DEBUG_LOGGING_ENABLED = os.environ.get('ENABLE_DEBUG_LOGGING', 'False').lower() in ('true', '1')

# Raw environment variables (no defaults allowed)
EXTERNAL_API_URL_NAME = os.environ.get('EXTERNAL_API_URL_NAME')
EXTERNAL_APP_NAME = os.environ.get('EXTERNAL_APP_NAME')
EXTERNAL_API_TIMEOUT_RAW = os.environ.get('EXTERNAL_API_TIMEOUT')
AES_KEY_RAW = os.environ.get('AES_KEY')
AES_IV_RAW = os.environ.get('AES_IV')

# Variables used by the application, initialized to None/zero
AES_KEY = None
AES_IV = None
EXTERNAL_API_TIMEOUT = None

# --- Validation Logic ---
MISSING_ENVS = []

# 1. Check for presence of all required variables
if not EXTERNAL_API_URL_NAME: MISSING_ENVS.append('EXTERNAL_API_URL_NAME (Missing or configured blank)')
if not EXTERNAL_APP_NAME: MISSING_ENVS.append('EXTERNAL_APP_NAME (Missing or configured blank)')
if not AES_KEY_RAW: MISSING_ENVS.append('AES_KEY (Missing or configured blank)')
if not AES_IV_RAW: MISSING_ENVS.append('AES_IV (Missing or configured blank)')
if not EXTERNAL_API_TIMEOUT_RAW: MISSING_ENVS.append('EXTERNAL_API_TIMEOUT (Missing or configured blank)')


# 2. If present, check format/length
# Check EXTERNAL_API_TIMEOUT format
if EXTERNAL_API_TIMEOUT_RAW and not 'EXTERNAL_API_TIMEOUT (Missing or configured blank)' in MISSING_ENVS:
    try:
        EXTERNAL_API_TIMEOUT = int(EXTERNAL_API_TIMEOUT_RAW)
    except ValueError:
        MISSING_ENVS.append('EXTERNAL_API_TIMEOUT (Invalid: Must be an integer)')

# Check AES_KEY length (16 bytes)
if AES_KEY_RAW and not 'AES_KEY (Missing or configured blank)' in MISSING_ENVS:
    # Key length must be 16 for AES-128
    if len(AES_KEY_RAW.encode('utf-8')) != 16:
        MISSING_ENVS.append(f'AES_KEY (Invalid: Must be 16 bytes/128 bits, found {len(AES_KEY_RAW.encode("utf-8"))})')
    else:
        AES_KEY = AES_KEY_RAW.encode('utf-8')

# Check AES_IV length (16 bytes)
if AES_IV_RAW and not 'AES_IV (Missing or configured blank)' in MISSING_ENVS:
    # IV length must be 16 for AES-128 CBC
    if len(AES_IV_RAW.encode('utf-8')) != 16:
        MISSING_ENVS.append(f'AES_IV (Invalid: Must be 16 bytes/128 bits, found {len(AES_IV_RAW.encode("utf-8"))})')
    else:
        AES_IV = AES_IV_RAW.encode('utf-8')


# 3. Finalize global state
if MISSING_ENVS:
    print(f"FATAL ERROR at startup: The following critical environment configuration issues were found: {'; '.join(MISSING_ENVS)}")
    IS_ENV_CONFIG_VALID = False
    
# --- End of Validation Logic ---

def decrypt_aes(encrypted_b64_str):
    """Decrypts a base64 encoded string using AES-128 CBC and fixed IV."""
    if not encrypted_b64_str:
        return None
        
    try:
        if AES_KEY is None or AES_IV is None: 
            return None 

        encrypted_data = base64.b64decode(encrypted_b64_str)
        cipher = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
        decrypted_padded = cipher.decrypt(encrypted_data)
        decrypted_bytes = unpad(decrypted_padded, AES.block_size)
        return decrypted_bytes.decode('utf-8')
        
    except (ValueError, TypeError, KeyError, base64.binascii.Error) as e:
        if IS_DEBUG_LOGGING_ENABLED:
            print(f"DEBUG: Decryption failed for data: {encrypted_b64_str}. Error: {e}")
        return None


# ==============================================================================
# 3. SERVICE CONFIGURATION & UTILITY
# ==============================================================================

CONFIG_FILE_PATH = os.path.join(os.path.dirname(__file__), 'config.json')

def load_config():
    """Load configuration from config.json."""
    try:
        with open(CONFIG_FILE_PATH, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Configuration file not found at {CONFIG_FILE_PATH}")
        return None
    except json.JSONDecodeError:
        print("Error: Could not decode config.json.")
        return None

CONFIG = load_config()

def run_business_validation(decrypted_data, config):
    """
    Performs business logic validation (mileID, dealerCode, parentCode) 
    against the loaded configuration.
    
    Returns: Tuple (bool is_valid, str failed_code)
    """
    mile_id = decrypted_data.get("mileID")
    dealer_code = decrypted_data.get("dealerCode")
    parent_code = decrypted_data.get("parentCode")
    
    # Check mileID
    if mile_id not in config.get("allowed_mile_ids", []):
        return False, f"mileID '{mile_id}'"
    
    # Check dealerCode
    if dealer_code not in config.get("allowed_dealer_codes", []):
        return False, f"dealerCode '{dealer_code}'"

    # Check parentCode
    if parent_code not in config.get("allowed_parent_codes", []):
        return False, f"parentCode '{parent_code}'"
        
    return True, None


# ==============================================================================
# 4. FLASK APPLICATION AND ROUTE HANDLER
# ==============================================================================

app = Flask(__name__)
CORS(app) # Initialize CORS with default settings (allows all origins)

@app.route('/', methods=['GET'])
def health_check():
    """Simple health check endpoint for Cloud Run/Kubernetes."""
    # Health check at root path (GET /) for Cloud Run compatibility.
    return jsonify({"status": "ok", "message": "Service is running"}), 200

@app.route('/process', methods=['POST'])
def process_string():
    """
    Handles incoming POST requests, acting as the coordinating function 
    for validation, decryption, and business logic processing.
    """
    
    # 0. Environment Configuration Check
    if not IS_ENV_CONFIG_VALID:
        error_message = (
            "The application failed to start due to missing or invalid environment configuration. "
            f"Please check and correct the following variables: {'; '.join(MISSING_ENVS)}"
        )
        print(f"Returning 500: {error_message}")
        return jsonify({
            "error": "Configuration Error",
            "message": error_message
        }), 500
        
    # 1. Configuration Check (config.json)
    if CONFIG is None:
        print("Returning 500: Service configuration unavailable (config.json loading failed).")
        return jsonify({"error": "Service configuration unavailable (config.json loading failed)."}), 500
        
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Request body must be valid JSON."}), 400

        # 2. Mandatory Fields Presence Check (pre-decryption)
        missing_fields = [field for field in MANDATORY_FIELDS if field not in data or data[field] is None]

        if missing_fields:
            return jsonify({
                "error": "Mandatory fields missing or empty.",
                "missing_fields": missing_fields
            }), 400
            
        # 3. Decryption
        decrypted_data = {}
        decryption_failed = False
        
        for field in ENCRYPTED_FIELDS:
            decrypted_value = decrypt_aes(data.get(field))
            
            if decrypted_value is None:
                decryption_failed = True
                print(f"Critical Decryption Failure for field: {field}")
                break
            
            decrypted_data[field] = decrypted_value
            
        if decryption_failed:
             return jsonify({
                "error": "Decryption Failed",
                "message": "One or more input fields could not be decrypted. Check key, IV, padding, and base64 encoding."
            }), 400
        
        if IS_DEBUG_LOGGING_ENABLED:
            print(f"DEBUG: Successfully decrypted data: {decrypted_data}")

        # 4. Business Validation
        is_valid, failed_code = run_business_validation(decrypted_data, CONFIG)
            
        if not is_valid:
            print(f"Returning 501: Service for {failed_code} is not configured.")
            return jsonify({
                "error": "Coming Soon",
                "message": f"Service for {failed_code} is not yet configured or available."
            }), 501 # Not Implemented
            
        # 5. External API Calls
        mobile_number = decrypted_data.get("mobileNumber")
        
        # Session UUID is concatenation of mobile_number and a new UUID
        session_uuid = f"{mobile_number}_{uuid.uuid4()}"
        
        # --- First Call: Session Tracking (Currently COMMENTED OUT for Debugging) ---
        session_creation_status = True # Manually set to True for debugging

        # session_url = (
        #     f"https://{EXTERNAL_API_URL_NAME}/apps/{EXTERNAL_APP_NAME}/users/"
        #     f"{mobile_number}/sessions/{session_uuid}"
        # )
        
        # try:
        #     response_1 = requests.post(
        #         session_url, 
        #         timeout=EXTERNAL_API_TIMEOUT,
        #         headers={'Content-Type': 'application/json'}
        #     )
        #     response_1.raise_for_status() 
        #     print(f"Successfully called external session tracking API. Status: {response_1.status_code}")
        #     session_creation_status = True
        # except requests.exceptions.RequestException as req_e:
        #     print(f"WARNING: Failed to call external session tracking API: {session_url}. Error: {req_e}")

        
        # Initialize the final response data with the fixed content as a fallback
        final_response_data = FIXED_RESPONSE_DATA

        # --- Second Call: Process Inquiry (Conditional on First Call Success) ---
        if session_creation_status:
            sse_url = f"https://{EXTERNAL_API_URL_NAME}/api/process-inquiry"
            # Use the simple mobile number payload you defined
            sse_payload = {
                "mobilephone" : mobile_number
            }
            
            try:
                # Synchronous call that respects the timeout
                response_2 = requests.post(
                    sse_url, 
                    json=sse_payload, 
                    timeout=EXTERNAL_API_TIMEOUT,
                    headers={'Content-Type': 'application/json'}
                )
                response_2.raise_for_status() # Check for HTTP status errors (4xx, 5xx)
                
                if IS_DEBUG_LOGGING_ENABLED:
                    print(f"DEBUG: Successfully called external API: {sse_url}. Status: {response_2.status_code}")
                
                # Update the final response data to be the actual response from the external API
                try:
                    response_json = response_2.json()
                    final_response_data = response_json
                    
                    print("External API JSON Response (returned to client):")
                    print(json.dumps(response_json, indent=4))
                    
                except json.JSONDecodeError:
                    # If it's not JSON, print the raw text content and use fallback
                    print(f"WARNING: External API returned non-JSON data. Using fallback response. Raw Text: {response_2.text}")
                

            except requests.exceptions.RequestException as req_e_2:
                # --- Specific Logging for Diagnostic Aid ---
                if isinstance(req_e_2, requests.exceptions.Timeout):
                    error_detail = f"Timeout Error: Request exceeded {EXTERNAL_API_TIMEOUT} seconds."
                elif isinstance(req_e_2, requests.exceptions.HTTPError):
                    # Check if response object exists before accessing status code
                    status_code = req_e_2.response.status_code if req_e_2.response is not None else 'Unknown'
                    error_detail = f"HTTP Error: Status Code {status_code}. Did the external API return an error? Response Text: {req_e_2.response.text if req_e_2.response else 'N/A'}"
                else:
                    error_detail = f"Connection/Other Error: {req_e_2}. Is the URL correct and accessible?"

                print(f"WARNING: External API call to {sse_url} failed. {error_detail}. Using fallback response.")
                # --- End of Specific Logging ---


        # 6. Success Response
        return jsonify(final_response_data), 200

    except Exception as e:
        # Catch all unexpected runtime errors
        print(f"Unexpected error processing request: {e}")
        return jsonify({"error": f"Internal Server Error: {e}"}), 500

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
