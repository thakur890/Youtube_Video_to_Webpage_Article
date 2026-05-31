import os
import zipfile
import streamlit as st
from dotenv import load_dotenv

from langchain_community.document_loaders import YoutubeLoader
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableBranch, RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq

# ==========================================
# 1. INITIALIZATION, THEME MANAGEMENT & STYLES
# ==========================================
st.set_page_config(page_title="Video to Web-page Engine", page_icon="🌐", layout="wide")
load_dotenv()

# Initialize custom theme state if it doesn't exist
if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "Light"

# Aesthetic Sidebar with Theme Toggle
with st.sidebar:
    st.markdown("## ⚙️ App Controls")
    
    # Toggle theme state value
    theme = st.selectbox("Select Theme Mode", ["Light", "Dark/Night"], 
                         index=0 if st.session_state.theme_mode == "Light" else 1)
    st.session_state.theme_mode = "Light" if theme == "Light" else "Dark"
    
    st.markdown("---")
    st.markdown("### 🛠️ System Architecture")
    st.caption("Engineered using LangChain (LCEL), Gemini 2.5 Flash, and Groq Cloud providers.")

# Injecting clean CSS dynamically based on the selected sidebar theme toggle
if st.session_state.theme_mode == "Dark":
    st.markdown(
        """
        <style>
        .stApp {
            background-color: #0E1117 !important;
            color: #FAFAFA !important;
        }
        /* Style text inputs and cards for visibility in dark mode */
        div[data-baseweb="input"] input {
            color: #FAFAFA !important;
            background-color: #1E232E !important;
        }
        div[data-testid="stExpander"] {
            background-color: #1E232E !important;
            border: 1px solid #313A46 !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

# Guardrails for API Keys
if not os.getenv("GOOGLE_API_KEY"):
    st.error("Missing GOOGLE_API_KEY in environment variables or .env file.")
    st.stop()

if not os.getenv("GROQ_API_KEY"):
    st.error("Missing GROQ_API_KEY in environment variables or .env file.")
    st.stop()   

# Cache models safely using distinct function naming rules
@st.cache_resource
def init_gemini():
    return ChatGoogleGenerativeAI(model='gemini-2.5-flash', temperature=0.2)

@st.cache_resource
def init_groq():
    return ChatGroq(model='qwen/qwen3-32b', temperature=0.2)

llm = init_gemini()
llm_groq = init_groq()

# ==========================================
# 2. TRANSCRIPT LOGIC
# ==========================================
def extract_transcript(link):
    try:
        loader = YoutubeLoader.from_youtube_url(link, language=['en', 'hi'], add_video_info=False)
        docs = loader.load()
        if not docs:
            raise ValueError("No transcript available for this video.")
        return docs[0].page_content
    except Exception as e:
        raise RuntimeError(f"Failed to fetch YouTube data: {str(e)}")

def get_text_chunks(text, chunk_size=5000, chunk_overlap=200):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ".", " ", ""],
    )
    return splitter.split_text(text)

def recursive_summarize(transcript_text: str) -> str:
    chunks = get_text_chunks(transcript_text)
    running_summary = ""
    
    instruction_prompt = """You are an expert technical content writer converting transcript fragments into structured documentation.
    
    Current Progress Summary:
    {summary}
    
    New Snippet to Integrate:
    {chunk}
    
    STRICT COMPLIANCE RULES:
    - IGNORE all channel promotions, like/subscribe requests, sponsorships, and intro notes.
    - FOCUS EXCLUSIVELY on technical details, logical concepts, and actionable insights.
    - Retain code logic structure if present. Return the updated summary.
    """
    
    for chunk in chunks:
        formatted_prompt = instruction_prompt.format(summary=running_summary, chunk=chunk)
        response = llm.invoke(formatted_prompt)
        running_summary = response.content
        
    return running_summary

# ==========================================
# 3. PROMPT CONFIGURATIONS & CHAINS
# ==========================================
system_writer = 'You are a Professional Article Writer specializing in writing technical content for Medium, LinkedIn, and tech blogs.'
human_writer = '''Transform this YouTube transcript into an engaging, professional first-person technical article. 
Use bold subheadings, numbered lists, code snippets, and copy-paste ready actionable items. End with a short summary.
Transcript Content: {transcript}'''

summarizer_prompt = ChatPromptTemplate.from_messages([
    ("system", system_writer),
    ("human", human_writer)
])

base_summarizer = {"transcript": RunnablePassthrough()} | summarizer_prompt | llm | StrOutputParser()
long_summarizer = RunnableLambda(recursive_summarize)

def estimate_transcript_length(transcript: str) -> bool:
    return len(transcript) >= 4000 

routing_branch = RunnableBranch(
    (RunnableLambda(estimate_transcript_length), long_summarizer),
    base_summarizer
)

system_dev = """You are a Senior Frontend Web Developer with 10+ years experience in HTML5, CSS3, and modern JavaScript (ES6+).
Generate COMPLETE, PRODUCTION-READY frontend code based on user requirements.

MANDATORY OUTPUT FORMAT:
--html--
[html code here]
--html--

--css--
[css code here]
--css--

--js--
[javascript code here]
--js--
"""

human_dev = '''Create a production-ready responsive article webpage matching the style of Medium and Dev.to.
Include a clean modern card-based layout, a dark/light theme toggle, smooth transitions, and optimization metrics.
CONTENT TO LOAD ONTO THE CANVAS: {article_content}'''

web_dev_template = ChatPromptTemplate.from_messages([
    ("system", system_dev),
    ("human", human_dev)
])

webpage_chain = {"article_content": RunnablePassthrough()} | web_dev_template | llm | StrOutputParser()

# ==========================================
# 4. STREAMLIT INTERACTION LAYERS
# ==========================================
st.title("🌐 YouTube to Webpage Engine")
st.write("Extract video data, outline a clean article structure, and bundle a ready-to-deploy zipped asset pipeline.")

video_url = st.text_input("Enter YouTube Video URL:", placeholder="Provide your youtube link here.....")

if st.button("Generate Digital Assets", type="primary"):
    if not video_url:
        st.warning("Please enter a valid link first.")
    else:
        try:
            with st.spinner("Step 1 of 3: Fetching and cleaning raw audio transcript arrays..."):
                raw_transcript = extract_transcript(video_url)
                st.success("Transcript extracted successfully.")
                
            with st.spinner("Step 2 of 3: Segmenting text data and compiling structured article summaries..."):
                structured_article = routing_branch.invoke(raw_transcript)
                
                with st.expander("📄 Review Generated Article Content"):
                    st.markdown(structured_article)
                    
            with st.spinner("Step 3 of 3: Compiling responsive frontend components (--html--, --css--, --js--)..."):
                raw_web_code = webpage_chain.invoke(structured_article)
                
                try:
                    html_code = raw_web_code.split('--html--')[1].strip()
                    css_code = raw_web_code.split('--css--')[1].strip()
                    js_code = raw_web_code.split('--js--')[1].strip()
                except IndexError:
                    st.error("The model response structure dropped the code delimiter boundaries. Retrying ingestion helps.")
                    st.stop()
                    
            # 5. PACKAGING PIPELINES
            zip_filename = "website_package.zip"
            with zipfile.ZipFile(zip_filename, 'w') as zip_file:
                zip_file.writestr('index.html', html_code)
                zip_file.writestr('style.css', css_code)
                zip_file.writestr('script.js', js_code)
                
            st.balloons()
            st.success("Web Assets compiled successfully! Review or download your build packages below.")
            

            # This code is to mention the HTML,CSS,JS Webpage-Code on screen.

            # tab1, tab2, tab3 = st.tabs(["HTML Source", "CSS Styling", "JS Logic"])
            # with tab1:
            #     st.code(html_code, language="html")
            # with tab2:
            #     st.code(css_code, language="css")
            # with tab3:
            #     st.code(js_code, language="javascript")
                
            with open(zip_filename, "rb") as fp:
                st.download_button(
                    label="💾 Download Ready-to-Deploy ZIP",
                    data=fp,
                    file_name=zip_filename,
                    mime="application/zip",
                    use_container_width=True
                )
                
        except Exception as err:
            st.error(f"Execution Error Intercepted: {str(err)}")