import openai
import os
from typing import Dict, List, Optional, Any
from loguru import logger

class WorkingAIAgent:
    def __init__(self, agent_type: str = "sales"):
        self.agent_type = agent_type
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        
        # Define agent personas and expertise
        self.agent_personas = {
            "sales": {
                "role": "Expert B2B Sales Representative",
                "expertise": "Lead qualification, objection handling, discovery calls, deal closing",
                "tone": "Professional, consultative, and results-driven"
            },
            "email": {
                "role": "Email Marketing Specialist", 
                "expertise": "Cold outreach, email sequences, personalization, A/B testing",
                "tone": "Persuasive, personable, and action-oriented"
            },
            "auto": {
                "role": "Intelligent Sales & Marketing Assistant",
                "expertise": "Sales, marketing, customer success, and business development",
                "tone": "Adaptive and solution-focused"
            }
        }
    
    def get_system_prompt(self) -> str:
        """Generate system prompt based on agent type and use case"""
        persona = self.agent_personas.get(self.agent_type, self.agent_personas["auto"])
        
        base_prompt = f"""You are a {persona['role']} working for a B2B SaaS company.

EXPERTISE: {persona['expertise']}
TONE: {persona['tone']}

BUSINESS CONTEXT:
- You work for companies selling software, services, or solutions to other businesses
- Your goal is to help qualify prospects, generate revenue, and provide value
- You should be helpful, knowledgeable, and focused on business outcomes

SPECIFIC USE CASES YOU EXCEL AT:
1. Lead Qualification - Determining if prospects are sales-ready
2. Objection Handling - Addressing common concerns and pushbacks  
3. Email Generation - Creating personalized, high-converting outreach
4. Sales Strategy - Providing tactical advice for deal progression
5. Discovery Questions - Uncovering prospect needs and pain points

RESPONSE GUIDELINES:
- Be specific and actionable
- Reference real business scenarios
- Provide frameworks and methodologies
- Include next steps or follow-up actions
- Keep responses concise but comprehensive
"""

        # Add agent-specific instructions
        if self.agent_type == "sales":
            base_prompt += """
SALES-SPECIFIC INSTRUCTIONS:
- Focus on qualification frameworks (BANT, MEDDIC, etc.)
- Provide objection handling scripts
- Suggest discovery questions
- Recommend next steps for deal progression
- Include ROI/value proposition guidance
"""
        elif self.agent_type == "email":
            base_prompt += """
EMAIL-SPECIFIC INSTRUCTIONS:
- Create personalized subject lines
- Write compelling email copy
- Include clear calls-to-action
- Suggest follow-up sequences
- Optimize for response rates
"""
        
        return base_prompt
    
    async def process_task(self, task: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Process a task using OpenAI API"""
        try:
            if not self.openai_api_key:
                return {
                    "success": False,
                    "response": "OpenAI API key not configured. Please add OPENAI_API_KEY to your .env file.",
                    "agent_type": self.agent_type
                }
            
            # Create the prompt
            system_prompt = self.get_system_prompt()
            user_message = task
            
            # Add context if provided
            if context:
                context_str = "\n".join([f"{k}: {v}" for k, v in context.items()])
                user_message = f"CONTEXT:\n{context_str}\n\nTASK: {task}"
            
            # Call OpenAI API
            client = openai.OpenAI(api_key=self.openai_api_key)
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",  # Using the faster, cheaper model
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7,
                max_tokens=1500
            )
            
            ai_response = response.choices[0].message.content
            
            logger.info(f"AI Agent ({self.agent_type}) processed task successfully")
            
            return {
                "success": True,
                "response": ai_response,
                "agent_type": self.agent_type,
                "model": "gpt-4o-mini",
                "tokens_used": response.usage.total_tokens if response.usage else 0
            }
            
        except Exception as e:
            logger.error(f"Error processing task with AI agent: {str(e)}")
            return {
                "success": False,
                "response": f"Error: {str(e)}",
                "agent_type": self.agent_type
            }

class SalesAgent(WorkingAIAgent):
    def __init__(self):
        super().__init__("sales")
        
    async def qualify_lead(self, lead_info: Dict) -> Dict[str, Any]:
        """Specialized method for lead qualification"""
        task = f"""
        Analyze this lead and provide a qualification assessment:
        
        Lead Information:
        - Name: {lead_info.get('name', 'Unknown')}
        - Company: {lead_info.get('company', 'Unknown')}
        - Role: {lead_info.get('role', 'Unknown')}
        - Company Size: {lead_info.get('company_size', 'Unknown')}
        - Industry: {lead_info.get('industry', 'Unknown')}
        - Actions Taken: {lead_info.get('actions', 'None provided')}
        
        Please provide:
        1. Qualification Score (1-10)
        2. Key qualification criteria met/missing
        3. Recommended next steps
        4. Discovery questions to ask
        5. Potential objections to prepare for
        """
        
        return await self.process_task(task)

class EmailAgent(WorkingAIAgent):
    def __init__(self):
        super().__init__("email")
        
    async def generate_email(self, prospect_info: Dict) -> Dict[str, Any]:
        """Generate personalized outreach email"""
        task = f"""
        Create a personalized cold outreach email for this prospect:
        
        Prospect Information:
        - Name: {prospect_info.get('prospect_name', 'Unknown')}
        - Company: {prospect_info.get('prospect_company', 'Unknown')}
        - Role: {prospect_info.get('prospect_role', 'Unknown')}
        - Context: {prospect_info.get('context', 'General outreach')}
        
        Please provide:
        1. Compelling subject line
        2. Personalized email body
        3. Clear call-to-action
        4. Follow-up strategy
        
        Email should be:
        - Under 150 words
        - Highly personalized
        - Value-focused
        - Professional but conversational
        """
        
        return await self.process_task(task)

class AutoAgent(WorkingAIAgent):
    def __init__(self):
        super().__init__("auto")
        
    async def route_and_process(self, task: str) -> Dict[str, Any]:
        """Automatically determine the best approach and process the task"""
        # First, determine which type of agent would be best
        routing_task = f"""
        Analyze this task and determine if it's primarily:
        1. SALES-related (lead qualification, objection handling, discovery, deal strategy)
        2. EMAIL-related (email writing, outreach sequences, email strategy)
        3. GENERAL (requires mixed expertise)
        
        Task: {task}
        
        Respond with just: SALES, EMAIL, or GENERAL
        """
        
        try:
            client = openai.OpenAI(api_key=self.openai_api_key)
            routing_response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": routing_task}],
                temperature=0.1,
                max_tokens=10
            )
            
            route = routing_response.choices[0].message.content.strip().upper()
            
            # Route to appropriate specialized agent
            if route == "SALES":
                agent = SalesAgent()
            elif route == "EMAIL":
                agent = EmailAgent()
            else:
                agent = self
                
            result = await agent.process_task(task)
            result["routed_to"] = route
            return result
            
        except Exception as e:
            # Fallback to general processing
            return await self.process_task(task)