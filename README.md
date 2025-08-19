# AI Voice Agent for Claim Validation

A proof-of-concept serverless voice agent that validates insurance claims using Azure Functions and AI services.

## Architecture Overview

This project demonstrates a serverless architecture using:
- **Azure Functions** - Serverless compute for processing
- **Azure AI Services** (mocked) - Speech-to-text and text-to-speech
- **Streamlit** - Web frontend for audio capture
- **Python** - Backend implementation

## Features

- 🎤 Voice input capture via web interface
- 🗣️ Speech-to-text transcription (mocked)
- 📝 Entity extraction for claim numbers and zip codes
- ✅ Claim validation against CSV data
- 🔊 Text-to-speech response generation (mocked)

## Local Development Setup

### Prerequisites

- Python 3.8+
- Azure Functions Core Tools
- pip package manager

### Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd voice-agent-project
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Start the Azure Function:
```bash
func start
```

4. In a new terminal, run the Streamlit app:
```bash
streamlit run streamlit_simple.py
```

## Testing

Test the API directly:
```bash
python test_api.py
```

## How It Works

1. User records audio or uploads a WAV file
2. Audio is sent to the Azure Function
3. Function processes the audio (mocked in local version):
   - Converts speech to text
   - Extracts claim number and zip code
   - Validates against claims data
   - Generates audio response
4. Response is played back to the user

## Test Claims

| Claim # | Zip Code | Status | Amount |
|---------|----------|---------|---------|
| A123 | 90210 | APPROVED | $1,500.00 |
| B456 | 10001 | PENDING | $2,300.00 |
| C789 | 60601 | APPROVED | $850.00 |

## Production Deployment

To deploy to Azure:

1. Create Azure resources:
   - Azure Function App
   - Azure Storage Account
   - Azure AI Services
   - Azure Key Vault

2. Update configuration with real Azure service endpoints
3. Deploy using Azure Functions Core Tools or CI/CD

## Security Considerations

- Uses Azure Key Vault for secrets management
- Implements managed identity for service authentication
- Function-level authorization for API access

## Future Enhancements

- Real Azure AI Services integration
- Database storage instead of CSV
- Enhanced error handling
- API rate limiting
- Multi-language support

## License

This is a proof-of-concept project for demonstration purposes.
