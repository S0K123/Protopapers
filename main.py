import os
import json
from pdf_loader import load_and_chunk_pdf
from vector_db import VectorStoreManager
from agent import RAGAgent
from dotenv import load_dotenv

load_dotenv()

def build_n8n_json(bp: dict) -> dict:
    n8n_nodes = []
    connections = {}
    x_pos, y_pos = 240, 300
    
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
                "jsCode": f"// Input: {node['input_data_format']}\nreturn $input.all();"
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
                "main": [[[ {"node": next_node_name, "type": "main", "index": 0} ]]]
            }
        x_pos += 280

    return {
        "name": bp["paper_title"],
        "nodes": n8n_nodes,
        "connections": connections,
        "active": False,
        "settings": {"executionOrder": "v1"},
        "versionId": "protopapers-auto-v1",
        "meta": {"templateCredsSetupCompleted": True, "instanceId": "protopapers-engine"}
    }

def main():
    print("--- STARTING PROTOPAPERS AUTOMATION WORKFLOW SYSTEM ---", flush=True)
    pdf_file = "sample.pdf"

    if not os.path.exists(pdf_file):
        print(f"Error: Could not find '{pdf_file}'", flush=True)
        return

    print("Step 1/3: Reading and chunking PDF...", flush=True)
    chunks = load_and_chunk_pdf(pdf_file)

    print("Step 2/3: Embedding chunks into ChromaDB...", flush=True)
    vector_store = VectorStoreManager()
    vector_store.add_chunks(chunks)

    print("Step 3/3: Generating Workflow Blueprint, n8n Schema, and Executable Logic...\n", flush=True)
    rag_agent = RAGAgent(vector_store)
    
    raw_json = rag_agent.generate_blueprint()
    blueprint = json.loads(raw_json)
    blueprint["n8n_workflow_payload"] = build_n8n_json(blueprint)

    # Save outputs
    with open("n8n_workflow_import.json", "w") as f:
        json.dump(blueprint["n8n_workflow_payload"], f, indent=2)
    
    with open("generated_paper_logic.py", "w") as f:
        f.write(blueprint["executable_python_logic"])

    print("\n✅ Native n8n import schema saved to 'n8n_workflow_import.json'!")
    print("✅ Executable Python logic saved to 'generated_paper_logic.py'!")

if __name__ == "__main__":
    main()