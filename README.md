# MBR Automation Agent

An AI-powered tool for AWS Technical Account Managers to automate Monthly Business Review (MBR) preparation using Amazon Bedrock and Claude.

## Features

- **Automated Slide Analysis**: Uses Claude 3.5 Sonnet to analyze each slide
- **Context-Aware**: Incorporates previous MBR notes, SA/CSM notes, and custom context
- **Comprehensive Outputs**:
  - PowerPoint with talking points in speaker notes
  - Action items document (Markdown)
  - Q&A document with anticipated questions and answers
- **Web Interface**: Simple Flask-based UI for easy uploads and downloads
- **Future-Ready**: Outlook integration code included but not active

## Prerequisites

- Python 3.8+
- AWS credentials with Bedrock access
- Amazon Bedrock model access: `us.anthropic.claude-3-5-sonnet-20241022-v2:0`

## Installation

1. **Clone or navigate to the project directory**:
   ```bash
   cd mbr-automation-agent
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment** (optional):
   ```bash
   cp .env.example .env
   # Edit .env if you want to customize settings
   ```

   Note: AWS credentials are hardcoded in `services/bedrock_service.py` as specified.

## Usage

1. **Start the application**:
   ```bash
   python app.py
   ```

2. **Access the web interface**:
   Open your browser to `http://localhost:5000`

3. **Upload and process**:
   - Upload PowerPoint presentation (.pptx)
   - Enter customer name
   - Select audience type (Technical/Business/Mixed)
   - Optionally upload previous MBR notes (PDF/TXT)
   - Optionally upload SA/CSM notes (PDF/TXT)
   - Optionally add additional context text
   - Review details and process

4. **Download results**:
   - Enhanced presentation with talking points
   - Action items document
   - Q&A document

## Project Structure

```
mbr-automation-agent/
├── app.py                      # Flask application
├── config.py                   # Configuration
├── requirements.txt            # Dependencies
├── README.md                   # This file
├── .env.example               # Environment template
├── services/
│   ├── bedrock_service.py     # Claude/Bedrock integration (ACTIVE)
│   ├── pptx_service.py        # PowerPoint handling (ACTIVE)
│   ├── outlook_service.py     # Outlook/Graph API (READY, not called)
│   ├── context_gatherer.py    # File reading and context (ACTIVE)
│   └── presentation_agent.py  # Main orchestration
├── templates/
│   ├── index.html             # Upload form
│   ├── review.html            # Review page
│   └── download_direct.html   # Download page
├── uploads/                    # Temporary upload storage
└── outputs/                    # Generated files
```

## Output Files

All outputs are saved in the `outputs/` folder with timestamps:

- `{Customer}_MBR_{timestamp}.pptx` - Presentation with talking points in speaker notes
- `{Customer}_ActionItems_{timestamp}.md` - Action items organized by slide
- `{Customer}_QA_{timestamp}.md` - Anticipated questions and answers

## Future Enhancements

### Outlook Integration

The Outlook service is implemented but not currently active. To enable:

1. Obtain Microsoft Graph API personal access token
2. Add token to `.env`:
   ```
   OUTLOOK_ACCESS_TOKEN=your_token_here
   ```
3. Update `context_gatherer.py` to call `outlook_service.search_emails()`
4. Modify context gathering to include email summaries

## Configuration

## Configuration

### AWS Credentials

Set your AWS credentials as environment variables:

```bash
export AWS_ACCESS_KEY_ID=your_access_key_here
export AWS_SECRET_ACCESS_KEY=your_secret_key_here
export AWS_REGION=us-east-1
export BEDROCK_MODEL_ID=us.anthropic.claude-3-5-sonnet-20241022-v2:0
```

Or add them to your `.env` file:

```
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_REGION=us-east-1
BEDROCK_MODEL_ID=us.anthropic.claude-3-5-sonnet-20241022-v2:0
```

### Environment Variables

Optional configuration in `.env`:
- `AWS_REGION` - AWS region (default: us-east-1)
- `BEDROCK_MODEL_ID` - Bedrock model ID
- `OUTLOOK_ACCESS_TOKEN` - For future Outlook integration
- `FLASK_SECRET_KEY` - Flask session secret

## Error Handling

- File upload validation (size, type)
- Bedrock API error handling
- File reading error handling
- Session management for multi-step workflow

## Security Notes

- Uploaded files are stored temporarily in `uploads/`
- Session data is used for multi-step workflow
- Change `FLASK_SECRET_KEY` in production
- Consider rotating AWS credentials regularly

## Troubleshooting

**Bedrock Access Denied**:
- Verify AWS credentials have Bedrock permissions
- Ensure model access is enabled in AWS console

**File Upload Errors**:
- Check file size (max 50MB)
- Verify file extensions (.pptx, .pdf, .txt)

**Processing Errors**:
- Check Bedrock API quotas
- Verify presentation format is valid

## Support

For issues or questions, contact your AWS Technical Account Manager or AWS Support.
