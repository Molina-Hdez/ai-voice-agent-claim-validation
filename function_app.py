import azure.functions as func
import logging
import json
import io
import csv
import base64
from datetime import datetime

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

# Mock claims data (simulating blob storage)
MOCK_CLAIMS_DATA = """claim_number,zip_code,customer_name,status,amount
A123,90210,John Smith,APPROVED,1500.00
B456,10001,Jane Doe,PENDING,2300.00
C789,60601,Bob Johnson,APPROVED,850.00
D012,94105,Alice Brown,REJECTED,1200.00
E345,33101,Charlie Wilson,APPROVED,3200.00
F678,98101,Eva Martinez,PENDING,1750.00
G901,78701,Frank Lee,APPROVED,920.00
H234,85001,Grace Chen,APPROVED,2100.00
I567,80202,Henry Davis,PENDING,1650.00
J890,02108,Isabel Garcia,APPROVED,2800.00"""

@app.route(route="voice-agent", methods=["POST"])
def voice_agent(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Voice agent function triggered')
    
    try:
        # Get audio data from request
        audio_data = req.get_body()
        
        if not audio_data:
            return func.HttpResponse(
                "Please provide audio data",
                status_code=400
            )
        
        # MOCK: Speech to Text
        # In production, this would use Azure Speech Services
        # For testing, we'll simulate based on audio length
        transcribed_text = mock_speech_to_text(audio_data)
        logging.info(f"Mock transcribed text: {transcribed_text}")
        
        # MOCK: Extract entities
        # In production, this would use Azure Language Service
        claim_number, zip_code = mock_extract_entities(transcribed_text)
        logging.info(f"Mock extracted - Claim: {claim_number}, Zip: {zip_code}")
        
        # Validate against mock CSV data
        validation_result = validate_claim_local(claim_number, zip_code)
        
        # Generate response message
        if validation_result['valid']:
            response_text = f"Claim {claim_number} is valid. Status is {validation_result['status']}. Amount is {validation_result['amount']} dollars."
        else:
            response_text = f"Claim {claim_number} with zip code {zip_code} could not be validated. Please check your information."
        
        # MOCK: Text to Speech
        # In production, this would use Azure Speech Services
        audio_response = mock_text_to_speech(response_text)
        
        # Return audio response
        return func.HttpResponse(
            audio_response,
            mimetype="audio/wav",
            status_code=200
        )
        
    except Exception as e:
        logging.error(f"Error in voice agent: {str(e)}")
        error_audio = mock_text_to_speech(
            "Sorry, an error occurred processing your request."
        )
        return func.HttpResponse(
            error_audio,
            mimetype="audio/wav",
            status_code=500
        )

def mock_speech_to_text(audio_data):
    """Mock speech to text for local testing"""
    # For testing, return different responses based on audio size
    audio_size = len(audio_data)
    
    # Create a simple mapping based on audio characteristics
    if audio_size < 50000:
        return "My claim number is A123 and my zip code is 90210"
    elif audio_size < 100000:
        return "My claim number is B456 and my zip code is 10001"
    elif audio_size < 150000:
        return "My claim number is C789 and my zip code is 60601"
    else:
        return "My claim number is X999 and my zip code is 00000"

def mock_extract_entities(text):
    """Mock entity extraction for local testing"""
    import re
    
    # Extract claim number (letter followed by digits)
    claim_pattern = r'[A-Za-z]\d{3}'
    claim_match = re.search(claim_pattern, text.replace('-', '').replace(' ', ''))
    claim_number = claim_match.group(0).upper() if claim_match else None
    
    # Extract zip code (5 digits)
    zip_pattern = r'\b\d{5}\b'
    zip_match = re.search(zip_pattern, text.replace('-', '').replace(' ', ''))
    zip_code = zip_match.group(0) if zip_match else None
    
    return claim_number, zip_code

def validate_claim_local(claim_number, zip_code):
    """Validate claim against mock CSV data"""
    csv_reader = csv.DictReader(io.StringIO(MOCK_CLAIMS_DATA))
    
    for row in csv_reader:
        if row['claim_number'] == claim_number and row['zip_code'] == zip_code:
            return {
                'valid': True,
                'status': row['status'],
                'amount': row['amount']
            }
    
    return {'valid': False}

def mock_text_to_speech(text):
    """Mock text to speech for local testing"""
    # Create a simple WAV header for a silent audio file
    # In production, this would be actual speech audio
    
    # Generate a mock WAV file header
    sample_rate = 16000
    duration = 2  # seconds
    num_samples = sample_rate * duration
    
    # WAV file header
    wav_header = bytearray()
    wav_header.extend(b'RIFF')
    wav_header.extend((36 + num_samples * 2).to_bytes(4, 'little'))
    wav_header.extend(b'WAVE')
    wav_header.extend(b'fmt ')
    wav_header.extend((16).to_bytes(4, 'little'))
    wav_header.extend((1).to_bytes(2, 'little'))  # PCM
    wav_header.extend((1).to_bytes(2, 'little'))  # Mono
    wav_header.extend(sample_rate.to_bytes(4, 'little'))
    wav_header.extend((sample_rate * 2).to_bytes(4, 'little'))
    wav_header.extend((2).to_bytes(2, 'little'))  # Block align
    wav_header.extend((16).to_bytes(2, 'little'))  # Bits per sample
    wav_header.extend(b'data')
    wav_header.extend((num_samples * 2).to_bytes(4, 'little'))
    
    # Add some mock audio data (silence)
    audio_data = bytes(num_samples * 2)
    
    # Add a text marker in the metadata for testing
    # This helps identify which response was generated
    metadata = f"MOCK_RESPONSE:{text[:50]}"
    
    return bytes(wav_header) + audio_data