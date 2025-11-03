import os
from flask import Flask, request, jsonify

# The fixed JSON response requested by the user.
# In a real-world application, this would be dynamically generated
# based on the input string (e.g., using a separate LLM API call).
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

@app.route('/', methods=['POST'])
def process_string():
    """
    Handles incoming POST requests. It expects a JSON body containing a string input
    and returns a fixed JSON response structure.
    """
    try:
        # Check if the request body is valid JSON
        data = request.get_json()
        
        # In a real scenario, you would use the 'input_string' here:
        # input_string = data.get('input_string') 
        # For this example, we log and ignore it, as the output is fixed.
        if data and 'input_string' in data:
            print(f"Received input string: {data['input_string']}")
        
        # Return the hardcoded JSON response
        return jsonify(FIXED_RESPONSE_DATA), 200

    except Exception as e:
        # Handle cases where the request is not valid JSON
        print(f"Error processing request: {e}")
        return jsonify({"error": "Invalid JSON or required 'input_string' key is missing."}), 400

if __name__ == "__main__":
    # Cloud Run provides the PORT environment variable.
    # Use 8080 as a default for local testing if the PORT variable is not set.
    port = int(os.environ.get('PORT', 8080))
    # Setting host='0.0.0.0' is necessary for deployment on Cloud Run.
    app.run(host='0.0.0.0', port=port)
