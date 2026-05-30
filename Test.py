# import os
# from dotenv import load_dotenv

# from langchain_community.document_loaders import YoutubeLoader

# from langchain_openai import ChatOpenAI

# from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
# from langchain_core.runnables import chain, RunnableBranch, RunnablePassthrough, RunnableLambda
# from langchain_core.output_parsers import StrOutputParser
# from langchain_text_splitters import RecursiveCharacterTextSplitter

# from langchain.agents import create_agent
# from langchain.agents.middleware import SummarizationMiddleware

# from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain_groq import ChatGroq

# import zipfile

# load_dotenv()

# # os.environ['OPENAI_API_KEY'] = os.getenv('openai_key')
# os.environ['GOOGLE_API_KEY'] = os.getenv('GOOGLE_API_KEY')
# os.environ['GROQ_API_KEY'] = os.getenv('GROQ_API_KEY')

# # Model
# # llm = ChatOpenAI(model='gpt-5-nano')
# llm = ChatGoogleGenerativeAI(model = 'gemini-2.5-flash')
# llm_groq = ChatGroq(model = "qwen/qwen3-32b")

# system_message = 'You are an Professional Article Writer specializing in writing articles for Medium, LinkedIn, and tech blogs.'

# human_message = '''
# Transform YouTube transcript into **engaging, professional articles** with:

# **CRITICAL INSTRUCTIONS**:
# - **IGNORE** Introductionary notes like welcome, In this video
# - **IGNORE** all channel names, "subscribe", "like", "comment", "follow", "check description" 
# - **IGNORE** marketing phrases: "my course", "my discord", "affiliate links", "sponsors"
# - **FOCUS ONLY** on technical content, code, tutorials, actionable insights

# **MANDATORY ARTICLE STRUCTURE** (exact Medium/LinkedIn format):
# - Write in **first-person professional tone** 
# - Use **bold subheadings**, **numbered lists**.
# - Include **code snippets** for technical videos
# - Make **Actionable Steps** copy-paste ready
# - End with **short summary of the article**

# Here is the: {transcript}
# '''
# summarizer_prompt = ChatPromptTemplate.from_messages([
#     SystemMessagePromptTemplate.from_template(system_message),
#     HumanMessagePromptTemplate.from_template(human_message)
# ])

# # Transcript tool to extract transcript from youtube video.
# def extract_transcript(link: str) -> str:
#   """
#   Extract YouTube transcript using YoutubeLoader
#   Input: YouTube URL → Output: Transcript text
#   """
#   loader = YoutubeLoader.from_youtube_url(link)
#   docs = loader.load()
#   return docs[0].page_content

# # BASE SUMMARIZER (short transcripts < 1000 tokens)
# # Here, We can use the StrOutputParser but not in agentic_setup using middleware.
# base_summarizer = ( RunnablePassthrough() | RunnableLambda(extract_transcript) | summarizer_prompt | llm  | StrOutputParser() )




# system_prompt = """
# You are a recursive summarization engine.

# Your job:
# - Continuously summarize incoming content
# - Maintain a concise but complete running summary
# - When content grows large, compress older information
# - Preserve key technical details, concepts, and relationships
# - Output ONLY the updated summary

# Think of this as:
# A rolling summary that improves as more text arrives and prepares a production ready article.
# """

# def get_text_chunks(text, chunk_size=5000, chunk_overlap=200):
#     splitter = RecursiveCharacterTextSplitter(
#         chunk_size = chunk_size,
#         chunk_overlap = chunk_overlap,
#         separators=["\n\n", "\n", ".", " ", ""],  # priority order
#     )
#     return splitter.split_text(text)

# # Agent setup
# agent = create_agent(
#     model=llm,
#     tools=[],   # NO tools - summarization ONLY
#     system_prompt = system_message,
#     middleware=[
#         SummarizationMiddleware(
#             model=llm,
#             trigger=("tokens", 1000),     # Summarize when conversation hits 1000 tokens
#             keep=("tokens", 200),        # Preserve last 200 tokens verbatim
#         ),
#     ],
# )
# agent

# def recursive_summarize(text, agent=agent):
#     chunks = get_text_chunks(text)
#     running_summary = ""

#     for chunk in chunks:
#         response = agent.invoke({
#             "messages": [
#                 {
#                     "role": "user",
#                     "content": f"""
# You are summarizing technical content.

# Current summary:
# {running_summary}

# New content:
# {chunk}

# While summarizing teh text in the form of article strictly follow
# **CRITICAL INSTRUCTIONS**:
# - **IGNORE** Introductionary notes like welcome, In this video
# - **IGNORE** all channel names, "subscribe", "like", "comment", "follow", "check description"
# - **IGNORE** marketing phrases: "my course", "my discord", "affiliate links", "sponsors"
# - **FOCUS ONLY** on technical content, code, tutorials, actionable insights

# **MANDATORY ARTICLE STRUCTURE** (exact Medium/LinkedIn format):
# - Write in **first-person professional tone**
# - Use **bold subheadings**, **numbered lists**.
# - Include **code snippets** for technical videos
# - Make **Actionable Steps** copy-paste ready
# - End with **short summary of the article**
# """
#                 }
#             ]
#         })

#         running_summary = response["messages"][-1].content

#     return running_summary

# long_summarizer = RunnablePassthrough() | RunnableLambda(extract_transcript) | RunnableLambda(recursive_summarize)
# long_summarizer

# # RUNNABLE BRANCH - Routes automatically based on transcript length
# def estimate_transcript_length(link: str) -> bool:
#     """Quick length estimator (characters → tokens)."""
#     transcript = extract_transcript(link)
#     return len(transcript) >= 1000  # Returns True for long transcripts


# system_message = """You are a Senior Frontend Web Developer with 10+ years experience in HTML5, CSS3, and modern JavaScript (ES6+).

# Your task: Generate COMPLETE, PRODUCTION-READY frontend code based on user requirements.

# **MANDATORY OUTPUT FORMAT** (exact delimiters):
# --html--
# [html code here]
# --html--

# --css--
# [css code here]
# --css--

# --js--
# [java script code here]
# --js--
# """

# human_message = '''
# Create a **production-ready article webpages** in the style of **Medium, Dev.to, Hashnode, and Substack**.

# **MANDATORY REQUIREMENTS**:
# - **Mobile-first responsive design** (perfect on all devices)
# - **Clean, modern typography** (system fonts + readability first)
# - **Medium-like article layout** with card-based design
# - **Dark/light theme toggle**
# - **Smooth animations** and **scroll effects**
# - **SEO optimized** with proper meta tags
# - **Accessibility compliant** (ARIA labels, keyboard navigation)

# **CONTENT TO USE**: {article_content}
# '''

# web_dev_template = ChatPromptTemplate.from_messages([system_message, human_message]) # Prompt_template
# webpage_chain = web_dev_template | llm | StrOutputParser()

# smart_summarizer = RunnableBranch(
#     # Condition: if transcript ≥ 1000 words → long handler
#     (RunnableLambda(estimate_transcript_length), long_summarizer),
    
#     # Else: base summarizer for short transcripts
#     base_summarizer) | web_dev_template | llm | StrOutputParser()

# article = smart_summarizer.invoke("https://www.youtube.com/watch?v=-46UkLPf9h0")

# with open('index.html', 'w') as file:
#         file.write(article.split('--html--')[1])

# with open('style.css', 'w') as file:
#     file.write(article.split('--css--')[1])

# with open('script.js', 'w') as file:
#     file.write(article.split('--js--')[1])

# with zipfile.ZipFile('website.zip', 'w') as zip:
#     zip.write('index.html')
#     zip.write('style.css')
#     zip.write('script.js')




# Streamlit code.01



# import os
# import zipfile
# import streamlit as st
# from dotenv import load_dotenv

# from langchain_community.document_loaders import YoutubeLoader
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_core.runnables import RunnableBranch, RunnablePassthrough, RunnableLambda
# from langchain_core.output_parsers import StrOutputParser
# from langchain_text_splitters import RecursiveCharacterTextSplitter
# from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain_groq import ChatGroq

# # ==========================================
# # 1. INITIALIZATION & STYLES
# # ==========================================
# st.set_page_config(page_title="Video to Web Engine", page_icon="🌐")
# load_dotenv()

# # Guardrails for API Keys
# if not os.getenv("GOOGLE_API_KEY"):
#     st.error("Missing GOOGLE_API_KEY in environment variables or .env file.")
#     st.stop()

# # For Groq(Alternative Model):
# if not os.getenv("GROQ_API_KEY"):
#     st.error("Missing GROQ_API_KEY in environment variables or .env file.")
#     st.stop()   

# # Cache models to save computational memory
# @st.cache_resource
# def init_models():
#     llm = ChatGoogleGenerativeAI(model='gemini-2.5-flash', temperature=0.2)
#     return llm

# # For Groq(Alternative Model):
# @st.cache_resource
# def init_models():
#     llm_groq = ChatGroq(model='qwen/qwen3-32b', temperature=0.2)
#     return llm_groq

# llm = init_models()
# llm_groq = init_models()

# # ==========================================
# # 2.TRANSCRIPT LOGIC
# # ==========================================
# def extract_transcript(link):
#     try:
#         loader = YoutubeLoader.from_youtube_url(link, language=['en', 'hi'], add_video_info=False)
#         docs = loader.load()
#         if not docs:
#             raise ValueError("No transcript available for this video.")
#         return docs[0].page_content
#     except Exception as e:
#         raise RuntimeError(f"Failed to fetch YouTube data: {str(e)}")

# def get_text_chunks(text, chunk_size=5000, chunk_overlap=200):
#     splitter = RecursiveCharacterTextSplitter(
#         chunk_size=chunk_size,
#         chunk_overlap=chunk_overlap,
#         separators=["\n\n", "\n", ".", " ", ""],
#     )
#     return splitter.split_text(text)

# def recursive_summarize(transcript_text: str) -> str:
#     chunks = get_text_chunks(transcript_text)
#     running_summary = ""
    
#     instruction_prompt = """You are an expert technical content writer converting transcript fragments into structured documentation.
    
#     Current Progress Summary:
#     {summary}
    
#     New Snippet to Integrate:
#     {chunk}
    
#     STRICT COMPLIANCE RULES:
#     - IGNORE all channel promotions, like/subscribe requests, sponsorships, and intro notes.
#     - FOCUS EXCLUSIVELY on technical details, logical concepts, and actionable insights.
#     - Retain code logic structure if present. Return the updated summary.
#     """
    
#     for i, chunk in enumerate(chunks):
#         formatted_prompt = instruction_prompt.format(summary=running_summary, chunk=chunk)
#         formatted_prompt = instruction_prompt.invoke(summary=running_summary, chunk=chunk)
#         # Using a direct invocation interface for reliable streaming/loop execution 
#         response = llm.invoke(formatted_prompt)
#         running_summary = response.content
        
#     return running_summary

# # ==========================================
# # 3. PROMPT CONFIGURATIONS & CHAINS
# # ==========================================
# system_writer = 'You are a Professional Article Writer specializing in writing technical content for Medium, LinkedIn, and tech blogs.'
# human_writer = '''Transform this YouTube transcript into an engaging, professional first-person technical article. 
# Use bold subheadings, numbered lists, code snippets, and copy-paste ready actionable items. End with a short summary.
# Transcript Content: {transcript}'''

# summarizer_prompt = ChatPromptTemplate.from_messages([
#     ("system", system_writer),
#     ("human", human_writer)
# ])

# # Base pipeline paths mapped manually to match strict schema boundaries
# base_summarizer = {"transcript": RunnablePassthrough()} | summarizer_prompt | llm | StrOutputParser()
# long_summarizer = RunnableLambda(recursive_summarize)

# def estimate_transcript_length(transcript: str) -> bool:
#     # Safely routing by counting character size metrics
#     return len(transcript) >= 4000 

# # Router maps the raw text string input to clean summaries
# routing_branch = RunnableBranch(
#     (RunnableLambda(estimate_transcript_length), long_summarizer),
#     base_summarizer
# )

# # Web Development Generator Configuration
# system_dev = """You are a Senior Frontend Web Developer with 10+ years experience in HTML5, CSS3, and modern JavaScript (ES6+).
# Generate COMPLETE, PRODUCTION-READY frontend code based on user requirements.

# MANDATORY OUTPUT FORMAT:
# --html--
# [html code here]
# --html--

# --css--
# [css code here]
# --css--

# --js--
# [javascript code here]
# --js--
# """

# human_dev = '''Create a production-ready responsive article webpage matching the style of Medium and Dev.to.
# Include a clean modern card-based layout, a dark/light theme toggle, smooth transitions, and optimization metrics.
# CONTENT TO LOAD ONTO THE CANVAS: {article_content}'''

# web_dev_template = ChatPromptTemplate.from_messages([
#     ("system", system_dev),
#     ("human", human_dev)
# ])

# webpage_chain = {"article_content": RunnablePassthrough()} | web_dev_template | llm | StrOutputParser()

# # ==========================================
# # 4. STREAMLIT INTERACTION LAYERS
# # ==========================================
# st.title("🌐 YouTube to Production Webpage Engine")
# st.write("Extract video data, outline a clean article structure, and bundle a ready-to-deploy zipped asset pipeline.")

# video_url = st.text_input("Enter YouTube Video URL:", placeholder="https://www.youtube.com/watch?v=...")

# if st.button("Generate Digital Assets", type="primary"):
#     if not video_url:
#         st.warning("Please enter a valid link first.")
#     else:
#         try:
#             with st.spinner("Step 1 of 3: Fetching and cleaning raw audio transcript arrays..."):
#                 raw_transcript = extract_transcript(video_url)
#                 st.success("Transcript extracted successfully.")
                
#             with st.spinner("Step 2 of 3: Segmenting text data and compiling structural article summaries..."):
#                 # Run the text through our LCEL routing logic
#                 structured_article = routing_branch.invoke(raw_transcript)
                
#                 with st.expander("📄 Review Generated Article Content"):
#                     st.markdown(structured_article)
                    
#             with st.spinner("Step 3 of 3: Compiling responsive frontend components (--html--, --css--, --js--)..."):
#                 raw_web_code = webpage_chain.invoke(structured_article)
                
#                 # Extract asset bundles via tag validation
#                 try:
#                     html_code = raw_web_code.split('--html--')[1].strip()
#                     css_code = raw_web_code.split('--css--')[1].strip()
#                     js_code = raw_web_code.split('--js--')[1].strip()
#                 except IndexError:
#                     st.error("The model response structure dropped the code delimiter boundaries. Retrying ingestion helps.")
#                     st.stop()
                    
#             # 5. PACKAGING PIPELINES
#             zip_filename = "website_package.zip"
#             with zipfile.ZipFile(zip_filename, 'w') as zip_file:
#                 zip_file.writestr('index.html', html_code)
#                 zip_file.writestr('style.css', css_code)
#                 zip_file.writestr('script.js', js_code)
                
#             st.balloons()
#             st.success("Web Assets compiled successfully! Review or download your build packages below.")
            
#             # Interactive UI Split Layout for Preview
#             tab1, tab2, tab3 = st.tabs(["HTML Source", "CSS Styling", "JS Logic"])
#             with tab1:
#                 st.code(html_code, language="html")
#             with tab2:
#                 st.code(css_code, language="css")
#             with tab3:
#                 st.code(js_code, language="javascript")
                
#             # Direct binary injection pipeline down to local machine
#             with open(zip_filename, "rb") as fp:
#                 st.download_button(
#                     label="💾 Download Ready-to-Deploy ZIP",
#                     data=fp,
#                     file_name=zip_filename,
#                     mime="application/zip",
#                     use_container_width=True
#                 )
                
#         except Exception as err:
#             st.error(f"Execution Error Intercepted: {str(err)}")




# streamlit code -02

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
# 1. INITIALIZATION & STYLES
# ==========================================
st.set_page_config(page_title="Video to Web Engine", page_icon="🌐", layout="wide")
load_dotenv()

# Guardrails for API Keys
if not os.getenv("GOOGLE_API_KEY"):
    st.error("Missing GOOGLE_API_KEY in environment variables or .env file.")
    st.stop()

# Cache models to save computational memory
@st.cache_resource
def init_models():
    llm = ChatGoogleGenerativeAI(model='gemini-2.5-flash', temperature=0.2)
    return llm

llm = init_models()

# ==========================================
# 2. CORE TRANSCRIPT ENGINE LOGIC
# ==========================================
def extract_transcript(link: str) -> str:
    try:
        loader = YoutubeLoader.from_youtube_url(link, add_video_info=False)
        docs = loader.load()
        if not docs:
            raise ValueError("No transcript available for this video.")
        return docs[0].page_content
    except Exception as e:
        raise RuntimeError(f"Failed to fetch YouTube data: {str(e)}")

def get_text_chunks(text, chunk_size=6000, chunk_overlap=300):
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

# Base pipeline paths mapped manually to match strict schema boundaries
base_summarizer = {"transcript": RunnablePassthrough()} | summarizer_prompt | llm | StrOutputParser()
long_summarizer = RunnableLambda(recursive_summarize)

def estimate_transcript_length(transcript: str) -> bool:
    return len(transcript) >= 4000 

# Router maps the raw text string input to clean summaries
routing_branch = RunnableBranch(
    (RunnableLambda(estimate_transcript_length), long_summarizer),
    base_summarizer
)

# Web Development Generator Configuration
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

# --- AESTHETIC SIDEBAR CONSTRUCTION ---
with st.sidebar:
    st.markdown("## 🛠️ System Architecture")
    st.write("This engine leverages an advanced orchestration layer to process audio and script assets.")
    
    st.markdown("---")
    
    st.markdown("### 🧬 Orchestration & Core")
    st.markdown("""
    * **LangChain (LCEL):** Conditional routing branch & state pipelines
    * **Python-Dotenv:** Encrypted system variable ingestion
    """)
    
    st.markdown("### 🤖 Intelligence Layer")
    st.markdown("""
    * **Gemini 2.5 Flash:** High-speed token evaluation & synthesis
    * **Llama 3.1 (via Groq):** Low-latency content transformations
    """)
    
    st.markdown("### 🎨 Frontend Canvas")
    st.markdown("""
    * **Streamlit Framework:** Reactive UI widget rendering 
    * **HTML5 / CSS3 / ES6+:** Generated production-ready templates
    """)
    
    st.markdown("---")
    st.caption("Designed for fast, decoupled AI text-to-code compilation. 🚀")

# --- MAIN APPLICATION CANVAS ---
st.title("🌐 YouTube to Production Webpage Engine")
st.write("Extract video data, outline a clean article structure, and bundle a ready-to-deploy zipped asset pipeline.")

video_url = st.text_input("Enter YouTube Video URL:", placeholder="https://www.youtube.com/watch?v=...")

if st.button("Generate Digital Assets", type="primary"):
    if not video_url:
        st.warning("Please enter a valid link first.")
    else:
        try:
            with st.spinner("Step 1 of 3: Fetching and cleaning raw audio transcript arrays..."):
                raw_transcript = extract_transcript(video_url)
                st.success("Transcript extracted successfully.")
                
            with st.spinner("Step 2 of 3: Segmenting text data and compiling structural article summaries..."):
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
            
            # Interactive UI Split Layout for Preview
            tab1, tab2, tab3 = st.tabs(["HTML Source", "CSS Styling", "JS Logic"])
            with tab1:
                st.code(html_code, language="html")
            with tab2:
                st.code(css_code, language="css")
            with tab3:
                st.code(js_code, language="javascript")
                
            # Direct binary injection pipeline down to local machine
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



# My code should have dark mode option , along with a simple sidebar and no need to generate code on screen(or make it collapseable.)