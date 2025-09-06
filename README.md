# Receipt Database Project

A Python application for processing, storing, and managing receipt data with OCR capabilities.

## Features

- Extract data from receipt images using OCR
- Store receipt information in a structured database
- Process various receipt formats (Safeway, etc.)
- Web interface for receipt management
- Data export capabilities

## Setup

### Prerequisites

- Python 3.8 or higher
- Tesseract OCR (for image processing)

### Installation

1. **Clone or download the project**
   ```bash
   cd /path/to/your/project
   ```

2. **Run the setup script**
   ```bash
   ./setup_environment.sh
   ```

   This will:
   - Create a Python virtual environment
   - Install all required dependencies
   - Create necessary project directories
   - Set up configuration templates

3. **Configure your environment**
   ```bash
   cp .env.template .env
   # Edit .env with your specific configuration
   ```

4. **Activate the virtual environment**
   ```bash
   source venv/bin/activate
   ```

### Manual Setup (Alternative)

If you prefer to set up manually:

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create directories
mkdir -p receipts processed_receipts logs data
```

## Project Structure

```
gemini_ai/
├── requirements.txt          # Python dependencies
├── .gitignore               # Git ignore rules
├── setup_environment.sh     # Environment setup script
├── README.md               # This file
├── safeway_receipt_data.txt # Sample extracted receipt data
├── venv/                   # Virtual environment (created by setup)
├── receipts/               # Store receipt images here
├── processed_receipts/     # Processed receipt data
├── logs/                   # Application logs
└── data/                   # Database and data files
```

## Usage

### Basic Usage

1. **Place receipt images** in the `receipts/` directory
2. **Run the OCR processor** to extract data
3. **Store data** in the database
4. **Query and manage** receipt information

### Sample Data

The project includes sample extracted data from a Safeway receipt in `safeway_receipt_data.txt` showing the expected data format.

## Dependencies

Key dependencies include:

- **pandas**: Data manipulation and analysis
- **opencv-python**: Image processing
- **pytesseract**: OCR text extraction
- **sqlalchemy**: Database ORM
- **flask**: Web framework (optional)
- **pydantic**: Data validation

See `requirements.txt` for the complete list.

## Development

### Code Quality

The project includes tools for maintaining code quality:

- **black**: Code formatting
- **flake8**: Linting
- **mypy**: Type checking
- **pytest**: Testing

### Running Tests

```bash
# Activate virtual environment first
source venv/bin/activate

# Run tests
pytest

# Run tests with coverage
pytest --cov=.
```

## Configuration

Copy `.env.template` to `.env` and configure:

- Database connection settings
- OCR engine paths
- File upload limits
- Application secrets

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## License

[Add your license information here]

## Support

For questions or issues, please [create an issue](link-to-issues) or contact [your-email].
