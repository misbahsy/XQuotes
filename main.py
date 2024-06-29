import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List
import re
import os
from PIL import Image, ImageDraw, ImageFont
import io
import textwrap
import base64



# Pydantic model for structured output
class Excerpt(BaseModel):
    title: str = Field(description="The title of the excerpt")
    content: str = Field(description="The actual excerpt content of at least 1 page")

class ExcerptList(BaseModel):
    excerpts: List[Excerpt] = Field(description="List of excerpts")

# Function to extract video ID from YouTube URL
def extract_video_id(url):
    video_id_match = re.search(r"(?<=v=)[^&#]+", url)
    video_id_match = video_id_match or re.search(r"(?<=be/)[^&#]+", url)
    return video_id_match.group(0) if video_id_match else None

# Function to get transcript
def get_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join([entry['text'] for entry in transcript])
    except Exception as e:
        st.error(f"Error fetching transcript: {str(e)}")
        return None

# Function to generate excerpts using Groq
def generate_excerpts(transcript):
    llm = ChatGroq(max_tokens=4096, model="llama3-70b-8192", api_key=groq_api_key)
    parser = PydanticOutputParser(pydantic_object=ExcerptList)
    prompt_template = PromptTemplate(
        template="Extract 3-4 excerpts from the following transcript. For each excerpt, provide a title and the exact content that is at least a page long (300 words).\n\nTranscript: {transcript}\n\n{format_instructions}",
        input_variables=["transcript"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    _input = prompt_template.format_prompt(transcript=transcript)
    output = llm.predict(_input.to_string())
    return parser.parse(output)

# This is for replit as it did not recognize path of poppler-utils
# Replace with the actual path from the `which pdftoppm` command
# poppler_path = "/nix/store/1148ad1q9mhz9df2icbghgdhgv5czx4a-poppler-utils-23.02.0/bin/pdftoppm"  
# os.environ['PATH'] = f"{poppler_path}:{os.environ['PATH']}"

from pdf2image import convert_from_bytes

def pdf_to_image(pdf_content):
    images = convert_from_bytes(pdf_content)
    return images[0]  # Return the first page as an image

from xhtml2pdf import pisa
from io import BytesIO
import base64
import math

def create_pdf_from_text(title, content):
    # Estimate the font size needed to fill the page
    char_count = len(title) + len(content)
    estimated_font_size = math.sqrt(620000 / char_count)  # 620000 is an approximation of characters that fit on an A4 page
    font_size = min(max(estimated_font_size, 8), 36)  # Limit font size between 8 and 36

    # Define the HTML template
    html = f"""
    <html>
    <head>
        <style>
            @page {{ size: A4; margin: 1cm; }}
            body {{ 
                font-family: Arial, sans-serif; 
                font-size: {font_size}px;
            }}
            h1 {{ 
                text-align: center; 
                color: #333; 
                font-size: {font_size * 1.5}px;
            }}
            p {{ 
                color: #666; 
                line-height: {font_size * 1.2}px;
            }}
        </style>
    </head>
    <body>
        <h1>{title}</h1>
        <p>{content}</p>
    </body>
    </html>
    """

    # Create a PDF from the HTML
    buffer = BytesIO()
    pisa.CreatePDF(BytesIO(html.encode('utf-8')), buffer)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf

def get_pdf_download_link(pdf_content, filename, text):
    pdf_base64 = base64.b64encode(pdf_content).decode()
    href = f'<a href="data:application/pdf;base64,{pdf_base64}" download="{filename}">{text}</a>'
    return href

# Function to get image download link
def get_image_download_link(image_content, filename, text):
    image_base64 = base64.b64encode(image_content).decode()
    href = f'<a href="data:image/png;base64,{image_base64}" download="{filename}">{text}</a>'
    return href

st.title("YouTube Excerpt Generator")
# Get Groq API key
if 'GROQ_API_KEY' in os.environ:
    groq_api_key = os.environ['GROQ_API_KEY']
else:
    groq_api_key = st.text_input("Enter GROQ API key:", type="password")
    if not groq_api_key:
        st.error("Please enter your GROQ API key.")
        st.stop()

# Update the main function to use the new PDF generator
def main():
    

    youtube_url = st.text_input("Enter YouTube Video URL:")

    if youtube_url:
        video_id = extract_video_id(youtube_url)
        if video_id:
            transcript = get_transcript(video_id)
            if transcript:
                st.subheader("Full Transcript")
                st.text_area("Full transcript", transcript, height=200)

                if st.button("Generate Excerpts"):
                    with st.spinner("Generating excerpts..."):
                        excerpt_list = generate_excerpts(transcript)

                        cols = st.columns(2)
                        for i, excerpt in enumerate(excerpt_list.excerpts):
                            with cols[i % 2]:
                                st.subheader(excerpt.title)
                                st.text_area(f"Excerpt {i+1}", excerpt.content, height=150)

                                # Generate PDF and create download link
                                pdf = create_pdf_from_text(excerpt.title, excerpt.content)
                                st.markdown(
                                    get_pdf_download_link(pdf, f"excerpt_{i+1}.pdf", "Download as PDF"),
                                    unsafe_allow_html=True
                                )

                                # Convert PDF to image and create download link
                                image = pdf_to_image(pdf)
                                buffered = BytesIO()
                                image.save(buffered, format="PNG")
                                st.markdown(
                                    get_image_download_link(buffered.getvalue(), f"excerpt_{i+1}.png", "Download as Image"),
                                    unsafe_allow_html=True
                                )

                                # Display a preview of the PDF (first page)
                                st.image(pdf_to_image(pdf), caption=f"Preview of Excerpt {i+1}", use_column_width=True)
        else:
            st.error("Invalid YouTube URL")

if __name__ == "__main__":
    main()
