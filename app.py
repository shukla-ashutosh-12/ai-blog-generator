import streamlit as st
from groq import Groq
import requests
groq_api_key = st.secrets["groq_api_key"]
unsplash_api_key = st.secrets["unsplash_api_key"]
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
import io

# Initialize Groq client
client = Groq(api_key=groq_api_key)

st.set_page_config(layout="wide")

st.title("Craft Your Blog AI Writing Companion")

st.subheader("Your blog is generated with high quality")

# ---------------- SIDEBAR ---------------- #

with st.sidebar:

    st.title("Give Blog Inputs")

    blog_title = st.text_input("Blog Title")

    keywords = st.text_area("Keywords (comma separated)")

    num_words = st.slider("Number of Words", 250, 1500, 500)

    num_images = st.slider("Number of Images", 1, 5, 2)

    submit_button = st.button("Generate Blog")


# ---------------- BLOG GENERATOR ---------------- #

def generate_blog(title, keywords, words):

    prompt = f"""
    Write a {words} word SEO-optimized blog about "{title}".

    Use these keywords naturally:
    {keywords}

    Structure:
    - Introduction
    - 3 to 5 detailed sections with headings
    - Bullet points where appropriate
    - Conclusion
    """

    try:

        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant"
        )

        return response.choices[0].message.content

    except Exception as e:

        st.error("Groq API Error: Unable to generate blog.")
        st.error(f"Details: {e}")

        return None


# ---------------- IMAGE FETCHER ---------------- #

def get_blog_images(query, count):

    url = "https://api.unsplash.com/photos/random"

    params = {
        "query": query,
        "client_id": unsplash_api_key,
        "count": count,
        "orientation": "landscape"
    }

    try:

        response = requests.get(url, params=params)

        if response.status_code == 200:

            data = response.json()

            return [img["urls"]["regular"] for img in data]

        else:

            st.error(f"Unsplash API Error: Status code {response.status_code}")

            return []

    except Exception as e:

        st.error("Unsplash API Error: Unable to fetch images.")
        st.error(f"Details: {e}")

        return []


# ---------------- PDF CREATOR ---------------- #

def create_pdf(title, blog_text, images):

    buffer = io.BytesIO()

    styles = getSampleStyleSheet()

    story = []

    story.append(Paragraph(title, styles["Title"]))
    story.append(Spacer(1, 20))

    paragraphs = blog_text.split("\n\n")

    img_index = 0

    for i, para in enumerate(paragraphs):

        story.append(Paragraph(para, styles["BodyText"]))
        story.append(Spacer(1, 12))

        if img_index < len(images) and i % 2 == 1:

            try:

                img_data = requests.get(images[img_index]).content
                img_buffer = io.BytesIO(img_data)

                img = Image(img_buffer, width=500, height=280)

                story.append(img)
                story.append(Spacer(1, 20))

                img_index += 1

            except:

                pass

    doc = SimpleDocTemplate(buffer, pagesize=letter)

    doc.build(story)

    buffer.seek(0)

    return buffer


# ---------------- MAIN APP ---------------- #

if submit_button:

    if blog_title and keywords:

        with st.spinner("Your blog is loading..."):

            blog = generate_blog(blog_title, keywords, num_words)

            if blog:

                images = get_blog_images(blog_title, num_images)

            else:

                st.stop()

        st.divider()

        st.header("Generated Blog")

        paragraphs = blog.split("\n\n")

        img_index = 0

        for i, para in enumerate(paragraphs):

            st.write(para)

            if img_index < len(images) and i % 2 == 1:

                st.image(images[img_index], use_container_width=True)

                img_index += 1

        st.divider()

        # TXT download
        st.download_button(
            "Download Blog as TXT",
            blog,
            file_name="blog.txt"
        )

        # PDF download
        pdf_file = create_pdf(blog_title, blog, images)

        st.download_button(
            "Download Blog as PDF",
            data=pdf_file,
            file_name="blog.pdf",
            mime="application/pdf"
        )

    else:

        st.warning("Please enter a blog title and keywords.")