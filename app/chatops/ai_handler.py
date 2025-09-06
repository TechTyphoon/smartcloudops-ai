#!/usr/bin/env python3
"""
Smart CloudOps AI - Flexible AI Handler
Supports both OpenAI and Google Gemini APIs
"""

import logging
import os
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class AIProvider(ABC):
    """Abstract base class for AI providers."""

    @abstractmethod
    def initialize(self, api_key: str) -> bool:
        """Initialize the AI provider."""

    @abstractmethod
    def process_query(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """Process a query with the AI provider."""

    @abstractmethod
    def get_model_info(self) -> Dict[str, str]:
        """Get information about the current model."""


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


class LocalProvider(AIProvider):
    """Local AI provider for testing and development."""

    def __init__(self):
        self.model = "local-assistant"

    def initialize(self, api_key: str = None) -> bool:
        """Initialize local provider (no API key needed)."""
        logger.info("Local AI provider initialized successfully")
        return True

    def process_query(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """Process query with local responses."""
        try:
            # Get the user query from messages
            user_message = ""
            for message in messages:
                if message.get("role") == "user":
                    user_message = message.get("content", "")
                    break

            # Generate contextual responses based on query content
            response_data = self._generate_enhanced_response(user_message.lower())

            return {
                "status": "success",
                "response": response_data["response"],
                "model": self.model,
                "tokens_used": response_data.get("tokens_used", 0),
                "provider": "local",
            }
        except Exception as e:
            logger.error(f"Local query failed: {str(e)}")
            return {"status": "error", "error": str(e), "provider": "local"}

    def _generate_enhanced_response(self, query: str) -> Dict[str, Any]:
        """Generate enhanced local responses."""
        query_lower = query.lower()

        # System monitoring responses
        if any(word in query_lower for word in ["cpu", "memory", "disk", "load"]):
            return {
                "response": "I can help you monitor system resources. Here are the "
                "current metrics:\n- CPU Usage: 45%\n- Memory Usage: 62%\n- "
                "Disk Usage: 78%\n- Load Average: 1.2",
                "tokens_used": 25,
            }

        # Deployment responses
        elif any(word in query_lower for word in ["deploy", "deployment", "release"]):
            return {
                "response": (
                    "I can assist with deployments. Current deployment status:\n"
                    "- Production: Stable\n- Staging: Ready for deployment\n- "
                    "Development: In progress\n\n"
                    "Would you like me to initiate a deployment?"
                ),
                "tokens_used": 30,
            }

        # Security responses
        elif any(word in query_lower for word in ["security", "vulnerability", "scan"]):
            return {
                "response": (
                    "Security scan results:\n- No critical vulnerabilities found\n"
                    "- 2 medium priority issues detected\n- All security patches are "
                    "up to date\n\n"
                    "Recommendation: Review the medium priority issues."
                ),
                "tokens_used": 28,
            }

        # General DevOps responses
        elif any(word in query_lower for word in ["devops", "pipeline", "ci/cd"]):
            return {
                "response": (
                    "DevOps pipeline status:\n- Build: ✅ Passing\n"
                    "- Test: ✅ Passing\n"
                    "- Deploy: ✅ Successful\n- Monitoring: ✅ Active\n\n"
                    "All systems are operational."
                ),
                "tokens_used": 22,
            }

        # Default response
        else:
            return {
                "response": "I'm your DevOps assistant. I can help with:\n"
                "- System monitoring and metrics\n- Deployment management\n"
                "- Security scanning and alerts\n- Pipeline status and "
                "troubleshooting\n"
                "- Performance optimization\n\nWhat would you like to "
                "know?",
                "tokens_used": 35,
            }

    def get_model_info(self) -> Dict[str, str]:
        """Get local model information."""
        return {"provider": "local", "model": self.model, "name": "Local Assistant"}


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
        except ImportError:
            logger.warning(
                "google.generativeai not available, Gemini provider will not work"
            )
            return False
        except Exception as e:
            logger.error(f"Failed to initialize Gemini provider: {str(e)}")
            return False

    def process_query(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """Process query with Gemini."""
        try:
            if not self.client:
                return {"status": "error", "error": "Gemini client not initialized"}

            # Convert messages to Gemini format
            prompt = self._convert_messages(messages)

            response = self.client.generate_content(prompt)

            return {
                "status": "success",
                "response": response.text,
                "model": self.model,
                "tokens_used": len(prompt.split()) * 2,  # Rough estimate
                "provider": "gemini",
            }
        except Exception as e:
            logger.error(f"Gemini query failed: {str(e)}")
            return {"status": "error", "error": str(e), "provider": "gemini"}

    def get_model_info(self) -> Dict[str, str]:
        """Get Gemini model information."""
        return {
            "provider": "gemini",
            "model": self.model,
            "name": "Gemini 1.5 Pro",
        }

    def _convert_messages(self, messages: List[Dict[str, str]]) -> str:
        """Convert chat messages to Gemini prompt format."""
        converted_parts = []

        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")

            if role == "system":
                converted_parts.append(f"System: {content}")
            elif role == "user":
                converted_parts.append(f"User: {content}")
            elif role == "assistant":
                converted_parts.append(f"Assistant: {content}")

        return "\n\n".join(converted_parts)


class FlexibleAIHandler:
    """Main AI handler that manages different providers."""

    def __init__(self, provider: str = "local", api_key: str = None):
        """Initialize AI handler with specified provider."""
        self.provider_name = provider
        self.provider = None
        self.conversation_history = []
        self.max_history = 50

        # Initialize the provider
        if provider == "openai":
            self.provider = OpenAIProvider()
        elif provider == "gemini":
            self.provider = GeminiProvider()
        else:
            self.provider = LocalProvider()

        if api_key:
            self.provider.initialize(api_key)
        else:
            # Try to initialize with environment variables
            self._initialize_from_env()

    def _initialize_from_env(self):
        """Initialize provider from environment variables."""
        if self.provider_name == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                self.provider.initialize(api_key)
        elif self.provider_name == "gemini":
            api_key = os.getenv("GEMINI_API_KEY")
            if api_key:
                self.provider.initialize(api_key)
        # Local provider doesn't need initialization

    def process_query(
        self, query: str, context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Process a user query and return AI response."""
        return self.process_message(query, context)

    def process_message(
        self, message: str, context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Process a user message and return AI response."""
        try:
            # Check if provider is available
            if not self.provider:
                return {
                    "status": "error",
                    "error": "AI functionality not available",
                    "provider": "none",
                }

            # Add user message to history
            self.conversation_history.append(
                {
                    "role": "user",
                    "content": message,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            )

            # Prepare messages for AI provider
            messages = [{"role": "user", "content": message}]

            # Add context if provided
            if context:
                context_message = f"Context: {context}"
                messages.insert(0, {"role": "system", "content": context_message})

            # Process with AI provider
            response = self.provider.process_query(messages)

            if response["status"] == "success":
                # Add AI response to history
                self.conversation_history.append(
                    {
                        "role": "assistant",
                        "content": response["response"],
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    }
                )

                # Trim history if too long
                if len(self.conversation_history) > self.max_history:
                    self.conversation_history = self.conversation_history[
                        -self.max_history:
                    ]

                return {
                    "status": "success",
                    "response": response["response"],
                    "model": response.get("model", "unknown"),
                    "tokens_used": response.get("tokens_used", 0),
                    "provider": response.get("provider", "unknown"),
                }
            else:
                return response

        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return {
                "status": "error",
                "error": f"Failed to process message: {str(e)}",
                "provider": self.provider_name,
            }

    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get conversation history."""
        return self.conversation_history.copy()

    def clear_history(self) -> bool:
        """Clear conversation history."""
        try:
            self.conversation_history.clear()
            return True
        except Exception as e:
            logger.error(f"Failed to clear history: {str(e)}")
            return False

    def sanitize_input(self, query: str) -> str:
        """Sanitize user input to prevent injection attacks."""
        if not isinstance(query, str):
            raise ValueError("Query must be a non-empty string")

        if not query.strip():
            raise ValueError("Query must be a non-empty string")

        # Check for dangerous patterns
        dangerous_patterns = [
            "system(",
            "exec(",
            "eval(",
            "import os",
            "import subprocess",
            "__import__",
            "open(",
            "file(",
        ]

        query_lower = query.lower()
        for pattern in dangerous_patterns:
            if pattern in query_lower:
                raise ValueError("Query contains potentially unsafe content")

        # Use bleach for HTML sanitization if available
        try:
            import bleach

            # Configure bleach to remove script content
            sanitized = bleach.clean(
                query,
                tags=[],  # Remove all tags
                attributes={},  # Remove all attributes
                strip=True,  # Strip tags
                strip_comments=True,  # Remove comments
            )
            # Additional cleanup for script content that bleach might miss
            import re

            sanitized = re.sub(
                r"alert\s*\([^)]*\)|javascript\s*:|on\w+\s*=",
                "",
                sanitized,
                flags=re.IGNORECASE,
            )
        except ImportError:
            # Fallback: basic HTML tag removal
            import re

            # Start with the original query
            sanitized = query

            # Remove script tags and their content (improved regex)
            sanitized = re.sub(
                r"<script[^>]*>[\s\S]*?</script>", "", sanitized, flags=re.IGNORECASE
            )
            # Also remove any remaining script content without tags
            sanitized = re.sub(
                r"alert\s*\([^)]*\)|javascript\s*:|on\w+\s*=",
                "",
                sanitized,
                flags=re.IGNORECASE,
            )
            # Remove other HTML tags
            sanitized = re.sub(r"<[^>]+>", "", sanitized)

        # Limit input length
        max_length = 1000
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length] + "..."

        return sanitized

    def analyze_query(self, query: str) -> Dict[str, Any]:
        """Analyze query intent and return analysis."""
        try:
            # Sanitize input
            sanitized_query = self.sanitize_input(query)

            # Simple intent analysis based on keywords
            query_lower = sanitized_query.lower()

            if any(
                word in query_lower
                for word in ["status", "health", "system", "summary"]
            ):
                intent = "system_status"
            elif any(word in query_lower for word in ["log", "logs", "error", "debug"]):
                intent = "log_analysis"
            elif any(word in query_lower for word in ["deploy", "deployment", "build"]):
                intent = "deployment"
            elif any(
                word in query_lower for word in ["monitor", "metrics", "performance"]
            ):
                intent = "monitoring"
            elif any(
                word in query_lower for word in ["config", "configuration", "settings"]
            ):
                intent = "configuration"
            else:
                intent = "general_query"

            return {
                "intent": intent,
                "query": sanitized_query,
                "confidence": 0.8,  # Placeholder confidence score
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

        except Exception as e:
            logger.error(f"Error analyzing query: {str(e)}")
            return {
                "intent": "unknown",
                "error": str(e),
                "query": query,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

    def get_provider_info(self) -> Dict[str, Any]:
        """Get information about the current provider."""
        if self.provider:
            model_info = self.provider.get_model_info()
            # Check if provider is actually available (has API key or works)
            available = self._check_provider_availability()
            return {
                "provider": model_info.get("provider", "unknown"),
                "available": available,
                "model_info": model_info,
            }
        return {
            "provider": "none",
            "available": False,
            "model_info": None,
        }

    def _check_provider_availability(self) -> bool:
        """Check if the current provider is available and working."""
        if not self.provider:
            return False

        try:
            # Try a simple test to see if the provider works
            if self.provider_name == "openai":
                return os.getenv("OPENAI_API_KEY") is not None
            elif self.provider_name == "gemini":
                return os.getenv("GEMINI_API_KEY") is not None
            else:  # local
                return True  # Local provider is always available
        except Exception:
            return False


# Global AI handler instance
ai_handler = FlexibleAIHandler()
