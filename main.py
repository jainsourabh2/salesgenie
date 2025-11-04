import os
import json # New import for JSON configuration
from flask import Flask, request, jsonify
from flask_cors import CORS

# The fixed JSON response requested by the user.
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

app = Flask(__name__)
CORS(app) # Initialize CORS with default settings (allows all origins)

# Define the path to the configuration file (assuming it's in the same directory)
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

@app.route('/', methods=['POST'])
def process_string():
    """
    Handles incoming POST requests, validates mandatory input fields and 
    codes against the configuration, and returns the response.
    """
    
    # Check if config was loaded successfully
    if CONFIG is None:
        return jsonify({"error": "Service configuration unavailable."}), 500
        
    MANDATORY_FIELDS = ["mileID", "mobileNumber", "dealerCode", "parentCode"]
    
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Request body must be valid JSON."}), 400

        # 1. Mandatory Fields Check
        missing_fields = [field for field in MANDATORY_FIELDS if field not in data or data[field] is None]

        if missing_fields:
            return jsonify({
                "error": "Mandatory fields missing or empty.",
                "missing_fields": missing_fields
            }), 400
            
        # 2. Code Validation Check against Configuration
        
        mile_id = data.get("mileID")
        dealer_code = data.get("dealerCode")
        parent_code = data.get("parentCode")
        
        validation_failed = False
        failed_code = None
        
        # Check mileID
        if mile_id not in CONFIG.get("allowed_mile_ids", []):
            validation_failed = True
            failed_code = f"mileID '{mile_id}'"
        
        # Check dealerCode
        elif dealer_code not in CONFIG.get("allowed_dealer_codes", []):
            validation_failed = True
            failed_code = f"dealerCode '{dealer_code}'"

        # Check parentCode
        elif parent_code not in CONFIG.get("allowed_parent_codes", []):
            validation_failed = True
            failed_code = f"parentCode '{parent_code}'"
            
        # If any validation failed, return the "Coming Soon" error
        if validation_failed:
            return jsonify({
                "error": "Coming Soon",
                "message": f"Service for {failed_code} is not yet configured or available."
            }), 501 # Not Implemented
            
        # All mandatory fields and code validations passed
        print(f"Received valid request data: {data}")
        return jsonify(FIXED_RESPONSE_DATA), 200

    except Exception as e:
        # Catch exceptions during JSON parsing or general runtime errors (e.g., malformed JSON)
        print(f"Unexpected error processing request: {e}")
        return jsonify({"error": f"Internal Server Error or invalid request format."}), 500

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
