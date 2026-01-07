# ============================================
# LLM SERVICE - Dynamic Multi-Provider Support
# Email Parsing with OpenAI/Anthropic/Azure/Ollama/Groq/etc.
# ============================================

import json
import re
from typing import Optional, Dict, Any, List
from abc import ABC, abstractmethod
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.schemas import EmailAnalysisResult, TicketPriorityEnum, TicketCategoryEnum


# SAP Module Keywords for classification
SAP_MODULE_KEYWORDS = {
    "MM": [
        "material", "purchase", "procurement", "vendor", "inventory",
        "goods receipt", "purchase order", "po", "material master",
        "stock", "warehouse", "mrp", "purchase requisition", "pr",
        "invoice verification", "source list", "quota arrangement"
    ],
    "SD": [
        "sales", "distribution", "customer", "order", "delivery",
        "billing", "invoice", "pricing", "sales order", "so",
        "quotation", "inquiry", "shipment", "shipping", "credit memo",
        "returns", "consignment", "third party"
    ],
    "FICO": [
        "finance", "accounting", "controlling", "cost center", "profit center",
        "general ledger", "gl", "accounts payable", "ap", "accounts receivable", "ar",
        "asset accounting", "fixed asset", "financial statement", "budget",
        "internal order", "cost element", "closing", "reconciliation"
    ],
    "PP": [
        "production", "planning", "manufacturing", "bom", "bill of material",
        "routing", "work center", "capacity", "production order", "shop floor",
        "mrp", "demand management", "sop", "scheduling"
    ],
    "HCM": [
        "human resources", "hr", "payroll", "employee", "personnel",
        "time management", "attendance", "leave", "recruitment", "training",
        "organizational management", "benefits", "compensation"
    ],
    "PM": [
        "plant maintenance", "maintenance", "equipment", "functional location",
        "work order", "notification", "preventive maintenance", "breakdown",
        "calibration", "inspection", "repair"
    ],
    "QM": [
        "quality", "inspection", "quality management", "qm", "quality notification",
        "inspection lot", "quality certificate", "calibration", "audit",
        "control chart", "quality planning"
    ],
    "WM": [
        "warehouse management", "wm", "storage bin", "transfer order",
        "putaway", "picking", "goods movement", "storage type", "warehouse structure"
    ],
    "PS": [
        "project system", "project", "wbs", "work breakdown structure",
        "network", "milestone", "project planning", "project budget"
    ],
    "BW": [
        "business warehouse", "bw", "bi", "business intelligence",
        "data warehouse", "infocube", "report", "query", "data extraction"
    ],
    "ABAP": [
        "abap", "programming", "development", "code", "report", "function module",
        "bapi", "rfc", "enhancement", "user exit", "badi", "smartform", "sapscript"
    ],
    "BASIS": [
        "basis", "admin", "system", "transport", "authorization", "role",
        "background job", "performance", "upgrade", "installation", "configuration",
        "user management", "sap*", "client"
    ]
}

# Priority indicators
PRIORITY_INDICATORS = {
    "Critical": [
        "urgent", "critical", "emergency", "asap", "immediately", "down",
        "not working", "stopped", "blocked", "production issue", "showstopper"
    ],
    "High": [
        "important", "high priority", "soon", "affecting", "impact",
        "multiple users", "deadline", "pressing"
    ],
    "Low": [
        "minor", "cosmetic", "enhancement", "nice to have", "when possible",
        "low priority", "no rush"
    ]
}

# System prompt for email analysis
SYSTEM_PROMPT = """You are an SAP support ticket classifier. Analyze emails and determine:
1. If it's related to SAP systems
2. Which SAP module it belongs to (MM, SD, FICO, PP, HCM, PM, QM, WM, PS, BW, ABAP, BASIS, or OTHER)
3. The priority level (Low, Medium, High, Critical)
4. A concise ticket title
5. Key points from the email

Respond ONLY with valid JSON in this exact format:
{
    "is_sap_related": true/false,
    "confidence": 0.0-1.0,
    "category": "MM/SD/FICO/PP/HCM/PM/QM/WM/PS/BW/ABAP/BASIS/OTHER",
    "priority": "Low/Medium/High/Critical",
    "suggested_title": "Brief descriptive title",
    "key_points": ["point 1", "point 2", "point 3"]
}"""

# Available models per provider
AVAILABLE_MODELS = {
    "openai": ["gpt-4-turbo-preview", "gpt-4-turbo", "gpt-4", "gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"],
    "anthropic": ["claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307", "claude-3-5-sonnet-20241022"],
    "azure": ["gpt-4", "gpt-4-32k", "gpt-35-turbo"],
    "ollama": ["llama3.2", "llama3.1", "llama3", "mistral", "mixtral", "codellama", "phi3", "qwen2.5"],
    "groq": ["llama-3.2-90b-vision-preview", "llama-3.1-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"],
    "together": ["meta-llama/Llama-3.2-90B-Vision-Instruct-Turbo", "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo"],
    "google": ["gemini-1.5-pro", "gemini-1.5-flash", "gemini-1.0-pro"],
}


# ============================================
# Abstract LLM Provider Base
# ============================================

class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    def __init__(self, model: str, temperature: float = 0.3, max_tokens: int = 1000):
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
    
    @abstractmethod
    async def chat_completion(self, system_prompt: str, user_prompt: str) -> str:
        """Send a chat completion request and return the response text"""
        pass
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the provider name"""
        pass


# ============================================
# OpenAI Provider
# ============================================

class OpenAIProvider(BaseLLMProvider):
    """OpenAI API provider (GPT-4, GPT-3.5, etc.)"""
    
    def __init__(self, model: str, temperature: float = 0.3, max_tokens: int = 1000):
        super().__init__(model, temperature, max_tokens)
        from openai import AsyncOpenAI
        kwargs = {"api_key": settings.llm_api_key}
        if settings.llm_base_url:
            kwargs["base_url"] = settings.llm_base_url
        self.client = AsyncOpenAI(**kwargs)
    
    @property
    def provider_name(self) -> str:
        return "openai"
    
    async def chat_completion(self, system_prompt: str, user_prompt: str) -> str:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )
        return response.choices[0].message.content.strip()


# ============================================
# Anthropic Provider (Claude)
# ============================================

class AnthropicProvider(BaseLLMProvider):
    """Anthropic API provider (Claude models)"""
    
    def __init__(self, model: str, temperature: float = 0.3, max_tokens: int = 1000):
        super().__init__(model, temperature, max_tokens)
        from anthropic import AsyncAnthropic
        self.client = AsyncAnthropic(api_key=settings.llm_api_key)
    
    @property
    def provider_name(self) -> str:
        return "anthropic"
    
    async def chat_completion(self, system_prompt: str, user_prompt: str) -> str:
        response = await self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}]
        )
        return response.content[0].text.strip()


# ============================================
# Azure OpenAI Provider
# ============================================

class AzureOpenAIProvider(BaseLLMProvider):
    """Azure OpenAI API provider"""
    
    def __init__(self, model: str, temperature: float = 0.3, max_tokens: int = 1000):
        super().__init__(model, temperature, max_tokens)
        from openai import AsyncAzureOpenAI
        self.client = AsyncAzureOpenAI(
            api_key=settings.llm_api_key,
            api_version=settings.azure_openai_api_version,
            azure_endpoint=settings.azure_openai_endpoint
        )
        self.deployment = settings.azure_openai_deployment or model
    
    @property
    def provider_name(self) -> str:
        return "azure"
    
    async def chat_completion(self, system_prompt: str, user_prompt: str) -> str:
        response = await self.client.chat.completions.create(
            model=self.deployment,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )
        return response.choices[0].message.content.strip()


# ============================================
# Ollama Provider (Local LLMs - No API key needed)
# ============================================

class OllamaProvider(BaseLLMProvider):
    """Ollama local LLM provider (Llama, Mistral, etc.)"""
    
    def __init__(self, model: str, temperature: float = 0.3, max_tokens: int = 1000):
        super().__init__(model, temperature, max_tokens)
        import httpx
        self.base_url = settings.llm_base_url or "http://localhost:11434"
        self.client = httpx.AsyncClient(timeout=120.0)
    
    @property
    def provider_name(self) -> str:
        return "ollama"
    
    async def chat_completion(self, system_prompt: str, user_prompt: str) -> str:
        response = await self.client.post(
            f"{self.base_url}/api/chat",
            json={
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "stream": False,
                "options": {"temperature": self.temperature, "num_predict": self.max_tokens}
            }
        )
        response.raise_for_status()
        return response.json()["message"]["content"].strip()


# ============================================
# Groq Provider (Fast inference)
# ============================================

class GroqProvider(BaseLLMProvider):
    """Groq API provider (Fast LLama, Mixtral)"""
    
    def __init__(self, model: str, temperature: float = 0.3, max_tokens: int = 1000):
        super().__init__(model, temperature, max_tokens)
        from groq import AsyncGroq
        self.client = AsyncGroq(api_key=settings.llm_api_key)
    
    @property
    def provider_name(self) -> str:
        return "groq"
    
    async def chat_completion(self, system_prompt: str, user_prompt: str) -> str:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )
        return response.choices[0].message.content.strip()


# ============================================
# Together AI Provider
# ============================================

class TogetherProvider(BaseLLMProvider):
    """Together AI provider"""
    
    def __init__(self, model: str, temperature: float = 0.3, max_tokens: int = 1000):
        super().__init__(model, temperature, max_tokens)
        from together import AsyncTogether
        self.client = AsyncTogether(api_key=settings.llm_api_key)
    
    @property
    def provider_name(self) -> str:
        return "together"
    
    async def chat_completion(self, system_prompt: str, user_prompt: str) -> str:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )
        return response.choices[0].message.content.strip()


# ============================================
# Google AI Provider (Gemini)
# ============================================

class GoogleAIProvider(BaseLLMProvider):
    """Google AI provider (Gemini models)"""
    
    def __init__(self, model: str, temperature: float = 0.3, max_tokens: int = 1000):
        super().__init__(model, temperature, max_tokens)
        import google.generativeai as genai
        genai.configure(api_key=settings.llm_api_key)
        self.genai = genai
        self.model_instance = genai.GenerativeModel(model)
    
    @property
    def provider_name(self) -> str:
        return "google"
    
    async def chat_completion(self, system_prompt: str, user_prompt: str) -> str:
        import asyncio
        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self.model_instance.generate_content(
                full_prompt,
                generation_config={"temperature": self.temperature, "max_output_tokens": self.max_tokens}
            )
        )
        return response.text.strip()


# ============================================
# LLM Provider Factory
# ============================================

def get_llm_provider(
    provider: str = None,
    model: str = None,
    temperature: float = None,
    max_tokens: int = None
) -> BaseLLMProvider:
    """Factory function to get the appropriate LLM provider"""
    provider = provider or settings.llm_provider
    model = model or settings.llm_model
    temperature = temperature if temperature is not None else settings.llm_temperature
    max_tokens = max_tokens or settings.llm_max_tokens
    
    providers = {
        "openai": OpenAIProvider,
        "anthropic": AnthropicProvider,
        "azure": AzureOpenAIProvider,
        "ollama": OllamaProvider,
        "groq": GroqProvider,
        "together": TogetherProvider,
        "google": GoogleAIProvider,
    }
    
    provider_class = providers.get(provider.lower())
    if not provider_class:
        raise ValueError(f"Unknown LLM provider: {provider}. Supported: {list(providers.keys())}")
    
    return provider_class(model=model, temperature=temperature, max_tokens=max_tokens)


# ============================================
# Main LLM Service
# ============================================

class LLMService:
    """
    Dynamic LLM Service for Email Analysis
    Supports multiple providers: OpenAI, Anthropic, Azure, Ollama, Groq, Together, Google
    """
    
    def __init__(self, db: AsyncSession, provider: str = None, model: str = None):
        self.db = db
        
        # Always try to use LLM, fallback to keyword analysis if not configured
        try:
            self.llm_provider = get_llm_provider(provider=provider, model=model)
            print(f"LLM Service initialized: {self.llm_provider.provider_name} ({self.llm_provider.model})")
        except Exception as e:
            print(f"LLM not configured ({e}), will use keyword-based analysis")
            self.llm_provider = None
    
    async def analyze_email(
        self,
        subject: str,
        body: str,
        from_address: str
    ) -> EmailAnalysisResult:
        """
        Analyze an email using the configured LLM to determine:
        1. Is it SAP-related?
        2. Which SAP module (MM, SD, FICO, etc.)?
        3. Suggested priority
        4. Suggested ticket title
        5. Key points
        """
        try:
            # Check if LLM is available
            if self.llm_provider is None:
                return await self._keyword_based_analysis(subject, body)
            
            # Build the prompt
            prompt = self._build_analysis_prompt(subject, body, from_address)
            
            # Call LLM provider
            content = await self.llm_provider.chat_completion(
                system_prompt=SYSTEM_PROMPT,
                user_prompt=prompt
            )
            
            # Parse response
            result_data = self._parse_llm_response(content)
            
            # Convert to schema
            category = None
            if result_data.get("category") and result_data.get("is_sap_related"):
                try:
                    category = TicketCategoryEnum(result_data["category"])
                except ValueError:
                    category = TicketCategoryEnum.OTHER
            
            priority = TicketPriorityEnum.Medium
            if result_data.get("priority"):
                try:
                    priority = TicketPriorityEnum(result_data["priority"])
                except ValueError:
                    pass
            
            return EmailAnalysisResult(
                is_sap_related=result_data.get("is_sap_related", False),
                confidence=result_data.get("confidence", 0.5),
                detected_category=category,
                suggested_title=result_data.get("suggested_title"),
                suggested_priority=priority,
                key_points=result_data.get("key_points", []),
                raw_response=result_data
            )
            
        except Exception as e:
            print(f"LLM analysis error: {e}")
            # Fallback to keyword-based analysis
            return await self._keyword_based_analysis(subject, body)
    
    def _build_analysis_prompt(self, subject: str, body: str, from_address: str) -> str:
        """Build the prompt for email analysis"""
        max_body_length = 3000
        truncated_body = body[:max_body_length] + "..." if len(body) > max_body_length else body
        
        return f"""Analyze this email for SAP support ticket creation:

FROM: {from_address}
SUBJECT: {subject}

BODY:
{truncated_body}

Determine if this is SAP-related, classify the module, assess priority, and suggest a ticket title."""
    
    def _parse_llm_response(self, content: str) -> Dict[str, Any]:
        """Parse the LLM response as JSON"""
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            raise ValueError("Could not parse LLM response as JSON")
    
    async def _keyword_based_analysis(self, subject: str, body: str) -> EmailAnalysisResult:
        """Fallback keyword-based analysis when LLM fails"""
        text = f"{subject} {body}".lower()
        
        # Check if SAP-related
        sap_indicators = ["sap", "erp", "transaction", "t-code", "abap", "fiori", "hana"]
        is_sap_related = any(indicator in text for indicator in sap_indicators)
        
        # Detect category
        detected_category = None
        max_score = 0
        
        for module, keywords in SAP_MODULE_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw.lower() in text)
            if score > max_score:
                max_score = score
                detected_category = module
                is_sap_related = True
        
        # Detect priority
        priority = TicketPriorityEnum.Medium
        for prio, keywords in PRIORITY_INDICATORS.items():
            if any(kw.lower() in text for kw in keywords):
                try:
                    priority = TicketPriorityEnum(prio)
                except ValueError:
                    pass
                break
        
        category_enum = None
        if detected_category:
            try:
                category_enum = TicketCategoryEnum(detected_category)
            except ValueError:
                category_enum = TicketCategoryEnum.OTHER
        
        return EmailAnalysisResult(
            is_sap_related=is_sap_related,
            confidence=0.6 if is_sap_related else 0.4,
            detected_category=category_enum,
            suggested_title=subject[:100] if subject else "Email Inquiry",
            suggested_priority=priority,
            key_points=[],
            raw_response={"method": "keyword_based", "max_score": max_score}
        )
    
    @staticmethod
    def get_available_providers() -> List[str]:
        """Get list of available LLM providers"""
        return ["openai", "anthropic", "azure", "ollama", "groq", "together", "google"]
    
    @staticmethod
    def get_available_models(provider: str) -> List[str]:
        """Get list of available models for a provider"""
        return AVAILABLE_MODELS.get(provider.lower(), [])



