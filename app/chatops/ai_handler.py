#!/usr/bin/env python3
"""
Smart CloudOps AI - Flexible AI Handler
Supports both OpenAI and Google Gemini APIs
"""

import logging
import os
import re
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from flask import Flask, jsonify, request

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
                "response": "I can help you monitor system resources. Here are the current metrics:\n- CPU Usage: 45%\n- Memory Usage: 62%\n- Disk Usage: 78%\n- Load Average: 1.2",
                "tokens_used": 25,
            }

        # Deployment responses
        elif any(word in query_lower for word in ["deploy", "deployment", "release"]):
            return {
                "response": "I can assist with deployments. Current deployment status:\n- Production: Stable\n- Staging: Ready for deployment\n- Development: In progress\n\nWould you like me to initiate a deployment?",
                "tokens_used": 30,
            }

        # Security responses
        elif any(word in query_lower for word in ["security", "vulnerability", "scan"]):
            return {
                "response": "Security scan results:\n- No critical vulnerabilities found\n- 2 medium priority issues detected\n- All security patches are up to date\n\nRecommendation: Review the medium priority issues.",
                "tokens_used": 28,
            }

        # General DevOps responses
        elif any(word in query_lower for word in ["devops", "pipeline", "ci/cd"]):
            return {
                "response": "DevOps pipeline status:\n- Build: ✅ Passing\n- Test: ✅ Passing\n- Deploy: ✅ Successful\n- Monitoring: ✅ Active\n\nAll systems are operational.",
                "tokens_used": 22,
            }

        # Default response
        else:
            return {
                "response": "I'm your DevOps assistant. I can help with:\n- System monitoring and metrics\n- Deployment management\n- Security scanning and alerts\n- Pipeline status and troubleshooting\n- Performance optimization\n\nWhat would you like to know?",
                "tokens_used": 35,
            }

    def get_model_info(self) -> Dict[str, str]:
        """Get local model information."""
        return {"provider": "local", "model": self.model, "name": "Local Assistant"}


class AIHandler:
    """Main AI handler that manages different providers."""

    def __init__(self, provider_type: str = "local", api_key: str = None):
        """Initialize AI handler with specified provider."""
        self.provider_type = provider_type
        self.provider = None
        self.conversation_history = []
        self.max_history = 50

        # Initialize the provider
        if provider_type == "openai":
            self.provider = OpenAIProvider()
        else:
            self.provider = LocalProvider()

        if api_key:
            self.provider.initialize(api_key)
        else:
            self.provider.initialize()

    def process_message(
        self, message: str, context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Process a user message and return AI response."""
        try:
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
                        -self.max_history :
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
                "provider": self.provider_type,
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

    def get_provider_info(self) -> Dict[str, str]:
        """Get information about the current provider."""
        if self.provider:
            return self.provider.get_model_info()
        return {"provider": "none", "model": "none", "name": "No provider"}


# Global AI handler instance
ai_handler = AIHandler()
