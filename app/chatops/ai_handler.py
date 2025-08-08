"""
Smart CloudOps AI - Flexible AI Handler
Supports both OpenAI and Google Gemini APIs
"""

import os
import re
import logging
from typing import Dict, Any, Optional, List, Union
from datetime import datetime, timezone
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class AIProvider(ABC):
    """Abstract base class for AI providers."""

    @abstractmethod
    def initialize(self, api_key: str) -> bool:
        """Initialize the AI provider."""
        pass

    @abstractmethod
    def process_query(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """Process a query with the AI provider."""
        pass

    @abstractmethod
    def get_model_info(self) -> Dict[str, str]:
        """Get information about the current model."""
        pass


class OpenAIProvider(AIProvider):
    """OpenAI GPT provider implementation."""

    def __init__(self):
        self.client = None
        self.model = "gpt-3.5-turbo"

    def initialize(self, api_key: str) -> bool:
        """Initialize OpenAI client."""
        try:
            from openai import OpenAI

            self.client = OpenAI(api_key=api_key)
            logger.info("OpenAI provider initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI provider: {str(e)}")
            return False

    def process_query(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """Process query with OpenAI."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=kwargs.get("max_tokens", 500),
                temperature=kwargs.get("temperature", 0.3),
                timeout=kwargs.get("timeout", 30),
            )

            return {
                "status": "success",
                "response": response.choices[0].message.content.strip(),
                "model": self.model,
                "tokens_used": response.usage.total_tokens if response.usage else None,
                "provider": "openai",
            }
        except Exception as e:
            logger.error(f"OpenAI query failed: {str(e)}")
            return {"status": "error", "error": str(e), "provider": "openai"}

    def get_model_info(self) -> Dict[str, str]:
        """Get OpenAI model information."""
        return {"provider": "openai", "model": self.model, "name": "GPT-3.5 Turbo"}


class GeminiProvider(AIProvider):
    """Google Gemini provider implementation."""

    def __init__(self):
        self.client = None
        self.model = "gemini-1.5-pro"

    def initialize(self, api_key: str) -> bool:
        """Initialize Gemini client."""
        try:
            import google.generativeai as genai

            genai.configure(api_key=api_key)
            self.client = genai.GenerativeModel(self.model)
            logger.info("Gemini provider initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Gemini provider: {str(e)}")
            return False

    def process_query(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """Process query with Gemini."""
        try:
            # Convert OpenAI format to Gemini format
            gemini_messages = self._convert_messages(messages)

            import google.generativeai as genai

            response = self.client.generate_content(
                gemini_messages,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=kwargs.get("max_tokens", 500),
                    temperature=kwargs.get("temperature", 0.3),
                ),
            )

            return {
                "status": "success",
                "response": response.text.strip(),
                "model": self.model,
                "tokens_used": response.usage_metadata.total_token_count
                if hasattr(response, "usage_metadata")
                else None,
                "provider": "gemini",
            }
        except Exception as e:
            logger.error(f"Gemini query failed: {str(e)}")
            return {"status": "error", "error": str(e), "provider": "gemini"}

    def _convert_messages(self, messages: List[Dict[str, str]]) -> str:
        """Convert OpenAI message format to Gemini format."""
        converted = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")

            if role == "system":
                converted.append(f"System: {content}")
            elif role == "user":
                converted.append(f"User: {content}")
            elif role == "assistant":
                converted.append(f"Assistant: {content}")

        return "\n\n".join(converted)

    def get_model_info(self) -> Dict[str, str]:
        """Get Gemini model information."""
        return {"provider": "gemini", "model": self.model, "name": "Gemini 1.5 Pro"}


class FlexibleAIHandler:
    """Flexible AI handler supporting multiple providers."""

    def __init__(self, provider: str = "auto"):
        """
        Initialize AI handler.

        Args:
            provider: "openai", "gemini", or "auto" (detects based on available API keys)
        """
        self.provider_name = provider
        self.provider = None
        self.system_prompt = self._get_system_prompt()
        self.conversation_history: List[Dict[str, str]] = []

        # Initialize provider
        self._initialize_provider()

    def _initialize_provider(self):
        """Initialize the appropriate AI provider."""
        if self.provider_name == "auto":
            # Try to detect available provider
            if os.getenv("OPENAI_API_KEY"):
                self.provider_name = "openai"
            elif os.getenv("GEMINI_API_KEY"):
                self.provider_name = "gemini"
            else:
                logger.warning("No AI provider API keys found")
                return

        if self.provider_name == "openai":
            self.provider = OpenAIProvider()
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                self.provider.initialize(api_key)
        elif self.provider_name == "gemini":
            self.provider = GeminiProvider()
            api_key = os.getenv("GEMINI_API_KEY")
            if api_key:
                self.provider.initialize(api_key)
        else:
            logger.error(f"Unknown provider: {self.provider_name}")

    def _get_system_prompt(self) -> str:
        """Get the system prompt for DevOps assistant role."""
        return """You are a Senior DevOps Engineer and Cloud Operations expert. Your role is to assist with:

1. **Infrastructure Analysis**: Analyze AWS resources, monitoring data, and system metrics
2. **Troubleshooting**: Help diagnose issues using logs, metrics, and system status
3. **Best Practices**: Provide guidance on DevOps, security, and cloud operations
4. **Automation**: Suggest improvements and automation opportunities
5. **Monitoring**: Interpret Prometheus metrics and Grafana dashboards

**Response Guidelines**:
- Be concise and actionable
- Use technical terminology appropriately
- Provide specific recommendations when possible
- Include relevant metrics or data points
- Suggest next steps for investigation

**Current System Context**:
- AWS infrastructure with EC2 instances
- Prometheus + Grafana monitoring stack
- Flask application with metrics endpoints
- Node Exporter for system metrics

Always respond in a professional, helpful manner focused on operational excellence."""

    def sanitize_input(self, query: str) -> str:
        """Sanitize and validate user input."""
        if not query or not isinstance(query, str):
            raise ValueError("Query must be a non-empty string")

        # Remove potentially dangerous characters and patterns
        sanitized = query.strip()

        # Remove script tags and their content
        sanitized = re.sub(
            r"<script[^>]*>.*?</script>", "", sanitized, flags=re.IGNORECASE | re.DOTALL
        )

        # Remove alert calls
        sanitized = re.sub(r"alert\s*\([^)]*\)", "", sanitized, flags=re.IGNORECASE)

        # Remove other dangerous characters
        sanitized = re.sub(r'[<>"]', "", sanitized)

        # Limit query length
        if len(sanitized) > 1000:
            sanitized = sanitized[:1000] + "..."

        # Basic injection prevention
        dangerous_patterns = [
            r"system\s*\(",
            r"eval\s*\(",
            r"exec\s*\(",
            r"import\s+os",
            r"__import__",
        ]

        for pattern in dangerous_patterns:
            if re.search(pattern, sanitized, re.IGNORECASE):
                raise ValueError("Query contains potentially unsafe content")

        return sanitized

    def add_context(self, context: Dict[str, Any]) -> str:
        """Add system context to the conversation."""
        context_prompt = "\n\n**Current System Context**:\n"

        if context.get("system_health"):
            context_prompt += f"- System Health: {context['system_health']}\n"

        if context.get("prometheus_metrics"):
            context_prompt += f"- Prometheus Status: {context['prometheus_metrics']}\n"

        if context.get("recent_alerts"):
            context_prompt += f"- Recent Alerts: {context['recent_alerts']}\n"

        if context.get("resource_usage"):
            context_prompt += f"- Resource Usage: {context['resource_usage']}\n"

        return context_prompt

    def process_query(
        self, query: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process ChatOps query with AI integration."""
        try:
            # Check if AI provider is available
            if not self.provider:
                return {
                    "status": "error",
                    "error": "AI functionality not available",
                    "message": f"No AI provider configured. Set {self.provider_name.upper()}_API_KEY environment variable.",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }

            # Sanitize input
            sanitized_query = self.sanitize_input(query)

            # Prepare context
            context = context or {}
            context_prompt = self.add_context(context)

            # Build messages
            messages = [
                {"role": "system", "content": self.system_prompt + context_prompt},
                {"role": "user", "content": sanitized_query},
            ]

            # Add conversation history (last 10 messages)
            if self.conversation_history:
                recent_history = self.conversation_history[-10:]
                messages = (
                    [{"role": "system", "content": self.system_prompt + context_prompt}]
                    + recent_history
                    + [{"role": "user", "content": sanitized_query}]
                )

            # Process with AI provider
            result = self.provider.process_query(messages)

            if result["status"] == "success":
                # Update conversation history
                self.conversation_history.append(
                    {"role": "user", "content": sanitized_query}
                )
                self.conversation_history.append(
                    {"role": "assistant", "content": result["response"]}
                )

                # Keep history manageable
                if len(self.conversation_history) > 20:
                    self.conversation_history = self.conversation_history[-20:]

                logger.info(
                    f"Successfully processed query with {self.provider_name}: {sanitized_query[:50]}..."
                )

                return {
                    "status": "success",
                    "response": result["response"],
                    "query": sanitized_query,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "model": result.get("model", "unknown"),
                    "provider": result.get("provider", self.provider_name),
                    "tokens_used": result.get("tokens_used"),
                }
            else:
                return {
                    "status": "error",
                    "error": result.get("error", "Unknown error"),
                    "message": "AI processing failed",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "provider": result.get("provider", self.provider_name),
                }

        except ValueError as e:
            logger.warning(f"Input validation error: {str(e)}")
            return {
                "status": "error",
                "error": "Invalid input",
                "message": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        except Exception as e:
            logger.error(f"AI processing error: {str(e)}")
            return {
                "status": "error",
                "error": "Processing failed",
                "message": "Unable to process query at this time",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get conversation history."""
        return self.conversation_history.copy()

    def clear_history(self) -> bool:
        """Clear conversation history."""
        self.conversation_history.clear()
        logger.info("Conversation history cleared")
        return True

    def get_provider_info(self) -> Dict[str, Any]:
        """Get information about the current AI provider."""
        if self.provider:
            return {
                "provider": self.provider_name,
                "available": True,
                "model_info": self.provider.get_model_info(),
            }
        else:
            return {
                "provider": self.provider_name,
                "available": False,
                "model_info": None,
            }
