import json
import random
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

# Import simple email sender
try:
    from .simple_email_sender import SimpleEmailSender
    EMAIL_SENDING_AVAILABLE = True
except ImportError:
    EMAIL_SENDING_AVAILABLE = False

# Set up basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LocalAIAgent:
    """AI Agent that works without API keys using rule-based intelligence and templates"""
    
    def __init__(self, agent_type: str = "sales"):
        self.agent_type = agent_type
        self.knowledge_base = self._load_knowledge_base()
        
    def _load_knowledge_base(self) -> Dict:
        """Load pre-built knowledge base for different business scenarios"""
        return {
            "sales": {
                "qualification_frameworks": ["BANT", "MEDDIC", "CHAMP", "SPICED"],
                "objections": {
                    "price": [
                        "I understand price is a concern. Let's focus on ROI - what would a 20% increase in sales efficiency be worth to your team?",
                        "Many companies find that the time savings alone pays for itself within 60 days. What's the cost of missing qualified leads?",
                        "Price is definitely important. Can we schedule a brief call to show you the exact ROI calculator other similar companies use?"
                    ],
                    "timing": [
                        "I totally get that timing matters. What would need to happen for this to become a priority?",
                        "Many of our best customers started with 'not the right time.' What's driving your current priorities?",
                        "That's fair. When would be a better time to revisit this? Can I follow up in [timeframe]?"
                    ],
                    "budget": [
                        "Budget is always a consideration. Have you allocated funds for solving [pain point] this year?",
                        "Most companies find budget when they see clear ROI. What would justify the investment for you?",
                        "I understand. What budget range would make sense for a solution that [value proposition]?"
                    ]
                },
                "discovery_questions": [
                    "What's your current process for [relevant process]?",
                    "How are you handling [pain point] today?",
                    "What would success look like for your team?",
                    "Who else is involved in this decision?",
                    "What's the cost of not solving this problem?",
                    "When do you need to have a solution in place?",
                    "What solutions have you evaluated so far?"
                ],
                "value_props": {
                    "saas": "Increase team productivity by 40%, reduce manual work by 80%, and improve customer satisfaction",
                    "services": "Get expert guidance, proven methodologies, and faster time to results",
                    "ecommerce": "Boost conversion rates, reduce cart abandonment, and increase average order value"
                }
            },
            "email": {
                "subject_lines": {
                    "cold": [
                        "Quick question about {company}",
                        "{name}, noticed {trigger_event}",
                        "5-min chat about {pain_point}?",
                        "{company} + {solution} = ?",
                        "Helping {similar_company} with {result}"
                    ],
                    "follow_up": [
                        "Following up on {previous_topic}",
                        "{name}, did you get my message?",
                        "Quick follow-up - {value_prop}",
                        "One more try - {benefit}",
                        "Last attempt - {urgent_reason}"
                    ]
                },
                "templates": {
                    "cold_outreach": """Hi {name},

I noticed {personalization_trigger} and thought you might be interested in how {similar_company} {achieved_result}.

{value_proposition}

Worth a 15-minute conversation?

Best regards,
{sender_name}""",
                    "follow_up": """Hi {name},

Following up on my previous email about {topic}.

{additional_value} - would love to share how this could work for {company}.

Quick call this week?

Best,
{sender_name}""",
                    "value_based": """Hi {name},

{industry_specific_insight}

We've helped companies like {similar_company} achieve:
• {benefit_1}
• {benefit_2}  
• {benefit_3}

Interested in learning how this applies to {company}?

Best,
{sender_name}"""
                }
            },
            "industries": {
                "saas": {
                    "pain_points": ["customer churn", "user adoption", "scaling support", "lead quality"],
                    "metrics": ["MRR growth", "CAC", "LTV", "churn rate"],
                    "solutions": ["automation", "analytics", "integration", "optimization"]
                },
                "real_estate": {
                    "pain_points": ["lead response time", "market analysis", "client communication", "deal pipeline"],
                    "metrics": ["conversion rate", "average deal size", "time to close", "client satisfaction"],
                    "solutions": ["CRM automation", "market insights", "communication tools", "pipeline management"]
                },
                "ecommerce": {
                    "pain_points": ["cart abandonment", "customer acquisition", "inventory management", "conversion optimization"],
                    "metrics": ["conversion rate", "AOV", "ROAS", "customer lifetime value"],
                    "solutions": ["personalization", "automation", "analytics", "optimization"]
                }
            }
        }

class LocalSalesAgent(LocalAIAgent):
    def __init__(self):
        super().__init__("sales")
        
    async def process_task(self, task: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Process sales-related tasks using rule-based intelligence"""
        try:
            task_lower = task.lower()
            
            # Lead Qualification
            if any(word in task_lower for word in ["qualify", "lead", "prospect"]):
                return await self._qualify_lead(task, context)
            
            # Objection Handling
            elif any(word in task_lower for word in ["objection", "price", "budget", "timing", "competitor"]):
                return await self._handle_objection(task, context)
            
            # Discovery Questions
            elif any(word in task_lower for word in ["discovery", "questions", "call", "meeting"]):
                return await self._generate_discovery_questions(task, context)
            
            # Sales Strategy
            elif any(word in task_lower for word in ["strategy", "approach", "plan", "framework"]):
                return await self._create_sales_strategy(task, context)
            
            # General Sales Help
            else:
                return await self._general_sales_advice(task, context)
                
        except Exception as e:
            logger.error(f"Error in LocalSalesAgent: {str(e)}")
            return {
                "success": False,
                "response": "I encountered an error processing your request. Please try rephrasing your question.",
                "agent_type": "sales"
            }
    
    async def _qualify_lead(self, task: str, context: Optional[Dict]) -> Dict[str, Any]:
        """Generate lead qualification assessment"""
        frameworks = self.knowledge_base["sales"]["qualification_frameworks"]
        questions = self.knowledge_base["sales"]["discovery_questions"]
        
        response = f"""**Lead Qualification Assessment**

**Recommended Framework:** {random.choice(frameworks)}

**Key Qualification Areas to Explore:**

1. **Budget Authority**
   - Do they have budget allocated?
   - Who controls the budget decision?
   - What's the approval process?

2. **Need/Pain Point**
   - What specific challenges are they facing?
   - How are they solving it today?
   - What's the cost of not solving it?

3. **Timeline**
   - When do they need a solution?
   - What's driving the urgency?
   - Any upcoming deadlines or events?

4. **Decision Process**
   - Who else is involved in the decision?
   - What's their evaluation criteria?
   - Have they looked at other solutions?

**Next Steps:**
1. Schedule a discovery call
2. Send qualification questionnaire
3. Research their company and industry
4. Prepare value proposition tailored to their needs

**Discovery Questions to Ask:**
{chr(10).join([f"• {q}" for q in random.sample(questions, 5)])}

**Qualification Score Factors:**
- Company size and growth stage
- Budget availability and authority
- Timeline urgency
- Pain point severity
- Decision-making process clarity
"""
        
        return {
            "success": True,
            "response": response,
            "agent_type": "sales",
            "framework_used": "Lead Qualification"
        }
    
    async def _handle_objection(self, task: str, context: Optional[Dict]) -> Dict[str, Any]:
        """Provide objection handling responses"""
        objections = self.knowledge_base["sales"]["objections"]
        
        # Determine objection type
        objection_type = "price"
        if "budget" in task.lower() or "cost" in task.lower() or "expensive" in task.lower():
            objection_type = "budget"
        elif "time" in task.lower() or "busy" in task.lower() or "later" in task.lower():
            objection_type = "timing"
        
        responses = objections.get(objection_type, objections["price"])
        
        response = f"""**Objection Handling: {objection_type.title()}**

**Recommended Responses:**

{chr(10).join([f"{i+1}. {resp}" for i, resp in enumerate(responses)])}

**Framework: LAER Method**
- **Listen:** Fully understand their concern
- **Acknowledge:** Validate their perspective  
- **Explore:** Ask questions to uncover the real objection
- **Respond:** Address with value and evidence

**Follow-up Strategy:**
1. Ask clarifying questions to understand the root concern
2. Provide specific examples and case studies
3. Offer to connect them with similar customers
4. Suggest a pilot or trial to reduce risk
5. Schedule follow-up to address any remaining concerns

**Additional Techniques:**
- Feel, Felt, Found method
- Boomerang technique
- Question technique
- Direct denial (when appropriate)
"""
        
        return {
            "success": True,
            "response": response,
            "agent_type": "sales",
            "objection_type": objection_type
        }
    
    async def _generate_discovery_questions(self, task: str, context: Optional[Dict]) -> Dict[str, Any]:
        """Generate discovery questions for sales calls"""
        questions = self.knowledge_base["sales"]["discovery_questions"]
        
        response = f"""**Discovery Call Question Framework**

**Opening Questions (Build Rapport):**
• How long have you been with {context.get('company', 'the company') if context else 'your company'}?
• What's your role in [relevant department]?
• How did you hear about us?

**Current State Questions:**
{chr(10).join([f"• {q}" for q in questions[:4]])}

**Pain Point Exploration:**
• What's the biggest challenge you're facing with [relevant area]?
• How is this impacting your team/company?
• What have you tried to solve this?
• What would happen if you don't address this?

**Future State Questions:**
• What would an ideal solution look like?
• How would you measure success?
• What would this mean for your business?

**Decision Process Questions:**
• Who else would be involved in evaluating a solution?
• What's your typical process for making decisions like this?
• What's your timeline for implementing something?
• What budget range are you considering?

**Closing Questions:**
• What questions do you have for me?
• What would be a logical next step?
• When would be a good time to follow up?

**Pro Tips:**
- Use the 80/20 rule (listen 80%, talk 20%)
- Ask follow-up questions with "Tell me more about that"
- Take detailed notes for follow-up
- Confirm understanding throughout the call
"""
        
        return {
            "success": True,
            "response": response,
            "agent_type": "sales",
            "framework_used": "Discovery Questions"
        }
    
    async def _create_sales_strategy(self, task: str, context: Optional[Dict]) -> Dict[str, Any]:
        """Create sales strategy and approach"""
        value_props = self.knowledge_base["sales"]["value_props"]
        
        response = f"""**Sales Strategy Framework**

**1. Account Research**
- Company background and recent news
- Key stakeholders and decision makers
- Current tech stack and solutions
- Industry trends and challenges
- Competitive landscape

**2. Value Proposition Development**
- Primary pain points they're likely facing
- Specific benefits our solution provides
- ROI calculation and business case
- Success stories from similar companies
- Competitive differentiators

**3. Multi-Touch Outreach Sequence**
- Touch 1: Initial email with value prop
- Touch 2: Follow-up with case study
- Touch 3: Phone call + voicemail
- Touch 4: LinkedIn connection + message
- Touch 5: Email with video message
- Touch 6: Final attempt with referral

**4. Meeting Preparation**
- Custom demo focused on their needs
- Questions to uncover additional pain points
- Pricing options and negotiation strategy
- Next steps and timeline discussion

**5. Deal Progression Strategy**
- Identify all stakeholders
- Create mutual evaluation plan
- Build business case together
- Handle objections proactively
- Establish clear next steps

**6. Closing Techniques**
- Assumptive close
- Alternative choice close
- Urgency close (if genuine)
- Trial close throughout process

**Success Metrics:**
- Response rate to outreach
- Meeting-to-opportunity conversion
- Sales cycle length
- Deal size and close rate
"""
        
        return {
            "success": True,
            "response": response,
            "agent_type": "sales",
            "framework_used": "Sales Strategy"
        }
    
    async def _general_sales_advice(self, task: str, context: Optional[Dict]) -> Dict[str, Any]:
        """Provide general sales advice"""
        response = f"""**Sales Best Practices & Advice**

**Core Sales Principles:**
1. **Listen More Than You Talk** - Understand before trying to be understood
2. **Focus on Value** - Always lead with customer benefit, not features
3. **Build Relationships** - People buy from people they like and trust
4. **Qualify Early** - Don't waste time on unqualified prospects
5. **Follow Up Consistently** - Most sales happen after the 5th touchpoint

**Daily Sales Habits:**
• Start each day with prospecting activities
• Review and update your pipeline weekly
• Send personalized follow-ups within 24 hours
• Practice your pitch and objection handling
• Learn something new about your industry daily

**Key Performance Indicators:**
- Activities: Calls, emails, meetings booked
- Pipeline: Number and value of opportunities
- Conversion: Meeting-to-opportunity rate
- Velocity: Average sales cycle length
- Quality: Average deal size and close rate

**Common Mistakes to Avoid:**
• Talking too much about features vs benefits
• Not asking enough qualifying questions
• Following up too little or too aggressively
• Not understanding the decision-making process
• Giving discounts too early in the process

**Resources for Improvement:**
- Role-play common scenarios with colleagues
- Record and review your sales calls
- Study your best-performing emails and calls
- Get feedback from prospects who didn't buy
- Continuously update your sales materials

**Your Question:** {task}

Based on your specific question, I'd recommend focusing on [relevant advice based on the task]. Would you like me to dive deeper into any particular area?
"""
        
        return {
            "success": True,
            "response": response,
            "agent_type": "sales",
            "framework_used": "General Sales Advice"
        }

class LocalEmailAgent(LocalAIAgent):
    def __init__(self):
        super().__init__("email")
    
    async def process_task(self, task: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Process email-related tasks"""
        try:
            task_lower = task.lower()
            
            if any(word in task_lower for word in ["cold", "outreach", "prospect"]):
                return await self._generate_cold_email(task, context)
            elif any(word in task_lower for word in ["follow", "sequence", "campaign"]):
                return await self._create_email_sequence(task, context)
            elif any(word in task_lower for word in ["subject", "headline"]):
                return await self._generate_subject_lines(task, context)
            else:
                return await self._general_email_advice(task, context)
                
        except Exception as e:
            logger.error(f"Error in LocalEmailAgent: {str(e)}")
            return {
                "success": False,
                "response": "I encountered an error processing your email request. Please try again.",
                "agent_type": "email"
            }
    
    async def generate_email(self, prospect_info: Dict) -> Dict[str, Any]:
        """Generate personalized outreach email"""
        name = prospect_info.get('prospect_name', 'there')
        company = prospect_info.get('prospect_company', 'your company')
        role = prospect_info.get('prospect_role', 'your role')
        context = prospect_info.get('context', 'general outreach')
        
        # Generate personalized email
        subject_lines = self.knowledge_base["email"]["subject_lines"]["cold"]
        template = self.knowledge_base["email"]["templates"]["cold_outreach"]
        
        # Personalization triggers based on context
        triggers = {
            "downloaded": f"saw you downloaded our {context}",
            "visited": f"noticed you visited our {context} page",
            "webinar": f"saw you attended our {context}",
            "product": f"thought you might be interested in our product solutions",
            "company": f"came across {company} and was impressed by your growth in the industry",
            "general": f"came across {company} and was impressed by your growth in the industry"
        }
        
        # Better context detection
        if "product" in context.lower() or "company" in context.lower():
            trigger_key = "company"
        else:
            trigger_key = next((k for k in triggers.keys() if k in context.lower()), "general")
        personalization = triggers[trigger_key]
        
        # Value propositions based on role
        value_props = {
            "ceo": "helping CEOs like yourself scale operations and increase revenue",
            "vp": "enabling VPs to hit their targets faster with less manual work",
            "manager": "giving managers the tools to improve team performance",
            "director": "helping directors optimize processes and drive results",
            "default": "helping companies like yours achieve better results"
        }
        
        role_key = next((k for k in value_props.keys() if k in role.lower()), "default")
        value_prop = value_props[role_key]
        
        subject = random.choice(subject_lines).format(
            company=company,
            name=name.split()[0] if name != 'there' else 'there',
            trigger_event=context,
            pain_point="operational efficiency",
            solution="automation"
        )
        
        # Create better email body with proper formatting
        if name != "there" and company != "your company":
            greeting = f"Hi {name.split()[0]},"
            company_mention = f"I {personalization}."
        else:
            greeting = "Hi there,"
            company_mention = f"I hope this email finds you well."
        
        # Build structured email body
        sender_name = "Your Sales Team"
        email_body = f"""{greeting}

{company_mention}

We've been helping companies like {company} achieve:
• 50% reduction in manual processes
• 40% improvement in operational efficiency  
• 25% faster time-to-market

{value_prop.capitalize()}.

Worth a brief 15-minute conversation to explore how this could apply to {company}?

Best regards,
{sender_name}"""
        
        response = f"""**Subject Line:** {subject}

**Email Body:**
{email_body}

**Email Strategy:**
- **Personalization Level:** High (company and role-specific)
- **Value Focus:** Operational efficiency and results
- **Call-to-Action:** Low-pressure meeting request
- **Follow-up:** Recommend 5-touch sequence over 2 weeks

**Performance Optimization Tips:**
- A/B test subject lines for your industry
- Include specific metrics when possible
- Keep emails under 150 words
- Send Tuesday-Thursday, 10-11 AM for best response rates
- Personalize the sender name and email signature

**Next Steps:**
1. Send initial email
2. Follow up in 3-4 business days if no response
3. Vary your approach (phone, LinkedIn, etc.)
4. Track open rates and responses for optimization
"""
        
        return {
            "success": True,
            "response": response,
            "agent_type": "email",
            "subject_line": subject,
            "email_body": email_body
        }
    
    async def _generate_cold_email(self, task: str, context: Optional[Dict]) -> Dict[str, Any]:
        """Generate cold outreach email templates"""
        templates = self.knowledge_base["email"]["templates"]
        subject_lines = self.knowledge_base["email"]["subject_lines"]["cold"]
        
        response = f"""**Cold Outreach Email Framework**

**Subject Line Options:**
{chr(10).join([f"• {line}" for line in subject_lines[:5]])}

**Email Template Structure:**

**Template 1: Value-First Approach**
```
Hi [Name],

[Personalization trigger - something specific about their company]

We've helped companies like [Similar Company] achieve [Specific Result].

[Brief value proposition in 1-2 sentences]

Worth a 15-minute conversation to see if there's a fit?

Best regards,
[Your Name]
```

**Template 2: Problem-Agitation-Solution**
```
Hi [Name],

Many [Role] tell us that [Common Pain Point] is their biggest challenge.

[Agitate the problem with a specific example or stat]

We've developed a solution that [Specific Benefit]. 

Interested in learning how [Similar Company] solved this?

Best,
[Your Name]
```

**Template 3: Question-Based Approach**
```
Hi [Name],

Quick question: How is [Company] currently handling [Relevant Process]?

[Brief context about why you're asking]

[Value proposition or case study]

Worth a brief call to share what's working for others?

Thanks,
[Your Name]
```

**Best Practices:**
- Keep it under 150 words
- One clear call-to-action
- Personalize the first line
- Include social proof
- Make it about them, not you
- A/B test everything

**Metrics to Track:**
- Open rate (aim for 20%+)
- Response rate (aim for 5%+)
- Meeting booking rate (aim for 2%+)
- Email deliverability
"""
        
        return {
            "success": True,
            "response": response,
            "agent_type": "email",
            "framework_used": "Cold Email Generation"
        }
    
    async def _create_email_sequence(self, task: str, context: Optional[Dict]) -> Dict[str, Any]:
        """Create email follow-up sequences"""
        response = f"""**Email Sequence Framework (5-Touch Campaign)**

**Email 1: Initial Outreach (Day 1)**
- Subject: [Value-focused subject line]
- Content: Personalized value proposition
- CTA: Request for brief call
- Length: 100-125 words

**Email 2: Case Study Follow-up (Day 4)**
- Subject: "Following up + [Specific Case Study]"
- Content: Detailed success story from similar company
- CTA: "Worth learning how this applies to [Company]?"
- Length: 125-150 words

**Email 3: Resource Share (Day 8)**
- Subject: "[Resource] that might interest you"
- Content: Valuable content (guide, calculator, template)
- CTA: Soft ask for feedback on the resource
- Length: 75-100 words

**Email 4: Direct Ask (Day 12)**
- Subject: "Quick question about [Specific Pain Point]"
- Content: Direct question about their challenges
- CTA: "15-minute call to share solutions?"
- Length: 50-75 words

**Email 5: Final Attempt (Day 18)**
- Subject: "Last attempt - [Compelling Reason]"
- Content: Final value proposition with urgency
- CTA: "Should I take you off my list?"
- Length: 50-75 words

**Sequence Strategy:**
- Vary subject line approaches
- Include different types of value (case studies, resources, insights)
- Gradually increase directness
- Use different CTAs to test response
- Track which emails perform best

**Personalization Variables:**
- Company name and industry
- Specific pain points by role
- Recent company news or events
- Mutual connections or customers
- Geographic or market relevance

**Performance Benchmarks:**
- Overall sequence response rate: 10-15%
- Email 1 typically highest open rate
- Email 2-3 often highest response rate
- Email 5 can get responses due to urgency
"""
        
        return {
            "success": True,
            "response": response,
            "agent_type": "email",
            "framework_used": "Email Sequence"
        }
    
    async def _generate_subject_lines(self, task: str, context: Optional[Dict]) -> Dict[str, Any]:
        """Generate effective subject lines"""
        cold_subjects = self.knowledge_base["email"]["subject_lines"]["cold"]
        follow_up_subjects = self.knowledge_base["email"]["subject_lines"]["follow_up"]
        
        response = f"""**High-Converting Subject Line Formulas**

**Cold Outreach Subject Lines:**
{chr(10).join([f"• {line}" for line in cold_subjects])}

**Follow-up Subject Lines:**
{chr(10).join([f"• {line}" for line in follow_up_subjects])}

**Subject Line Formulas That Work:**

**1. Question-Based**
- "Quick question about [Company]"
- "[Name], how do you handle [Process]?"
- "Thoughts on [Industry Trend]?"

**2. Personalization-Based**
- "[Name], noticed [Trigger Event]"
- "Congrats on [Recent Achievement]"
- "[Mutual Connection] suggested I reach out"

**3. Value-Based**
- "Help [Company] [Achieve Specific Goal]"
- "[Benefit] in [Timeframe]?"
- "How [Similar Company] [Achieved Result]"

**4. Curiosity-Based**
- "[Company] + [Solution] = ?"
- "This might interest you, [Name]"
- "[Number] [Industry] leaders are doing this"

**5. Direct-Approach**
- "Partnership opportunity with [Company]"
- "5-min chat about [Specific Topic]?"
- "[Solution] demo for [Company]"

**Subject Line Best Practices:**
- Keep under 50 characters for mobile
- Avoid spam trigger words (free, guarantee, urgent)
- Use proper case (not ALL CAPS)
- A/B test everything
- Include company name for personalization
- Make it specific and relevant
- Create curiosity but don't be clickbait-y

**Words That Increase Open Rates:**
- Quick, Brief, Short
- Question, Thoughts, Opinion
- Noticed, Saw, Observed
- Helping, Achieve, Improve
- [Company Name], [First Name]

**Words to Avoid:**
- Free, Guarantee, Limited time
- Urgent, Act now, Don't miss
- Money, Cash, Profit
- Meeting, Call, Demo (sometimes)
"""
        
        return {
            "success": True,
            "response": response,
            "agent_type": "email",
            "framework_used": "Subject Line Generation"
        }
    
    async def _general_email_advice(self, task: str, context: Optional[Dict]) -> Dict[str, Any]:
        """Provide general email marketing advice"""
        response = f"""**Email Marketing Best Practices**

**Email Structure:**
1. **Subject Line** - Clear, compelling, under 50 chars
2. **Opening** - Personal greeting and context
3. **Body** - Value proposition and social proof
4. **CTA** - Single, clear call-to-action
5. **Signature** - Professional with contact info

**Personalization Levels:**
- **Basic:** First name and company
- **Advanced:** Role, industry, recent news
- **Premium:** Specific pain points, mutual connections

**Timing & Frequency:**
- **Best Days:** Tuesday, Wednesday, Thursday
- **Best Times:** 10-11 AM, 2-3 PM
- **Frequency:** Max 1 email per week in sequence
- **Follow-up:** 3-5 touches over 2-3 weeks

**Performance Metrics:**
- **Open Rate:** 20-25% (industry average)
- **Response Rate:** 3-8% (varies by industry)
- **Click Rate:** 2-5% (if including links)
- **Bounce Rate:** Under 2%
- **Unsubscribe:** Under 1%

**A/B Testing Ideas:**
- Subject line variations
- Send time optimization
- Email length (short vs detailed)
- CTA wording and placement
- Personalization elements

**Compliance & Deliverability:**
- Include unsubscribe link
- Use authenticated sending domain
- Avoid spam trigger words
- Maintain clean email lists
- Monitor sender reputation

**Tools & Resources:**
- Email verification services
- Subject line testing tools
- Email template builders
- Analytics and tracking platforms
- CRM integration for automation

**Your Specific Question:** {task}

Would you like me to dive deeper into any of these areas or help you with a specific email challenge?
"""
        
        return {
            "success": True,
            "response": response,
            "agent_type": "email",
            "framework_used": "General Email Advice"
        }

class LocalAutoAgent(LocalAIAgent):
    def __init__(self):
        super().__init__("auto")
        self.sales_agent = LocalSalesAgent()
        self.email_agent = LocalEmailAgent()
    
    async def route_and_process(self, task: str) -> Dict[str, Any]:
        """Route to appropriate agent based on task content"""
        task_lower = task.lower()
        
        # Email-specific routing (enhanced to catch email sending requests)
        if any(phrase in task_lower for phrase in [
            "send email", "write email", "email to", "compose email", 
            "draft email", "create email", "generate email", "@"
        ]):
            return await self._handle_email_request(task)
        
        # Sales routing keywords
        elif any(word in task_lower for word in [
            "qualify", "lead", "prospect", "objection", "discovery", "sales", 
            "call", "meeting", "close", "pipeline", "quota", "conversion"
        ]):
            result = await self.sales_agent.process_task(task)
            result["routed_to"] = "SALES"
            return result
        
        # Email marketing/strategy routing
        elif any(word in task_lower for word in [
            "outreach", "sequence", "subject", "campaign", "cold", "follow-up", "template"
        ]):
            result = await self.email_agent.process_task(task)
            result["routed_to"] = "EMAIL"
            return result
        
        # General business advice
        else:
            result = await self._general_business_advice(task)
            result["routed_to"] = "GENERAL"
            return result
    
    async def _handle_email_request(self, task: str) -> Dict[str, Any]:
        """Handle specific email sending/creation requests"""
        task_lower = task.lower()
        
        # Check if this is a bulk email request
        if any(phrase in task_lower for phrase in [
            "email list", "bulk email", "mass email", "send to all", 
            "email campaign", "prospect list", "multiple emails"
        ]):
            return await self._handle_bulk_email_request(task)
        
        # Check if user wants actual email sending (Option 2)
        if any(phrase in task_lower for phrase in [
            "actually send", "send automatically", "auto send", "send now"
        ]):
            return await self._handle_automatic_email_sending(task)
        
        # Extract email address if present
        import re
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, task)
        recipient_email = emails[0] if emails else "recipient@company.com"
        
        # Extract name from email if possible
        recipient_name = recipient_email.split('@')[0].replace('.', ' ').title() if emails else "Recipient"
        
        # Determine email purpose/context
        email_context = "general outreach"
        if "product" in task_lower:
            email_context = "product introduction"
        elif "demo" in task_lower:
            email_context = "demo request"
        elif "follow" in task_lower:
            email_context = "follow-up"
        elif "meeting" in task_lower:
            email_context = "meeting request"
        elif "company" in task_lower:
            email_context = "company introduction"
        
        # Generate the actual email
        prospect_info = {
            'prospect_name': recipient_name,
            'prospect_company': recipient_email.split('@')[1].split('.')[0].title() if emails else "Their Company",
            'prospect_role': "Decision Maker",
            'context': email_context
        }
        
        email_result = await self.email_agent.generate_email(prospect_info)
        
        # Format the response with OPTION 2 setup instructions
        response = f"""**✉️ EMAIL READY - CHOOSE YOUR METHOD**

**To:** {recipient_email}
**From:** Your Sales Team
**Purpose:** {email_context.title()}

{email_result.get('response', 'Email content generated')}

**🚀 SENDING OPTIONS:**

**Option 1: Manual Copy & Paste (Current)**
1. Copy the email content above
2. Paste into Gmail/Outlook
3. Send manually

**Option 2: Automatic Email Sending (Available!)**
🔧 **SETUP REQUIRED:** Configure your email credentials for automatic sending

To enable automatic email sending, you need:
1. **Gmail App Password** (not your regular password)
2. **Email Configuration** in the system
3. **Test with one email first**

**� EMAIL AUTOMATION SETUP:**

**Step 1: Get Gmail App Password**
- Go to Gmail → Settings → Security
- Enable 2-Factor Authentication
- Generate App Password for "Mail"
- Copy the 16-character password

**Step 2: Configure System**
Navigate to: **http://localhost:3000/bulk-email**
- Enter your Gmail address
- Enter the app password
- Test with one email first

**Step 3: Enable Auto-Sending**
Once configured, ask: "Actually send email to {recipient_email}"
And the system will send it automatically!

**🎯 WHAT AUTO-SENDING DOES:**
- ✅ Sends email immediately to recipient
- ✅ Tracks delivery status
- ✅ Monitors for replies
- ✅ Handles responses automatically
- ✅ Maintains conversation threads

**Ready to set up automatic email sending?**
Visit: **http://localhost:3000/bulk-email**

**Original Request:** {task}
**Status:** ✅ Email generated! Ready for manual or automatic sending.
"""
        
        return {
            "success": True,
            "response": response,
            "agent_type": "auto",
            "routed_to": "EMAIL_GENERATION",
            "recipient": recipient_email,
            "email_content": email_result.get('email_body', ''),
            "subject_line": email_result.get('subject_line', ''),
            "action_required": "Choose manual copy/paste or setup automatic sending",
            "automatic_sending_available": EMAIL_SENDING_AVAILABLE,
            "setup_url": "http://localhost:3000/bulk-email"
        }
    
    async def _handle_automatic_email_sending(self, task: str) -> Dict[str, Any]:
        """Handle automatic email sending requests"""
        
        if not EMAIL_SENDING_AVAILABLE:
            return {
                "success": False,
                "response": "Email sending not configured. Please set up email credentials first.",
                "action_required": "Configure email settings at http://localhost:3000/bulk-email"
            }
        
        # Extract email from task
        import re
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, task)
        
        if not emails:
            return {
                "success": False,
                "response": "No email address found in request. Please specify recipient email.",
                "example": "Send email to john@company.com about our product"
            }
        
        recipient_email = emails[0]
        
        response = f"""**🚀 AUTOMATIC EMAIL SENDING SETUP**

**Recipient:** {recipient_email}
**Request:** {task}

**⚠️ EMAIL CREDENTIALS REQUIRED**

To send emails automatically, I need your email configuration:

**Required Information:**
- Your email address (Gmail recommended)
- App password (16-character code from Gmail)

**Quick Setup:**
1. **Visit:** http://localhost:3000/bulk-email
2. **Configure:** Enter your email credentials
3. **Test:** Send one test email
4. **Confirm:** Come back and ask me to send

**Security Note:**
- Use Gmail App Passwords (not your regular password)
- Credentials are stored securely for sending

**Once configured, you can say:**
- "Send email to {recipient_email} about our product"
- "Actually send that email now"
- "Send bulk emails to our prospect list"

**Alternative: Manual Sending**
If you prefer not to configure automatic sending, I can generate the email content and you can copy/paste it into your email client.

**Next Step:** Configure email at http://localhost:3000/bulk-email
"""
        
        return {
            "success": True,
            "response": response,
            "action_required": "Configure email credentials",
            "setup_url": "http://localhost:3000/bulk-email",
            "recipient": recipient_email
        }
    
    async def _handle_bulk_email_request(self, task: str) -> Dict[str, Any]:
        """Handle bulk email campaign requests"""
        
        response = f"""**🚀 BULK EMAIL CAMPAIGN SYSTEM**

**Your Request:** {task}

**✅ ADVANCED EMAIL AUTOMATION AVAILABLE!**

I can help you set up a complete email automation system that:

**📧 BULK SENDING CAPABILITIES:**
- ✅ Send personalized emails to prospect lists (from CSV files)
- ✅ Auto-personalize each email based on role/company
- ✅ Rate limiting to avoid spam filters (30-60 seconds between emails)
- ✅ Track sent emails and delivery status
- ✅ Professional email templates for different industries

**🤖 INTELLIGENT REPLY HANDLING:**
- ✅ Monitor inbox for responses automatically (every 5 minutes)
- ✅ AI categorizes replies (Interested, Not Interested, Questions, etc.)
- ✅ Generate appropriate follow-up responses automatically
- ✅ Maintain full conversation threads with context
- ✅ Score leads based on engagement and interest level

**📊 CAMPAIGN MANAGEMENT:**
- ✅ Multi-touch email sequences (5-7 personalized emails)
- ✅ Automated follow-ups based on response type
- ✅ A/B testing for subject lines and content
- ✅ Performance analytics (open rates, response rates, meetings booked)
- ✅ Lead scoring and prioritization dashboard

**🎯 BUSINESS IMPACT:**
- **Expected Response Rate:** 8-15% (vs 2-3% for generic emails)
- **Meeting Booking Rate:** 3-6% of total emails sent
- **Time Savings:** 85% reduction in manual email work
- **Lead Quality:** Better qualification through AI conversations

**� QUICK START OPTIONS:**

**Option 1: Test with Sample Data (Recommended)**
1. Go to http://localhost:3000/bulk-email
2. Click "Load Sample Data" (includes 3 sample prospects)
3. Configure your email settings (Gmail app password)
4. Preview the personalized emails
5. Send to test the system

**Option 2: Upload Your Prospect List**
1. Create CSV with columns: email, name, company, role, context
2. Load into the bulk email interface
3. AI will personalize each email automatically
4. Launch campaign with rate limiting

**⚡ IMMEDIATE NEXT STEPS:**
1. **Setup Email:** Get Gmail app password (Settings → Security → App Passwords)
2. **Test Campaign:** Use sample data to see how it works
3. **Load Real Prospects:** Upload your actual prospect list
4. **Monitor Results:** AI handles responses automatically

**� TECHNICAL FEATURES:**
- **Email Authentication:** SPF, DKIM, DMARC support
- **CRM Integration:** Export/import from Salesforce, HubSpot
- **Analytics Dashboard:** Real-time campaign performance
- **Response Processing:** AI handles objections, questions, scheduling

**💡 SAMPLE WORKFLOW:**
1. Load 100 prospects from CSV
2. AI generates 100 personalized emails
3. System sends 1 email per minute (safer delivery)
4. AI monitors responses throughout the day
5. Interested prospects get meeting scheduling emails
6. Questions get detailed automated responses
7. "Not now" prospects go into 90-day follow-up sequence
8. You get daily summary of responses and next actions

**Ready to revolutionize your sales outreach?**

Navigate to: **http://localhost:3000/bulk-email** to get started!
"""
        
        return {
            "success": True,
            "response": response,
            "agent_type": "auto",
            "routed_to": "BULK_EMAIL_AUTOMATION",
            "features_available": [
                "Bulk email sending with personalization",
                "Automatic response monitoring and categorization", 
                "Automated follow-up email generation",
                "Conversation thread management",
                "Campaign performance analytics",
                "Lead scoring and qualification"
            ],
            "next_steps": [
                "Visit http://localhost:3000/bulk-email",
                "Setup email configuration (Gmail app password)",
                "Load prospect list or use sample data",
                "Preview and launch campaign",
                "Monitor AI-powered response handling"
            ],
            "expected_results": {
                "response_rate": "8-15%",
                "meeting_rate": "3-6%", 
                "time_savings": "85%",
                "lead_quality": "Significantly improved"
            }
        }
    
    async def _general_business_advice(self, task: str) -> Dict[str, Any]:
        """Provide general business and GTM advice"""
        response = f"""**Business & Go-To-Market Strategy Advice**

**Your Question:** {task}

**General GTM Framework:**

**1. Market Analysis**
- Define your ideal customer profile (ICP)
- Understand buyer personas and pain points
- Analyze competitive landscape
- Identify market size and opportunity

**2. Value Proposition**
- Clearly articulate your unique value
- Focus on customer outcomes, not features
- Develop messaging for different segments
- Create compelling proof points and case studies

**3. Channel Strategy**
- Direct sales vs partner channels
- Digital marketing and content strategy
- Event and relationship marketing
- Inside sales and outbound prospecting

**4. Sales Process**
- Lead qualification framework
- Sales methodology and playbooks
- Pricing and proposal strategy
- Customer onboarding and success

**5. Measurement & Optimization**
- Define key metrics and KPIs
- Implement tracking and analytics
- Regular testing and optimization
- Customer feedback and iteration

**Common GTM Challenges & Solutions:**

**Challenge:** Long sales cycles
**Solution:** Focus on value selling, multiple stakeholders, and proof of concept

**Challenge:** Low conversion rates
**Solution:** Better qualification, improved messaging, and sales training

**Challenge:** High customer acquisition cost
**Solution:** Optimize marketing channels, improve targeting, and increase retention

**Challenge:** Scaling challenges
**Solution:** Systematize processes, invest in tools, and build repeatable playbooks

Would you like me to dive deeper into any specific area of your go-to-market strategy?
"""
        
        return {
            "success": True,
            "response": response,
            "agent_type": "auto",
            "framework_used": "General Business Advice"
        }