# Youtube_Video_to_Webpage_Article


🌐 YouTube to Production Webpage Engine
An automated web application that extracts YouTube transcripts, processes them into high-quality technical articles, and instantly generates a complete, downloadable frontend webpage code bundle (HTML, CSS, JS).

🎯 Main Functions
Smart Transcript Ingestion: Downloads raw subtitle data directly from a YouTube link.

Dynamic Length Routing: Uses conditional routing logic to automatically process short transcripts in one fast pass, or chunk large videos recursively to handle long technical tutorials.

Text-to-Code Synthesis: Compiles the structured article into a mobile-first, responsive dashboard layout with a built-in dark/light theme toggle.

Automated Packaging: Instantly previews the source code files and bundles them into a ready-to-deploy .zip package for one-click downloading.

🛠️ Technologies Used
Core Frameworks & Tools
Streamlit: Powers the frontend web interface, reactive widgets, and file downloading systems.

LangChain (LCEL): Orchestrates the conditional pipeline blocks using RunnableBranch, RunnablePassthrough, and RunnableLambda.

Python-Dotenv: Handles secure local environment variable loading for keys.

Intelligence & Models
Gemini 2.5 Flash: Serves as the primary engine for transcript optimization, summarization, and frontend code generation.

Libraries & Built-ins
langchain-community (YoutubeLoader): Extracts raw text transcripts directly from standard YouTube URLs.

langchain-text-splitters (RecursiveCharacterTextSplitter): Breaks massive text volumes down safely using separator priority boundaries.

zipfile (Python Native): Dynamically bundles code strings into a single compression package right in system memory.

💻 Quick Start
Set up Environment Key: Create a .env file in your root folder:

Plaintext
GOOGLE_API_KEY=your_gemini_api_key_here
Launch App: Run the application script from your active environment terminal:

Bash
streamlit run app.py