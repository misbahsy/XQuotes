# XQuotes

XQuotes is a Streamlit app that generates excerpts from YouTube video transcripts using language models and allows users to download the excerpts as PDFs and images.

## Features

- Extracts 3-4 excerpts from a YouTube video transcript.
- Provides a structured view of the full transcript.
- Generates downloadable PDFs and images for each excerpt.
- Supports customization through environment variables.

![Excerpt Example](example_images/excerpt_3.png)


## Setup

### Prerequisites

- Python 3.7+
- pip (Python package installer)

### Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/misbahsy/XQuotes.git
    cd XQuotes
    ```

2. Install dependencies using pip:

    ```bash
    pip install -r requirements.txt
    ```

### Environment Variables

The following environment variables need to be set:

- **GROQ_API_KEY**: API key for the Groq service. Obtain it from [Groq](https://groq.com) if you don't have one.

### Running the App

Run the Streamlit app locally:

```bash
streamlit run app.py
```

The app will be accessible in your web browser at http://localhost:8501.

If you encounter issues with PDF generation, ensure that poppler-utils is installed in your environment. This package is required for PDF to image conversion.

### Contributing
Contributions are welcome! Please fork the repository and submit a pull request with your improvements.

### License
This project is licensed under the MIT License - see the LICENSE file for details.