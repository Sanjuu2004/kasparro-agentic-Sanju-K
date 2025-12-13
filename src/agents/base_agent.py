from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from langchain.agents import AgentExecutor
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI  # Updated import
from langchain_core.output_parsers import JsonOutputParser
import google.generativeai as genai
from ..config import Config  # Import the updated config


class BaseAgent(ABC):
    """Base class for all agents in the system - Updated for Gemini"""
    
    def __init__(self, name: str, description: str, llm=None):
        self.name = name
        self.description = description
        
        # Use provided LLM or create from config
        if llm:
            self.llm = llm
        else:
            config = Config()
            self.llm = config.llm  # This is now ChatGoogleGenerativeAI
        
        self.tools = []
        self.agent_executor: Optional[AgentExecutor] = None
        self.json_parser = JsonOutputParser()
        
        # For direct Gemini calls when LangChain tools don't work
        self.direct_gemini_model = None
        try:
            self.direct_gemini_model = genai.GenerativeModel('gemini-1.5-flash')
        except:
            pass
        
        self._setup_tools()
        self._setup_agent()
    
    @abstractmethod
    def _setup_tools(self):
        """Setup agent-specific tools - to be implemented by subclasses"""
        pass
    
    @abstractmethod
    def _setup_agent(self):
        """Setup agent with prompt - to be implemented by subclasses"""
        pass
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """Get system prompt for the agent"""
        pass
    
    def _create_simple_chain(self, system_prompt: str):
        """Create a simple chain for Gemini (since tool calling might not work well)"""
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=system_prompt),
            HumanMessage(content="{input}"),
        ])
        
        return prompt | self.llm | self.json_parser
    
    def _call_direct_gemini(self, prompt: str, system_instruction: str = None):
        """Call Gemini directly without LangChain tools"""
        if not self.direct_gemini_model:
            # Fallback to LangChain
            messages = []
            if system_instruction:
                messages.append(SystemMessage(content=system_instruction))
            messages.append(HumanMessage(content=prompt))
            
            response = self.llm.invoke(messages)
            return response.content
        
        # Use direct Gemini API
        try:
            generation_config = genai.types.GenerationConfig(
                temperature=0.2,
                max_output_tokens=2000,
                top_p=0.95,
                top_k=40
            )
            
            if system_instruction:
                response = self.direct_gemini_model.generate_content(
                    f"System: {system_instruction}\n\nUser: {prompt}",
                    generation_config=generation_config
                )
            else:
                response = self.direct_gemini_model.generate_content(
                    prompt,
                    generation_config=generation_config
                )
            
            return response.text
        except Exception as e:
            print(f"Direct Gemini call failed: {e}")
            # Fallback to simple LLM call
            return self.llm.invoke(prompt).content
    
    def _create_agent_executor(self, tools: list, system_prompt: str) -> AgentExecutor:
        """Create an agent executor - simplified for Gemini compatibility"""
        try:
            # Try to create standard agent with Gemini
            # Note: Gemini doesn't support tool calling as well as OpenAI
            # So we use a simpler approach
            
            from langchain.agents import create_react_agent
            from langchain.agents import AgentExecutor
            
            prompt = ChatPromptTemplate.from_messages([
                SystemMessage(content=system_prompt),
                HumanMessage(content="{input}"),
                ("placeholder", "{agent_scratchpad}"),
            ])
            
            # Create REACT agent (works better with Gemini)
            agent = create_react_agent(self.llm, tools, prompt)
            return AgentExecutor(
                agent=agent, 
                tools=tools, 
                verbose=True, 
                handle_parsing_errors=True,
                max_iterations=3,
                early_stopping_method="generate"
            )
            
        except Exception as e:
            print(f"Warning: Could not create agent executor: {e}")
            print("Using simple chain instead...")
            
            # Create a simple prompt chain instead
            class SimpleExecutor:
                def __init__(self, chain):
                    self.chain = chain
                
                def invoke(self, inputs):
                    try:
                        result = self.chain.invoke(inputs)
                        return {"output": str(result)}
                    except Exception as e:
                        return {"output": f"Error: {str(e)}"}
            
            chain = self._create_simple_chain(system_prompt)
            return SimpleExecutor(chain)
    
    def run_with_json_output(self, input_data: Dict[str, Any], system_prompt: str = None) -> Dict[str, Any]:
        """Run agent and parse JSON output - optimized for Gemini"""
        try:
            if system_prompt is None:
                system_prompt = self.get_system_prompt()
            
            # Create prompt for JSON output
            json_prompt = system_prompt + "\n\nIMPORTANT: Return ONLY valid JSON. Do not include any other text, explanations, or markdown formatting."
            
            prompt = ChatPromptTemplate.from_messages([
                SystemMessage(content=json_prompt),
                HumanMessage(content=str(input_data)),
            ])
            
            chain = prompt | self.llm | self.json_parser
            result = chain.invoke({"input": str(input_data)})
            
            return {
                "success": True,
                "agent": self.name,
                "output": result,
                "error": None
            }
            
        except Exception as e:
            print(f"JSON chain failed, trying direct call: {e}")
            
            # Try direct Gemini call
            try:
                direct_result = self._call_direct_gemini(
                    f"Return valid JSON for: {str(input_data)}",
                    system_prompt
                )
                
                # Try to extract JSON from response
                import json
                import re
                
                # Find JSON in text
                json_match = re.search(r'\{.*\}', direct_result, re.DOTALL)
                if json_match:
                    json_str = json_match.group()
                    parsed = json.loads(json_str)
                    return {
                        "success": True,
                        "agent": self.name,
                        "output": parsed,
                        "error": None,
                        "method": "direct_gemini"
                    }
            except:
                pass
            
            return {
                "success": False,
                "agent": self.name,
                "output": None,
                "error": str(e)
            }
    
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent with given input - main entry point"""
        try:
            # Try with agent executor if available
            if self.agent_executor:
                result = self.agent_executor.invoke({"input": str(input_data)})
                return {
                    "success": True,
                    "agent": self.name,
                    "output": result.get("output", ""),
                    "intermediate_steps": result.get("intermediate_steps", []),
                    "error": None
                }
            else:
                # Fallback to simple JSON output
                return self.run_with_json_output(input_data)
                
        except Exception as e:
            # Last resort: direct call
            try:
                direct_result = self._call_direct_gemini(
                    str(input_data),
                    self.get_system_prompt()
                )
                return {
                    "success": True,
                    "agent": self.name,
                    "output": direct_result,
                    "error": None,
                    "method": "direct_fallback"
                }
            except Exception as e2:
                return {
                    "success": False,
                    "agent": self.name,
                    "output": None,
                    "error": f"{str(e)}; Fallback also failed: {str(e2)}"
                }