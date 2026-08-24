import os
import json
import time
import streamlit as st
from pdf_loader import load_and_chunk_pdf
from vector_db import VectorStoreManager
from agent import RAGAgent
from dotenv import load_dotenv

load_dotenv()

# Page Configuration for a clean, wide SaaS dashboard layout
st.set_page_config(
    page_title="ProtoPapers Automation Architect",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling Injection for a Sleek Modern Tech Aesthetic
st.markdown("""
    <style>
        /* Main background & font smoothing */
        .main {
            background-color: #FAFAFC;
        }
        /* Style headers */
        h1, h2, h3 {
            letter-spacing: -0.025em;
        }
        /* Custom card styling wrappers */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        .stTabs [data-baseweb="tab"] {
            background-color: #F1F5F9;
            border-radius: 6px;
            padding: 8px 16px;
            font-weight: 500;
        }
        .stTabs [aria-selected="true"] {
            background-color: #2563EB !important;
            color: white !important;
        }
    </style>
""", unsafe_allow_html=True)

def render_mermaid(code: str):
    st.markdown("### 📊 Workflow Graph Structure")
    st.code(code, language="text")
    st.info("💡 You can copy this flow structure directly into n8n, Zapier, or any Mermaid live editor.")

def build_n8n_json(bp: dict) -> dict:
    """Dynamically translates the ProtoPapers blueprint into a native n8n-importable JSON schema."""
    n8n_nodes = []
    connections = {}
    
    x_pos = 240
    y_pos = 300
    
    for i, node in enumerate(bp["nodes"]):
        node_name_clean = f"Node {node['node_number']}: {node['node_name']}"
        
        n8n_type = "n8n-nodes-base.code"
        if "Trigger" in node['node_type']:
            n8n_type = "n8n-nodes-base.webhook"
        elif "AI" in node['node_type']:
            n8n_type = "n8n-nodes-base.openAi"
        elif "Output" in node['node_type'] or "Action" in node['node_type']:
            n8n_type = "n8n-nodes-base.httpRequest"

        n8n_node = {
            "parameters": {
                "notice": node['plain_english_purpose'],
                "jsCode": f"// Input Format: {node['input_data_format']}\n// Output Format: {node['output_data_format']}\n// Config: {node['configuration_parameters']}\nreturn $input.all();"
            },
            "id": f"node-uuid-{node['node_number']}",
            "name": node_name_clean,
            "type": n8n_type,
            "typeVersion": 2,
            "position": [x_pos, y_pos]
        }
        n8n_nodes.append(n8n_node)
        
        if i < len(bp["nodes"]) - 1:
            next_node_name = f"Node {bp['nodes'][i+1]['node_number']}: {bp['nodes'][i+1]['node_name']}"
            connections[node_name_clean] = {
                "main": [
                    [
                        {
                            "node": next_node_name,
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            }

        x_pos += 280

    return {
        "name": bp["paper_title"],
        "nodes": n8n_nodes,
        "connections": connections,
        "active": False,
        "settings": {"executionOrder": "v1"},
        "versionId": "protopapers-auto-v1",
        "meta": {
            "templateCredsSetupCompleted": True,
            "instanceId": "protopapers-engine"
        }
    }

# ================= SIDEBAR WORKSPACE CONTROL =================
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/artificial-intelligence.png", width=64)
    st.title("ProtoPapers")
    st.caption("Research-to-Workflow Engine")
    st.markdown("---")
    
    uploaded_file = st.file_uploader("📂 Upload Research PDF", type="pdf")
    
    st.markdown("---")
    st.markdown("### ⚙️ Engine Status")
    if "blueprint" in st.session_state:
        st.success("Pipeline Ready ✅")
    else:
        st.info("Awaiting PDF Upload...")
    
    st.markdown("---")
    st.markdown("<p style='font-size:12px; color:gray;'>Built for CMU AI & Innovations Portfolio</p>", unsafe_allow_html=True)

# ================= MAIN HERO SECTION =================
st.title("⚡ ProtoPapers: Research-to-Workflow Architect")
st.markdown("Transform messy academic research papers into native n8n pipelines, executable algorithms, and interactive RAG insights.")

if uploaded_file:
    file_key = f"uploaded_{uploaded_file.name}_{uploaded_file.size}"
    
    if st.session_state.get("current_file_key") != file_key:
        st.session_state["current_file_key"] = file_key
        for key in ["blueprint", "vector_store", "messages"]:
            if key in st.session_state:
                del st.session_state[key]

        with open("temp.pdf", "wb") as f:
            f.write(uploaded_file.getbuffer())

        with st.spinner("📂 Step 1/2: Indexing research paper into local vector store..."):
            chunks = load_and_chunk_pdf("temp.pdf")
            vector_store = VectorStoreManager()
            vector_store.add_chunks(chunks)
            st.session_state["vector_store"] = vector_store

        with st.spinner("🤖 Step 2/2: Generating automation workflow, nodes, and code via Gemini..."):
            try:
                rag_agent = RAGAgent(st.session_state["vector_store"])
                raw_json = rag_agent.generate_blueprint()
                bp_dict = json.loads(raw_json)

                bp_dict["n8n_workflow_payload"] = build_n8n_json(bp_dict)
                st.session_state["blueprint"] = bp_dict
            except Exception as error:
                st.error(f"Could not generate the workflow: {error}")

else:
    with st.container(border=True):
        st.info("👆 Get started by uploading a research PDF paper using the sidebar control panel on the left.")

# ================= DASHBOARD WORKSPACE =================
if "blueprint" in st.session_state:
    bp = st.session_state["blueprint"]
    
    st.markdown("---")
    st.header(f"📄 {bp['paper_title']}")

    # Metrics Row
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Workflow Nodes", len(bp["nodes"]))
    m2.metric("Execution Engine Status", "Active 🟢")
    m3.metric("Schema Compatibility", "n8n v2 / Native")

    # SaaS Card Containers for Overview
    col_a, col_b = st.columns(2)
    with col_a:
        with st.container(border=True):
            st.markdown("### 🎯 Problem Statement")
            st.write(bp['problem_statement'])
    with col_b:
        with st.container(border=True):
            st.markdown("### 🔄 Workflow Overview")
            st.write(bp['workflow_overview'])

    st.markdown("<br>", unsafe_allow_html=True)

    # Clean Tabs Layout
    tab_map, tab_nodes, tab_master, tab_run, tab_chat, tab_translate, tab_refine = st.tabs([
        "🗺️ Visual Pipeline", 
        "⚙️ Automation Nodes", 
        "📋 n8n Schema & Import",
        "🚀 Live Execution Engine",
        "💬 RAG PDF Chatbot",
        "🌐 Universal Translator",
        "✍️ Workflow Refinement"
    ])

    with tab_map:
        st.subheader("Data Flow Automation Diagram")
        mermaid_code = "graph TD\n"
        for node in bp["nodes"]:
            safe_title = "".join(c for c in node['node_name'] if c.isalnum() or c.isspace()).strip()
            mermaid_code += f"    Node{node['node_number']}[Node {node['node_number']}: {safe_title}]\n"
            if node['node_number'] < len(bp["nodes"]):
                mermaid_code += f"    Node{node['node_number']} --> Node{node['node_number'] + 1}\n"
        render_mermaid(mermaid_code)

    with tab_nodes:
        st.subheader("Step-by-Step Node Configuration")
        for node in bp["nodes"]:
            with st.expander(f"Node {node['node_number']}: {node['node_name']} [{node['node_type']}]", expanded=False):
                st.markdown(f"💡 **Purpose:** {node['plain_english_purpose']}")
                c1, c2 = st.columns(2)
                with c1:
                    st.write(f"📥 **Input Format:** `{node['input_data_format']}`")
                with c2:
                    st.write(f"📤 **Output Format:** `{node['output_data_format']}`")
                st.write(f"🛠️ **Recommended Tools:** `{', '.join(node['recommended_integration_tools'])}`")
                st.markdown(f"⚙️ **Configuration Setup:** {node['configuration_parameters']}")

    with tab_master:
        st.subheader("🤖 Native n8n Workflow Schema & Import File")
        st.write("This JSON file is formatted according to n8n's workflow architecture specifications. You can download it and use **'Import from File'** directly in your n8n workspace canvas:")
        
        st.code(json.dumps(bp["n8n_workflow_payload"], indent=2), language="json")
        
        st.download_button(
            "📥 Download Native n8n Workflow JSON (.json)", 
            data=json.dumps(bp["n8n_workflow_payload"], indent=2), 
            file_name="n8n_workflow_import.json", 
            mime="application/json"
        )

    with tab_run:
        st.subheader("Interactive Logic Execution Engine")
        st.write("Execute the actual custom Python algorithm generated from this research paper on your uploaded PDF:")

        with st.expander("🔍 View Generated Python Algorithm Code"):
            st.code(bp["executable_python_logic"], language="python")

        if st.button("▶️ Run Actual Paper Logic on PDF", type="primary"):
            with st.spinner("Executing custom algorithm against uploaded paper text..."):
                try:
                    from pypdf import PdfReader
                    import re
                    import math
                    import statistics
                    import json
                    import collections
                    
                    reader = PdfReader("temp.pdf")
                    raw_text = "".join([page.extract_text() for page in reader.pages if page.extract_text()])

                    local_scope = {
                        "re": re,
                        "math": math,
                        "statistics": statistics,
                        "json": json,
                        "collections": collections
                    }
                    
                    exec(bp["executable_python_logic"], globals(), local_scope)

                    if "run_paper_logic" in local_scope:
                        result = local_scope["run_paper_logic"](raw_text)
                        st.success("✅ Paper logic executed successfully!")
                        st.json(result)
                        
                        st.download_button(
                            "📥 Download Execution Results (.json)",
                            data=json.dumps(result, indent=2),
                            file_name="execution_results.json",
                            mime="application/json"
                        )
                    else:
                        st.error("The generated code did not expose the required 'run_paper_logic' function.")
                except Exception as e:
                    st.error(f"Execution Error: {str(e)}")

    with tab_chat:
        st.subheader("💬 Chat with Research Paper (In-Built RAG Assistant)")
        st.write("Ask targeted questions about the paper's methodology, findings, datasets, or formulas.")
        
        if "messages" not in st.session_state:
            st.session_state.messages = []

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input("Ask a question about the uploaded paper..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Searching document context..."):
                    rag_agent = RAGAgent(st.session_state["vector_store"])
                    answer = rag_agent.answer_question(prompt)
                    st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})

    with tab_translate:
        st.subheader("🌐 Universal Ecosystem Translator")
        st.write("Translate the current workflow pipeline into alternative target platforms.")
        
        target_platform = st.selectbox("Select Target Ecosystem", ["LangGraph Orchestration", "Zapier Webhook Flow", "Make.com Scenario"])
        if st.button("Translate Workflow"):
            with st.spinner(f"Translating pipeline schema into {target_platform}..."):
                rag_agent = RAGAgent(st.session_state["vector_store"])
                translation = rag_agent.translate_workflow(json.dumps(bp["n8n_workflow_payload"]), target_platform)
                st.markdown(f"### {target_platform} Translation:")
                st.markdown(translation)

    with tab_refine:
        st.subheader("✍️ User-in-the-Loop Workflow Refinement")
        st.write("Modify the existing workflow schema dynamically by submitting natural language change requests.")
        
        user_feedback = st.text_area("Describe your modification request (e.g., 'Add a Slack notification node after Node 2'):")
        if st.button("Apply Modifications"):
            if user_feedback:
                with st.spinner("Refining workflow schema..."):
                    rag_agent = RAGAgent(st.session_state["vector_store"])
                    updated_json_str = rag_agent.refine_workflow(json.dumps(bp["n8n_workflow_payload"], indent=2), user_feedback)
                    st.markdown("### Refined Workflow Result:")
                    st.code(updated_json_str, language="json")
            else:
                st.warning("Please enter a modification request.")