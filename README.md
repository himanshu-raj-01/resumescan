# ResumeScan

## Overview
ResumeScan is a powerful tool designed to analyze and extract relevant information from resumes. This project leverages natural language processing (NLP) techniques to scan resumes and provide structured insights, making it easier for recruiters and hiring managers to shortlist candidates efficiently.

## Features
- Extract key details such as Name, Contact Information, Skills, Experience, and Education.
- Supports multiple resume formats (PDF, DOCX, etc.).
- Uses NLP techniques to categorize and analyze content.
- User-friendly interface for uploading and processing resumes.
- Provides structured output for easy integration with HR systems.

## Tech Stack
- **Programming Language:** Python
- **Framework:** Flask (for API & UI)
- **Libraries:**
  - `spaCy` (for NLP processing)
  - `pdfminer.six` (for parsing PDF resumes)
  - `docx2txt` (for parsing DOCX resumes)
  - `pandas` (for data structuring and analysis)
  - `Flask` (for building the web application)

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/himanshu-raj-01/resumescan.git
   cd resumescan
   ```
2. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage
1. Run the application:
   ```bash
   python app.py
   ```
2. Open your browser and go to:
   ```
   http://127.0.0.1:5000
   ```
3. Upload a resume file and view the extracted details.

## Project Structure
```
resumescan/
│-- app.py             # Main application file
│-- requirements.txt   # List of dependencies
│-- templates/         # HTML templates for UI
│-- static/            # CSS, JS, and other static files
│-- models/            # NLP models and data processing
│-- utils/             # Utility functions
│-- uploads/           # Directory to store uploaded resumes
```

## Contributing
Contributions are welcome! Feel free to fork the repository, create a new branch, and submit a pull request.

## License
This project is licensed under the MIT License.

## Contact
For any inquiries or suggestions, feel free to reach out:
- **GitHub:** [himanshu-raj-01](https://github.com/himanshu-raj-01)
- **Email:** your-email@example.com (replace with your actual email)