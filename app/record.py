from flask import Blueprint, request

record_bp = Blueprint('record', __name__)

@record_bp.route('/time_in_instructions', methods=['POST'])
def time_in_instructions():
    try:
        qr_data = request.form.get('qrData')  # Get the QR data from the form
        print("QR Data for Time In:", qr_data)
        save_qr_data(qr_data)
        instructions = "Instructions for Time In"
        return instructions  # Return plain text instructions
    except Exception as e:
        print("Error:", e)
        return "Error processing request", 500

@record_bp.route('/time_out_instructions', methods=['POST'])
def time_out_instructions():
    try:
        qr_data = request.form.get('qrData')  # Get the QR data from the form
        print("QR Data for Time Out:", qr_data)
        save_qr_data(qr_data)
        instructions = "Instructions for Time Out"
        return instructions  # Return plain text instructions
    except Exception as e:
        print("Error:", e)
        return "Error processing request", 500

def save_qr_data(qr_data):
    try:
        with open('qr_data.txt', 'w') as file:
            file.write(qr_data)
        print("QR Data saved successfully.")
    except Exception as e:
        print("Error saving QR Data:", e)
