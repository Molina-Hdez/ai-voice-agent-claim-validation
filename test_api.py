import requests
import wave
import struct
import io

def create_simple_wav():
    """Create a simple test WAV file"""
    sample_rate = 16000
    duration = 2  # 2 seconds = medium size
    
    wav_buffer = io.BytesIO()
    with wave.open(wav_buffer, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        
        # Generate simple audio data
        num_samples = sample_rate * duration
        for i in range(num_samples):
            value = int(100 * (i % 100))
            data = struct.pack('<h', value)
            wav_file.writeframesraw(data)
    
    wav_buffer.seek(0)
    return wav_buffer.getvalue()

# Test the API
print("Testing Azure Function API...")
print("-" * 50)

# Create test audio
audio_data = create_simple_wav()
print(f"Created test audio: {len(audio_data)} bytes")

# Send request
try:
    response = requests.post(
        "http://localhost:7071/api/voice-agent",
        data=audio_data,
        headers={"Content-Type": "audio/wav"},
        timeout=5
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ Success! Function is working!")
        print(f"Response size: {len(response.content)} bytes")
        # Save response
        with open("test_response.wav", "wb") as f:
            f.write(response.content)
        print("Response saved as test_response.wav")
    else:
        print(f"❌ Error: {response.text}")
        
except requests.exceptions.ConnectionError:
    print("❌ Connection Error: Make sure the Azure Function is running")
except Exception as e:
    print(f"❌ Error: {e}")