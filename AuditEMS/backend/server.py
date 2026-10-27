# %%
from langgraph.graph import StateGraph , START , END
from langgraph.types import interrupt, Command
from typing import TypedDict
import os
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser , PydanticOutputParser
from pydantic import BaseModel, Field
import mcpServers
from langchain_mcp_adapters.client import MultiServerMCPClient
# from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.postgres import PostgresSaver



class ChatState(TypedDict):
    standard : str
    document : bytes
    section_presence : bool
    necessary_sections : list[str]
    missing_sections : list[str]
    audit_plan : list[str]
    ocr_result : str
    audit_report : str
    feedback : str
    move_ahead : bool


class required_sections(BaseModel):
    req_sections : list[str] = Field(description = "list of the required sections in the document.")

class audit_plan_structure(BaseModel):
    audit_plan : list[str] = Field(description="This is the audit plan list")

class section_presence(BaseModel):
    section_present : bool = Field(description="True if the section is present in the document , False otherwise")

class missing_sections_class(BaseModel):
    section_not_in_doc : list[str] = Field(description = "list of the sections which are not present in the document")

class validate_node_result(BaseModel):
    audit_report : str = Field(description="The audit report")
    feedback : str = Field(description="The feedback for the next iteration")
    move_ahead : bool = Field(description="True if the audit_report can be further moved ahead , False otherwise")

def get_rules(state : ChatState) -> ChatState:
    llm = ChatGroq(
        api_key="YOUR_GROQ_API_KEY",
        model="llama-3.3-70b-versatile",
    )

    structured_llm = llm.with_structured_output(required_sections)

    prompt = PromptTemplate(
        template = "Give me a complete list of required sections in a document for compliance with {standard} under Indian Financial Laws. Return ONLY the JSON object matching the schema.",
        input_variables = ['standard'],
    )

    chain = prompt | structured_llm
    result = chain.invoke({'standard' : state["standard"]})

    print(result)

    return {'necessary_sections' : result.req_sections}


def audit_plan_generator(state : ChatState) -> ChatState:
    llm = ChatGroq(
        api_key="YOUR_GROQ_API_KEY",
        model="llama-3.3-70b-versatile",
    )

    structured_llm = llm.with_structured_output(audit_plan_structure)

    prompt = PromptTemplate(
        template="Provide me an audit plan for compliance with this standard - {standard} , for these sections - {sections} present in the document. Return ONLY the JSON object matching the schema.",
        input_variables=['standard' , 'sections'],
    )

    chain = prompt | structured_llm

    result = chain.invoke({'standard' : state['standard'] , 'sections' : state["necessary_sections"]})
    # print(result)
    return {'audit_plan' : result.audit_plan}

import base64

def create_ocr_node(client):
    async def ocr_node(state : ChatState) -> ChatState:

        file_bytes = state['document']
        file_base64 = base64.b64encode(file_bytes).decode('utf-8')

        # MultiServerMCPClient doesn't have call_tool. Use get_tools instead.
        tools = await client.get_tools()
        print(f"Available tools: {[t.name for t in tools]}")
        
        ocr_tool = next((t for t in tools if t.name == "ocr" or t.name.endswith("ocr")), None)
        
        if not ocr_tool:
            return {'ocr_result': "Error: OCR tool not found."}
            
        # Use 'file_base64' argument for the tool
        result = await ocr_tool.ainvoke({"file_base64": file_base64})

        return {'ocr_result' : result}
    
    return ocr_node


def analyse_ocr_result(state: ChatState) -> ChatState:
    ocr_result = state['ocr_result']
    necessary_sections = state['necessary_sections']

    llm = ChatGroq(
        api_key="YOUR_GROQ_API_KEY",
        model="llama-3.3-70b-versatile",
    )

    structured_llm = llm.with_structured_output(section_presence)

    prompt = PromptTemplate(
        template="""Analyse this OCR result: {result}\nCheck if these sections are present in the document: {sections}.
        If present then return True else return False. Return ONLY the JSON object matching the schema.""",
        input_variables=['result', 'sections'],
    )

    chain = prompt | structured_llm
    result = chain.invoke({'result': ocr_result, 'sections': necessary_sections})

    return {'section_presence': result.section_present}

def validate_node(state : ChatState) -> ChatState:

    llm = ChatGroq(
        api_key="YOUR_GROQ_API_KEY",
        model="llama-3.3-70b-versatile",
    )

    structured_llm = llm.with_structured_output(validate_node_result)

    prompt = PromptTemplate(
        template="""Analyse this OCR result : {result} and the audit plan - {audit_plan} and accordingly the audit_report -> {audit_report} and check this feedback - {feedback} from previous iteration , and decide if the audit_report can be further moved ahead or else fix the audit_report and provide further feedback to improve in next iteration. 
        Return ONLY the JSON object matching the schema.""",
        input_variables=['result', 'audit_plan' , 'audit_report' , 'feedback'],
    )

    chain = prompt | structured_llm
    result = chain.invoke({
        'result': state.get('ocr_result', ''), 
        'audit_plan': state.get('audit_plan', []), 
        'audit_report': state.get('audit_report', ''), 
        'feedback' : state.get('feedback', '')
    })

    return {'audit_report': result.audit_report , 'feedback' : result.feedback , 'move_ahead' : result.move_ahead}

def should_continue(state: ChatState) -> str:
    if state.get('move_ahead'):
        return END
    else:
        return "audit"
    


def classify_node(state: ChatState) -> str:
    if state.get('section_presence', False):
        return "audit"
    else:

        llm = ChatGroq(
            api_key="YOUR_GROQ_API_KEY",
            model="llama-3.3-70b-versatile",
        )

        structured_llm = llm.with_structured_output(missing_sections_class)

        prompt = PromptTemplate(
            template="""Analyse this OCR result: {result}\n Check the sections which are not present in the OCR result \n
            The necessary sections are {sections}. Tell the missing ones.
            Return ONLY the JSON object matching the schema.""",
            input_variables=['result', 'sections'],
        )

        chain = prompt | structured_llm
        ocr_result = state.get('ocr_result', '')
        necessary_sections = state.get('necessary_sections', [])
        result = chain.invoke({'result': ocr_result, 'sections': necessary_sections})

        state['missing_sections'] = result.section_not_in_doc

        # The value returned by interrupt() will be the value passed to Command(resume=...)
        # value will be yes or no
        approval = interrupt({
            "type":"approval",
            "missing_sections":state['missing_sections'],
            "question":"These are the missing sections in your audit , Do you still want to continue with the audit?",
            "instruction" : "Approve this request Yes/No"
        })

        # interrupt pauses the workflow and waits for the user to provide a response
        # the workflow resumes once the user provides a response
        # command gives the interrupt a value and based upon that we move ahead
        
        if str(approval).lower() == 'yes':
            return "audit"
        else:
            return END

def audit(state : ChatState) -> ChatState:
    llm = ChatGroq(
        api_key="YOUR_GROQ_API_KEY",
        model="llama-3.3-70b-versatile",
    )

    prompt = PromptTemplate(
        template="According to this audit plan: {audit_plan} and this document content: {ocr_result}, provide me a complete audit report.",
        input_variables=['audit_plan', 'ocr_result']
    )

    chain = prompt | llm
    result = chain.invoke({'audit_plan': state['audit_plan'], 'ocr_result': state['ocr_result']})

    return {'audit_report': result.content if hasattr(result, 'content') else str(result)}

graph = StateGraph(ChatState)
client = MultiServerMCPClient(mcpServers.SERVERS) 

graph.add_node('get_rules' , get_rules)
graph.add_node('audit_plan_generator' , audit_plan_generator)
graph.add_node('analyse_ocr_result', analyse_ocr_result)
graph.add_node('audit' , audit)
graph.add_node('validate_node', validate_node)

ocr_node = create_ocr_node(client=client)
graph.add_node('ocr_node' , ocr_node)

graph.add_edge(START, "get_rules")
graph.add_edge("get_rules", "audit_plan_generator")
graph.add_edge("audit_plan_generator", "ocr_node")
graph.add_edge("ocr_node", "analyse_ocr_result")
graph.add_conditional_edges(
    "analyse_ocr_result", 
    classify_node,
    {
        END: END,
        "audit": "audit"
    }
)
graph.add_edge("audit", "validate_node")
graph.add_conditional_edges(
    "validate_node",
    should_continue,
    {
        END: END,
        "audit": "audit"
    }
)

checkpointer = PostgresSaver() 
workflow = graph.compile(checkpointer=checkpointer)

# print(workflow)


# initial_state = {
#     "standard" : "Schedule 3"
# }


# final_result = workflow.ainvoke(initial_state)

# MCP expects the data to be in JSON format , therefore we convert to base64 and send as string in JSON format , and not raw bytes.

"""
WHY WITH_STRUCTURED_OUTPUT IS BETTER THAN PYDANTICOUTPUTPARSER:

1. Model-Native Schema Enforcement:
   - PydanticOutputParser: Appends format instructions to the prompt. The model often fails 
     by adding "rambling" text before or after the JSON.
   - with_structured_output: Leverages model-specific features like Tool Calling or JSON Mode. 
     The schema is passed as a dedicated parameter, ensuring strict adherence.

2. Robustness Against "Rambling":
   - PydanticOutputParser: Tries to parse the entire response string. Any extra characters 
     outside the JSON block cause a JSONDecodeError.
   - with_structured_output: Extracts only the structured part. Even if the model talks 
     too much, the structured output layer filters for just the JSON object.

3. Reduced Token Usage:
   - Eliminates the need for large parser format instructions in the prompt, 
     saving context window space and reducing latency.

4. Direct Object Return:
   - The chain returns a Pydantic object (or dict) directly, making the code cleaner 
     and avoiding manual parsing steps.

5 - For pydantic output parser we need to append format instructions to the prompt and 
    for with_structured_output we do not need to append format instructions to the prompt , saving tokens.
    Pydantic output parser is just extra instruction as a prompt to the LLM , llm can speak after giving the output.
    Eg - "I have done your work" , which is not a valid json.
    With structured output , llm will not speak after giving the output.
    it works under the hood.
"""
