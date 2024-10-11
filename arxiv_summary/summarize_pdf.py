import urllib
import pypdf
import io
import re
import anthropic
#note that basic structure of this code is taken from anthropic's github repo if receipes
#and modified to fit our porposes

def extract_text_from_pdf(pdf_url):
    # Download the PDF file
    response = urllib.request.urlopen(pdf_url)
    pdf_content = response.read()

    #read into memory
    in_memory_pdf = io.BytesIO(pdf_content)
    # Create a PDF object
    pdf = pypdf.PdfReader(in_memory_pdf)

    pdf_text = ''
    for page in pdf.pages:
        pdf_text += page.extract_text()

    return pdf_text

#remove whitespace and pagenumbers from the text
def clean_text(text):
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\n\s*\d+\s*\n', '\n', text)
    text = text.strip()
    return text

#limit the number of tokens in the text, somewhat arbitarily
def limit_tokens(text, max_tokens=100000):
    return text[:max_tokens * 4] #this is anthropics assumption of ~4 characters per token

#call the above helper functions on the pdf file given by the url
def prep_pdf_text_for_summarization(pdf_url):
    pdf_text = extract_text_from_pdf(pdf_url)
    pdf_text = clean_text(pdf_text)
    pdf_text = limit_tokens(pdf_text)
    return pdf_text

def summarize_pdf(text, max_tokens=1000):
    #assuming anthropic.Anthropic reads env for api key
    client = anthropic.Anthropic()

    #set a prompt that guides the summarization
    #surely we will need to change this later
    prompt = f"""
    Summarize the following text as if you are an accomplished researcher in the field but 
    are explaining this text to a colleague that is less experienced than you.
    You should be concise, but include what the work is, whether it is an improvement over
    previous work and what the contribution of the work is.
    {text}
    """
    response = client.messages.create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=max_tokens,
        system="You are a senior researcher that people approach for advice and learning",
        messages=[
            {
                "role": "user",
                "content": prompt
            },
            {
                "role": "assistant",
                "content": "Here is the summary of the text: <summary>"
            }
        ],
        stop_sequences=["</summary>"]
    )
    return response.content[0].text

if __name__ == "__main__":
    url = "https://arxiv.org/pdf/2410.05578.pdf"
    text = prep_pdf_text_for_summarization(url)
    summary = summarize_pdf(text)
    print(summary)  