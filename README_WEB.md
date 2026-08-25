# Credit File Scoring Web App

A web application for analyzing credit reports and generating credit scores using machine learning.

## Features

✨ **Modern Web Interface** - Built with Streamlit for an intuitive user experience
📊 **Real-time Analysis** - Process credit reports instantly
📈 **Detailed Results** - View personal data, income analysis, and validation reports
📥 **Export Options** - Download results as JSON or CSV
🎯 **Smart Scoring** - LightGBM-based credit scoring model

## Project Structure

```
creditfile-main/
├── app.py                          # Streamlit web application
├── requirements-web.txt            # Python dependencies for web app
├── creditfile/
│   ├── main.py                    # Original Colab implementation
│   ├── parse.py                   # Excel report parsing
│   ├── normalize.py               # Data normalization
│   ├── featurize.py               # Feature extraction
│   ├── score.py                   # Credit scoring
│   ├── loancalc.py                # Loan calculations
│   ├── utils.py                   # Utility functions
│   └── artifacts/
│       └── model.txt              # Trained LightGBM model
```

## Installation

### 1. Install Python (3.8+)

Make sure you have Python installed. You can download it from [python.org](https://www.python.org/downloads/)

### 2. Clone/Download the Repository

```bash
cd creditfile-main
```

### 3. Create Virtual Environment (Recommended)

```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements-web.txt
```

## Running the Web App

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

### On First Run

Streamlit may ask for telemetry settings. You can accept or decline as preferred.

## Usage

1. **Upload a File** - Click the file uploader and select an Excel credit report (.xlsx)
2. **Wait for Processing** - The app will:
   - Parse the credit report
   - Normalize the data
   - Extract features
   - Calculate the credit score
3. **Review Results** - View:
   - Credit score (1-100) with rating
   - Personal information
   - Income analysis
   - Validation status
4. **Export Results** - Download results as JSON or CSV

## Score Interpretation

- 🟢 **75-100: Excellent** - Strong credit profile, low risk
- 🟡 **60-74: Good** - Acceptable credit profile, moderate risk
- 🟠 **40-59: Fair** - Some concerns, higher risk
- 🔴 **0-39: Poor** - Significant concerns, very high risk

## Input File Format

Credit reports must be Excel files (.xlsx) with the following sections (in order):
- Personal Data
- Dependents
- Character References
- Income Data
- Client Reputation
- Other Creditors
- Client Assets
- Credit Assessment

The app will automatically locate and parse these sections.

## Original Colab Version

The original Google Colab implementation is preserved in `creditfile/main.py`. To use it:
- Requires Google Colab environment
- Uses `google.colab` for file uploads
- Uses `ipywidgets` for interactive widgets

## Deployment Options

### Local Development
```bash
streamlit run app.py
```

### Deploy to Streamlit Cloud
1. Push code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repository
4. Select the app.py file and deploy

### Deploy to Other Platforms
- **Heroku**: Create a Procfile with `web: streamlit run app.py`
- **AWS/Azure**: Use container deployment with Docker
- **DigitalOcean**: Use App Platform with similar setup

## Docker Deployment (Optional)

Create a `Dockerfile`:
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements-web.txt .
RUN pip install -r requirements-web.txt
COPY . .
CMD ["streamlit", "run", "app.py"]
```

Build and run:
```bash
docker build -t creditfile-app .
docker run -p 8501:8501 creditfile-app
```

## Troubleshooting

### "File not found" or "Module not found" errors
- Ensure you're in the correct directory
- Verify all dependencies are installed: `pip install -r requirements-web.txt`

### LightGBM model not loading
- Check that `creditfile/artifacts/model.txt` exists
- Re-install LightGBM: `pip install --upgrade lightgbm`

### Streamlit port already in use
```bash
streamlit run app.py --server.port 8502
```

### Slow processing
- Ensure you have adequate system resources
- Close other applications
- Check file size (very large Excel files may take longer)

## Technical Details

### Pipeline Flow
1. **Parse** - Reads Excel, locates sections using regex patterns
2. **Normalize** - Standardizes field names and values
3. **Featurize** - Extracts model-ready features
4. **Score** - LightGBM prediction with score scaling (1-100)

### ML Model
- **Algorithm**: LightGBM (Light Gradient Boosting Machine)
- **Target**: Delinquency probability
- **Score Calculation**: (1 - delinquency_probability) × 100
- **Features**: 40+ engineered features from credit report

## Requirements

- Python 3.8+
- See `requirements-web.txt` for Python package versions

## License

See LICENSE file (if included)

## Support

For issues or questions, please check the troubleshooting section or contact the development team.

---

**Migration Note**: This web app replaces the Google Colab notebook interface while maintaining all the core credit scoring functionality. The machine learning model and analysis logic remain unchanged.
