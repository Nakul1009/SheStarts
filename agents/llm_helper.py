import os
import json
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from dotenv import load_dotenv
load_dotenv()
def get_llm(state: dict, model_name: str = "meta/llama-3.3-70b-instruct"):
    """
    Initializes ChatNVIDIA using the API key in state or environment.
    """
    api_key = state.get("nvidia_api_key") or os.getenv("NVIDIA_API_KEY")
    if not api_key:
        raise ValueError("NVIDIA API Key not found. Please provide it via the UI sidebar or a .env file.")
    
    return ChatNVIDIA(
        model=model_name,
        api_key=api_key,
        temperature=1.0,
        top_p=0.95,
        max_completion_tokens=16384
    )

def get_structured_output(state: dict, pydantic_model, prompt_template: ChatPromptTemplate, prompt_vars: dict, model_name: str = "meta/llama-3.3-70b-instruct"):
    """
    Generates structured output for a Pydantic model. 
    Uses langchain's .with_structured_output if supported, 
    otherwise falls back to parsing JSON from raw output.
    """
    llm = get_llm(state, model_name)
    
    try:
        # Try native structured output first
        structured_llm = llm.with_structured_output(pydantic_model)
        chain = prompt_template | structured_llm
        result = chain.invoke(prompt_vars)
        return result
    except Exception as e:
        print(f"Native structured output failed, trying fallback JSON parsing: {e}")
        
        # Fallback: JSON instruction and parsing
        parser = JsonOutputParser(pydantic_object=pydantic_model)
        
        # Inject format instructions into the system or user prompt if possible
        format_instructions = parser.get_format_instructions()
        
        # Recreate the prompt with format instructions appended to user input
        modified_prompt_vars = prompt_vars.copy()
        if "format_instructions" in prompt_template.input_variables:
            modified_prompt_vars["format_instructions"] = format_instructions
        
        chain = prompt_template | llm
        raw_response = chain.invoke(modified_prompt_vars)
        
        content = raw_response.content if hasattr(raw_response, 'content') else str(raw_response)
        
        # Clean up response content if LLM wrapped it in markdown code blocks
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
            
        try:
            parsed = json.loads(content)
            return pydantic_model.model_validate(parsed)
        except Exception as json_err:
            print(f"Fallback JSON parsing also failed: {json_err}. Raw content: {content}")
            raise json_err
