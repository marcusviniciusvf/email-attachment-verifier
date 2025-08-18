
# Email Attachment Verifier

A comprehensive email attachment verification system with security features to protect against malicious files and ensure safe email processing.

## Features

### 🔒 Security Features
- **File Type Validation**: Whitelist/blacklist file extensions
- **File Size Limits**: Configurable maximum file size restrictions
- **Virus Pattern Detection**: Basic heuristic scanning for suspicious content
- **File Header Validation**: Verify file integrity and authenticity
- **Quarantine System**: Automatically isolate suspicious files
- **Hash Verification**: SHA-256 file integrity checks

### 📁 Supported File Types
- **Documents**: PDF, DOC, DOCX, TXT, RTF
- **Images**: JPG, JPEG, PNG, GIF, BMP, TIFF
- **Archives**: ZIP, RAR, 7Z, TAR, GZ
- **Spreadsheets**: XLS, XLSX, CSV
- **Presentations**: PPT, PPTX

### 🚫 Blocked File Types
- **Executables**: EXE, BAT, CMD, COM, SCR, PIF
- **Scripts**: VBS, JS, JAR
- **System Files**: MSI, DLL, SYS

## Installation

1. Ensure you have Python 3.6+ installed
2. Install required packages:
```bash
pip install imaplib email pathlib
```

## Configuration

### Email Configuration (`configs.json`)
```json
{
    "EMAIL_USER": "your-email@gmail.com",
    "EMAIL_PASS": "your-app-password",
    "LAST_VERIFICATION": "01-Jan-2024"
}
```

### Attachment Verification Configuration (`attachment_config.json`)
```json
{
    "max_file_size_mb": 25,
    "allowed_extensions": [".pdf", ".doc", ".docx"],
    "blocked_extensions": [".exe", ".bat", ".vbs"],
    "quarantine_folder": "quarantine",
    "enable_virus_scan": true,
    "enable_file_header_validation": true,
    "enable_suspicious_pattern_detection": true,
    "log_verification_details": true
}
```

## Usage

1. **Run the main script**:
```bash
python main.py
```

2. **Monitor the output**:
   - ✅ Safe attachments are saved to `downloaded_Files/`
   - ⚠️ Suspicious files are quarantined to `quarantine/`
   - 📊 Verification summary is displayed

## How It Works

### 1. Email Processing
- Connects to Gmail via IMAP
- Downloads emails since last verification date
- Extracts attachments and metadata

### 2. Attachment Verification
- **Extension Check**: Validates file type against whitelist/blacklist
- **Size Validation**: Ensures files don't exceed size limits
- **Content Analysis**: Scans for suspicious patterns
- **Header Validation**: Verifies file format integrity
- **Hash Generation**: Creates SHA-256 checksums

### 3. Security Actions
- **Safe Files**: Saved to `downloaded_Files/` folder
- **Suspicious Files**: Moved to `quarantine/` with detailed logs
- **Blocked Files**: Completely rejected and logged

## Folder Structure

```
email-attachment-verifier/
├── main.py                    # Main script
├── configs.json              # Email credentials
├── attachment_config.json    # Verification settings
├── downloaded_Files/         # Safe attachments
├── quarantine/               # Suspicious files
└── README.md                # This file
```

## Customization

### Adding New File Types
Edit `attachment_config.json`:
```json
{
    "allowed_extensions": [".pdf", ".doc", ".docx", ".newtype"],
    "blocked_extensions": [".exe", ".bat", ".malicious"]
}
```

### Adjusting Size Limits
```json
{
    "max_file_size_mb": 50
}
```

### Enabling/Disabling Features
```json
{
    "enable_virus_scan": false,
    "enable_file_header_validation": true,
    "enable_suspicious_pattern_detection": true
}
```

## Security Considerations

### What This System Protects Against
- **Executable Files**: Prevents running malicious programs
- **Script Files**: Blocks potentially harmful scripts
- **Oversized Files**: Prevents storage attacks
- **File Spoofing**: Validates file headers
- **Suspicious Content**: Detects common attack patterns

### Limitations
- **Basic Heuristics**: Not a full antivirus solution
- **Pattern Matching**: May have false positives/negatives
- **File Analysis**: Limited to header and content scanning

### Recommendations
- Use with a proper antivirus solution
- Regularly review quarantined files
- Monitor verification logs
- Update allowed/blocked extension lists as needed

## Troubleshooting

### Common Issues

1. **IMAP Connection Failed**
   - Check email credentials in `configs.json`
   - Enable 2FA and use app passwords for Gmail

2. **Permission Errors**
   - Ensure write permissions for `downloaded_Files/` and `quarantine/` folders

3. **Configuration Errors**
   - Verify JSON syntax in configuration files
   - Check file paths and permissions

### Logs and Monitoring
- Check console output for verification details
- Review quarantine folder for blocked files
- Monitor file sizes and types in logs

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is open source and available under the MIT License.
