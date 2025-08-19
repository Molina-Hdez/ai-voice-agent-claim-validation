import streamlit as st
import requests
import wave
import struct
import io
import os

# Local function URL
FUNCTION_URL = "http://localhost:7071/api/voice-agent"

# Page config
st.set_page_config(
    page_title="AI Voice Agent - Claim Validation (Local)",
    page_icon="🎤",
    layout="centered"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        padding-top: 2rem;
    }
    .stButton > button {
        width: 100%;
        background-color: #0078D4;
        color: white;
        border-radius: 5px;
        padding: 0.5rem;
        font-weight: bold;
    }
    .stButton > button:hover {
        background-color: #005A9E;
    }
    .info-box {
        background-color: #E3F2FD;
        border: 1px solid #2196F3;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Title and description
st.title("🎤 AI Voice Agent - Claim Validation (Local Dev)")
st.markdown("""
This is a **local development version** that simulates Azure AI Services.

**How it works:**
1. Generate or upload a test audio file
2. The system will mock transcribe it based on file size
3. Validate the claim and return a response
""")

# Test mapping info
st.info("""
**Test Mapping (based on file size):**
- Small file (< 50KB) → Claim A123, Zip 90210 ✅
- Medium file (50-100KB) → Claim B456, Zip 10001 ✅  
- Large file (100-150KB) → Claim C789, Zip 60601 ✅
- Very large file (> 150KB) → Invalid claim ❌
""")

def create_test_wav(duration_seconds=3, claim_type="A123"):
    """Create a test WAV file"""
    sample_rate = 16000
    num_samples = int(sample_rate * duration_seconds)
    
    # Create WAV file in memory
    wav_buffer = io.BytesIO()
    with wave.open(wav_buffer, 'w') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)   # 16-bit
        wav_file.setframerate(sample_rate)
        
        # Generate some audio data
        for i in range(num_samples):
            value = int(32767.0 * 0.1 * (i % 100) / 100)
            data = struct.pack('<h', value)
            wav_file.writeframesraw(data)
    
    wav_buffer.seek(0)
    return wav_buffer.getvalue()

# Section 1: Generate Test Audio
st.markdown("### 🎵 Generate Test Audio")

col1, col2 = st.columns(2)
with col1:
    test_claim = st.selectbox(
        "Select test claim:",
        ["A123 (Valid)", "B456 (Valid)", "C789 (Valid)", "Invalid"]
    )

with col2:
    # Map selection to duration
    duration_map = {
        "A123 (Valid)": 1,
        "B456 (Valid)": 3,
        "C789 (Valid)": 5,
        "Invalid": 10
    }
    duration = duration_map[test_claim]
    
if st.button("🎙️ Generate Test Audio"):
    audio_data = create_test_wav(duration)
    st.session_state.audio_data = audio_data
    st.success(f"Generated {len(audio_data):,} byte audio file for {test_claim}")

# Section 2: Upload Audio
st.markdown("### 📤 Or Upload Audio File")
uploaded_file = st.file_uploader("Choose a WAV file", type=['wav'])

if uploaded_file is not None:
    st.session_state.audio_data = uploaded_file.read()
    st.success(f"Uploaded {len(st.session_state.audio_data):,} byte audio file")

# Display audio if available
if 'audio_data' in st.session_state and st.session_state.audio_data:
    st.markdown("### 🎧 Your Audio")
    st.audio(st.session_state.audio_data, format='audio/wav')
    
    # Show file size for debugging
    file_size = len(st.session_state.audio_data)
    expected_result = "Unknown"
    if file_size < 50000:
        expected_result = "A123/90210 (APPROVED)"
    elif file_size < 100000:
        expected_result = "B456/10001 (PENDING)"
    elif file_size < 150000:
        expected_result = "C789/60601 (APPROVED)"
    else:
        expected_result = "X999/00000 (INVALID)"
    
    st.info(f"File size: {file_size:,} bytes → Expected: {expected_result}")

# Process button
if 'audio_data' in st.session_state and st.session_state.audio_data:
    if st.button("🚀 Validate Claim", type="primary"):
        with st.spinner("🤖 Processing your request..."):
            try:
                # Check if function is running
                response = requests.post(
                    FUNCTION_URL,
                    data=st.session_state.audio_data,
                    headers={"Content-Type": "audio/wav"},
                    timeout=10
                )
                
                if response.status_code == 200:
                    st.session_state.response_audio = response.content
                    st.success("✅ Claim validation completed!")
                    
                    # Display response audio
                    st.markdown("### 🔊 AI Agent Response")
                    st.audio(response.content, format='audio/wav')
                    st.info("Note: This is a mock audio response (silent) for local testing")
                    
                else:
                    st.error(f"❌ Error: {response.status_code}")
                    st.text(response.text)
                    
            except requests.exceptions.ConnectionError:
                st.error("""
                ❌ Cannot connect to local Azure Function!
                
                Please make sure:
                1. Your Azure Function is running in another terminal
                2. You see: "Http Functions: voice-agent: [POST] http://localhost:7071/api/voice-agent"
                3. There are no firewall issues blocking localhost:7071
                """)
            except Exception as e:
                st.error(f"❌ An error occurred: {str(e)}")

# Test data display
with st.expander("📊 Available Test Claims"):
    st.markdown("""
    | Claim # | Zip Code | Customer | Status | Amount |
    |---------|----------|----------|---------|---------|
    | A123 | 90210 | John Smith | APPROVED | $1,500.00 |
    | B456 | 10001 | Jane Doe | PENDING | $2,300.00 |
    | C789 | 60601 | Bob Johnson | APPROVED | $850.00 |
    | D012 | 94105 | Alice Brown | REJECTED | $1,200.00 |
    | E345 | 33101 | Charlie Wilson | APPROVED | $3,200.00 |
    """)

# Architecture explanation
with st.expander("🏗️ Architecture Overview"):
    st.markdown("""
    **Local Simulation Flow:**
    1. **Frontend (Streamlit)**: Captures/generates audio
    2. **Backend (Azure Function)**: Processes request locally
    3. **Mock Speech-to-Text**: Returns text based on file size
    4. **Mock NER**: Extracts entities using regex
    5. **Local Validation**: Checks hardcoded CSV data
    6. **Mock Text-to-Speech**: Returns valid WAV file
    
    **In Production:**
    - Replace mock functions with Azure AI Services
    - Use Azure Blob Storage for claims data
    - Deploy function to Azure
    - Add authentication and security
    """)

# Footer
st.markdown("---")
st.markdown("🏗️ Local Development Version - No Azure Services Required", help="POC for AI Voice Agent")