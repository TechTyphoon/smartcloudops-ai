"""
Smart CloudOps AI - GPT Handler Module
OpenAI integration for ChatOps functionality
"""

import logging
import os
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from openai import OpenAI

logger = logging.getLogger(__name__)


class GPTHandler:
    """GPT handler for ChatOps queries with input sanitization and
    context management."""

    def __init__(self, api_key: str = None):
        """Initialize GPT handler."""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = None
        self.conversation_history = []
        self.system_prompt = self._get_system_prompt()

        if not self.api_key:
            logger.warning(
                "OpenAI API key not provided. GPT functionality will be disabled."
            )
            raise ValueError("OpenAI API key is required")

        try:
            self.client = OpenAI(api_key=self.api_key)
            logger.info("GPT handler initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {str(e)}")
            raise ValueError(f"Failed to initialize OpenAI client: {str(e)}")

    def _get_system_prompt(self) -> str:
        """Get the system prompt for DevOps assistant role."""
        return (
            """You are a Senior DevOps Engineer and Cloud Operations """
            """expert. Your role is to assist with:

1. **Infrastructure Analysis**: Analyze AWS resources, monitoring data, """
            """and system metrics
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
        )

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
        """Process ChatOps query with GPT integration."""
        try:
            # Check if GPT client is available
            if not self.client:
                return {
                    "status": "error",
                    "error": "GPT functionality not available",
                    "message": (
                        "OpenAI API key not configured. Please set OPENAI_API_KEY "
                        "environment variable."
                    ),
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

            # Add conversation history (last 5 exchanges)
            if self.conversation_history:
                recent_history = self.conversation_history[-10:]  # Last 5 exchanges
                messages = (
                    [{"role": "system", "content": self.system_prompt + context_prompt}]
                    + recent_history
                    + [{"role": "user", "content": sanitized_query}]
                )

            # Call OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=500,
                temperature=0.3,
                timeout=30,
            )

            # Extract response
            gpt_response = response.choices[0].message.content.strip()

            # Update conversation history
            self.conversation_history.append(
                {"role": "user", "content": sanitized_query}
            )
            self.conversation_history.append(
                {"role": "assistant", "content": gpt_response}
            )

            # Keep history manageable
            if len(self.conversation_history) > 20:
                self.conversation_history = self.conversation_history[-20:]

            logger.info(f"Successfully processed query: {sanitized_query[:50]}...")

            return {
                "status": "success",
                "response": gpt_response,
                "query": sanitized_query,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "model": "gpt-3.5-turbo",
                "tokens_used": response.usage.total_tokens if response.usage else None,
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
            logger.error(f"GPT processing error: {str(e)}")
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
