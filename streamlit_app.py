import os
import zipfile
import io
import base64
import streamlit as st
from google import genai
from google.genai import types
from io import BytesIO
from zipfile import ZipFile

# Set up Gemini API client
def generate_code(language, prompt):
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    model = "gemini-2.5-flash"
    contents = [
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=prompt)],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        temperature=2,
        max_output_tokens=65535,
        thinking_config=types.ThinkingConfig(thinking_budget=0),
    )
    code = ""
    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        code += chunk.text
    return code

# Handle file upload and extraction
def handle_zip_upload(uploaded_file):
    with zipfile.ZipFile(uploaded_file, 'r') as zip_ref:
        zip_ref.extractall("uploaded_files")
    return "uploaded_files"

# Create a zip file from a directory
def create_zip_from_dir(directory):
    zip_buffer = BytesIO()
    with ZipFile(zip_buffer, 'w') as zip_file:
        for folder_name, subfolders, filenames in os.walk(directory):
            for filename in filenames:
                file_path = os.path.join(folder_name, filename)
                zip_file.write(file_path, os.path.relpath(file_path, directory))
    zip_buffer.seek(0)
    return zip_buffer

# Streamlit UI
def main():
    st.title("End-to-End Application Generator")
    language = st.selectbox("Select Programming Language", ["Python", "JavaScript", "Java", "C++", "Ruby"])
    prompt = st.text_area("Enter your application requirements:")
    if st.button("Generate Code"):
        if prompt:
            code = generate_code(language, prompt)
            st.code(code, language=language.lower())
            zip_buffer = create_zip_from_dir("generated_files")
            st.download_button(
                label="Download Project as ZIP",
                data=zip_buffer,
                file_name="generated_project.zip",
                mime="application/zip"
            )
        else:
            st.error("Please enter a prompt.")

    uploaded_file = st.file_uploader("Upload a ZIP file", type="zip")
    if uploaded_file:
        extracted_dir = handle_zip_upload(uploaded_file)
        st.success(f"Extracted files to {extracted_dir}")

if __name__ == "__main__":
    main()
