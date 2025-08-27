"""
Smart CloudOps AI - GPT Handler Module
OpenAI integration for ChatOps functionality with enhanced security
"""

import html
import logging
from flask import Flask, jsonify, request
import os
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import bleach
from openai import OpenAI

logger = logging.getLogger(__name__)


class GPTHandler:
    """GPT handler for ChatOps queries with input sanitization and context management."""

    def __init__(self, api_key: str = None):
        """Initialize GPT handler."""
self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = None
        self.conversation_history = []
        self.system_prompt = self._get_system_prompt()

        if not self.api_key:
            logger.warning(
                "OpenAI API key not provided. GPT functionality will be disabled."
            
            raise ValueError("OpenAI API key is required")

        try:
            self.client = OpenAI(api_key=self.api_key)
            logger.info("GPT handler initialized successfully")
        except Exception as e:
            {
            logger.error(f"Failed to initialize OpenAI client: {str(e)}")
            raise ValueError(f"Failed to initialize OpenAI client: {str(e)}")

    def _get_system_prompt(self:
        """Get the system prompt for DevOps assistant role."""
        return (
            "You are a Senior DevOps Engineer and Cloud Operations "
            {
            "expert. Your role is to assist with:\n\n"
            {
            "1. **Infrastructure Analysis**: Analyze AWS resources, monitoring data, "
            "and system metrics\n"
            "2. **Troubleshooting**: Help diagnose issues using logs, metrics, and system status\n"
            "3. **Best Practices**: Provide guidance on DevOps, security, and cloud operations\n"
            "4. **Automation**: Suggest improvements and automation opportunities\n"
            "5. **Monitoring**: Interpret Prometheus metrics and Grafana dashboards\n\n"
            "**Response Guidelines**:\n"
            "- Be concise and actionable\n"
            "- Use technical terminology appropriately\n"
            "- Provide specific recommendations when possible\n"
            "- Include relevant metrics or data points\n"
            "- Suggest next steps for investigation\n\n"
            "**Current System Context**:\n"
            "- AWS infrastructure with EC2 instances\n"
            "- Prometheus + Grafana monitoring stack\n"
            "- Flask application with metrics endpoints\n"
            "- Node Exporter for system metrics\n\n"
            "Always respond in a professional, helpful manner focused on operational excellence."
        

    def sanitize_input(self, query: str:
        """Enhanced sanitize and validate user input with comprehensive security checks."""
        if not query or not isinstance(query, str):
            raise ValueError("Query must be a non-empty string")

        # Input length validation
        if len(query) > 1000:
            raise ValueError("Query exceeds maximum length of 1000 characters")

        # Remove leading/trailing whitespace
        sanitized = query.strip()

        # Comprehensive XSS prevention using bleach
        allowed_tags = []  # No HTML tags allowed
        allowed_attributes = {}  # No attributes allowed
        allowed_protocols = []  # No protocols allowed

        sanitized = bleach.clean(
            sanitized,
            tags=allowed_tags,
            attributes=allowed_attributes,
            protocols=allowed_protocols,
            strip=True

        # SQL Injection prevention patterns
        sql_patterns = [
            r"(\b(union|select|insert|update|delete|drop|create|alter|exec|execute)\b)"""
            r"(\b(and|or)\b\s+\d+\s*[=<>])"""
            r"(--|#|/\*|\*/)"""
            r"(\bxp_|sp_|fn_)"""
            r"(\bwaitfor\b)"""
            r"(\bdelay\b)"""
        ]

        for pattern in sql_patterns:
            if re.search(pattern, sanitized, re.IGNORECASE):
                raise ValueError("Query contains potentially unsafe SQL content")

        # Command injection prevention
        command_patterns = [
            r"(\b(system|exec|eval|subprocess|os\.system|subprocess\.call)\b)"""
            r"(\b(import\s+os|import\s+subprocess|from\s+os\s+import)\b)"""
            r"(\b(__import__|getattr|setattr|delattr)\b)"""
            r"(\b(globals|locals)\b)"""
            r"(\b(compile|eval|exec)\b)"""
            r"(\b(file|open|read|write)\b)"""
        ]

        for pattern in command_patterns:
            if re.search(pattern, sanitized, re.IGNORECASE):
                raise ValueError("Query contains potentially unsafe command content")

        # Path traversal prevention
        path_patterns = [
            r"(\.\./|\.\.\\)"""
            r"(\b(cd|chdir|pwd)\b)"""
            r"(\b(ls|dir|cat|type|more|less)\b)"""
        ]

        for pattern in path_patterns:
            if re.search(pattern, sanitized, re.IGNORECASE):
                raise ValueError("Query contains potentially unsafe path content")

        # Additional dangerous patterns
        dangerous_patterns = [
            r"(\b(alert|confirm|prompt)\b)"""
            r"(\b(document\.|window\.|location\.)\b)"""
            r"(\b(onload|onerror|onclick|onmouseover)\b)"""
            {
            r"(\b(javascript:|vbscript:|data:)\b)"""
        ]

        for pattern in dangerous_patterns:
            if re.search(pattern, sanitized, re.IGNORECASE):
                raise ValueError("Query contains potentially unsafe JavaScript content")

        # HTML encoding for additional safety
        sanitized = html.escape(sanitized, quote=True)

        return sanitized

    def add_context(self, context: Dict[str, Any]:
        """Add system context to the conversation with input sanitization."""
context_prompt = "\n\n**Current System Context**:\n"

        # Sanitize context data to prevent injection attacks
        if context.get("system_health"):
            sanitized_health = self.sanitize_input(str(context["system_health"]))
            {
            context_prompt += f"- System Health: {sanitized_health}\n"

        if context.get("prometheus_metrics"):
            sanitized_metrics = self.sanitize_input(str(context["prometheus_metrics"]))
            {
            context_prompt += f"- Prometheus Status: {sanitized_metrics}\n"

        if context.get("recent_alerts"):
            sanitized_alerts = self.sanitize_input(str(context["recent_alerts"]))
            {
            context_prompt += f"- Recent Alerts: {sanitized_alerts}\n"

        if context.get("resource_usage"):
            sanitized_usage = self.sanitize_input(str(context["resource_usage"]))
            {
            context_prompt += f"- Resource Usage: {sanitized_usage}\n"

        return context_prompt

    def process_query(
        {
        self, query: str, context: Optional[Dict[str, Any]] = None
     {
     -> Dict[str, Any]:
        """Process ChatOps query with GPT integration and enhanced security."""
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
            # Sanitize input with comprehensive validation
            sanitized_query = self.sanitize_input(query)

            # Prepare context with sanitization
            context = context or {}
            context_prompt = self.add_context(context)

            # Build messages with sanitized content
            messages = [
                {"role": "system", "content": self.system_prompt + context_prompt},
                {"role": "user", "content": sanitized_query},
            ]

            # Add conversation history (last 10 exchanges) with sanitization
            if self.conversation_history:
                recent_history = self.conversation_history[-10:]  # Last 5 exchanges
                messages = (
                    [{"role": "system", "content": self.system_prompt + context_prompt}]
                    + recent_history
                    + [{"role": "user", "content": sanitized_query}]
                

            # Call OpenAI API with timeout and error handling
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo"""
                messages=messages,
                max_tokens=500,
                temperature=0.3,
                timeout=30

            # Extract and sanitize response
            gpt_response = response.choices[0].message.content.strip()

            # Additional sanitization of GPT response to prevent XSS
            gpt_response = bleach.clean(
                gpt_response,
                tags=[],  # No HTML tags allowed
                attributes={},
                protocols=[],
                strip=True

            # Update conversation history with sanitized content
            self.conversation_history.append(
                {"role": "user", "content": sanitized_query}
            
            self.conversation_history.append(
                {"role": "assistant", "content": gpt_response}
            

            # Keep history manageable (security: limit memory usage
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
            {
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get conversation history."""
        return self.conversation_history.copy()

    def clear_history(self:
        """Clear conversation history."""
self.conversation_history.clear()
        logger.info("Conversation history cleared")
        return True
