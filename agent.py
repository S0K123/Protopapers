import json
import time
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from vector_db import VectorStoreManager


class WorkflowNode(BaseModel):
    node_number: int
    node_name: str = Field(description="Name of the automation or workflow step")
    node_type: str = Field(description="Type of node: 'Trigger', 'Data Transformation', 'AI Processing', or 'Action/Output'")
    plain_english_purpose: str = Field(description="Simple 1-2 sentence real-world explanation")
    input_data_format: str = Field(description="What goes into this node")
    output_data_format: str = Field(description="What comes out of this node")
    recommended_integration_tools: list[str] = Field(description="Tools/APIs to use")
    configuration_parameters: str = Field(description="Exact settings or logic parameters required")


class ProtoPapersWorkflowBlueprintSchema(BaseModel):
    paper_title: str
    problem_statement: str = Field(description="The core problem or research gap addressed by the paper")
    workflow_overview: str = Field(description="Executive summary of the end-to-end automated pipeline")
    nodes: list[WorkflowNode]


class RAGAgent:
    def __init__(self, vector_store: VectorStoreManager):
        self.client = genai.Client()
        self.vector_store = vector_store

    def generate_blueprint(self) -> str:
        context = self.vector_store.search_similar(
            "problem statement methodology architecture pipeline implementation algorithm evaluation dataset model workflow step equations math formulas", 
            top_k=8
        )

        # Step 1: Generate the structural JSON workflow schema safely without code entanglement
        prompt_blueprint = f"""
        You are a workflow automation architect and senior quantitative developer. 
        Analyze the methodology and mathematical formulations of the research paper provided below and translate them into a valid, production-ready n8n workflow schema blueprint.

        Paper Context / Methodology Summary:
        {context}

        Instructions:
        1. Extract the core problem statement, workflow overview, and sequential workflow nodes (Data Ingestion, Data Transformation, AI Processing, Action/Output).
        """

        config_blueprint = types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=ProtoPapersWorkflowBlueprintSchema,
        )
        
        raw_blueprint_text = self._call_gemini(prompt_blueprint, config_blueprint)
        bp_dict = json.loads(raw_blueprint_text)

        # Step 2: Generate the executable Python algorithm code in a separate clean call
        prompt_code = f"""
        You are an expert Python developer and quantitative researcher. 
        Based on the following research paper context, write a clean, self-contained Python code snippet defining a function named `run_paper_logic(pdf_text: str) -> dict` that implements the core algorithm or data processing logic proposed in the paper.

        Paper Context:
        {context}

        Instructions:
        1. The python code must NEVER return an error for standard text inputs. Process text gracefully, extract key metrics or keywords, and return a dictionary result.
        2. You must explicitly include `import re` at the top of the code string.
        3. Return ONLY valid Python code inside standard markdown code blocks (```python ... ```). Do not include any other conversational filler.
        """
        
        raw_code_response = self._call_gemini(prompt_code)
        
        # Cleanly extract Python code from markdown blocks if returned
        python_code = raw_code_response
        if "```python" in python_code:
            parts = python_code.split("```python")
            if len(parts) > 1:
                python_code = parts[1].split("```")[0].strip()
        elif "```" in python_code:
            parts = python_code.split("```")
            if len(parts) > 1:
                python_code = parts[1].strip()

        bp_dict["executable_python_logic"] = python_code
        return json.dumps(bp_dict)

    def answer_question(self, user_query: str) -> str:
        context = self.vector_store.search_similar(user_query, top_k=6)
        prompt = f"""
        You are an expert AI Research Assistant. Answer user questions strictly based on the provided text extracted from the academic research paper.

        Context:
        {context}

        User Question:
        {user_query}

        Instructions:
        1. Answer the question accurately using only information explicitly stated in the provided paper.
        2. If the answer cannot be found in the text, state: "I cannot find this information in the uploaded research paper."
        """
        response = self.client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
        )
        return response.text

    def translate_workflow(self, workflow_logic: str, target_platform: str) -> str:
        prompt = f"""
        You are an integration engineer. Take the workflow logic generated from the research paper and format it for execution within a {target_platform} framework.

        Workflow Architecture & Logic:
        {workflow_logic}

        Instructions:
        1. Translate the node sequence into the syntax and structural requirements of the target platform.
        2. Define clear schema inputs, state management transitions, and tool-calling interfaces.
        """
        response = self.client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
        )
        return response.text

    def refine_workflow(self, current_json: str, user_feedback: str) -> str:
        prompt = f"""
        You are an adaptive workflow assistant. Modify the existing workflow schema based on the user modification request.

        Current Workflow Schema JSON:
        {current_json}

        User Modification Request:
        {user_feedback}

        Instructions:
        1. Modify the JSON schema to incorporate the user's requested change without breaking existing connections.
        2. Return the updated JSON schema.
        """
        response = self.client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
        )
        return response.text

    def _call_gemini(self, prompt: str, config=None) -> str:
        last_error = None
        for attempt in range(3):
            try:
                response = self.client.models.generate_content(
                    model="gemini-3.6-flash",
                    contents=prompt,
                    config=config,
                )
                return response.text
            except Exception as error:
                last_error = error
                if attempt == 2:
                    raise
                time.sleep(2 ** attempt)
        else:
            raise RuntimeError("Gemini did not return a response.") from last_error