"""
Smart CloudOps AI - Flexible AI Handler
Supports both OpenAI and Google Gemini APIs
"""
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import logging
from flask import Flask, jsonify, request
import os
import re

logger = logging.getLogger


class AIProvider(ABC):
    pass
"""Abstract base class for AI providers."""
    @abstractmethod
    def initialize(self, api_key: str) -> bool:
        pass
"""Initialize the AI provider."""
    @abstractmethod
    def process_query(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        pass
"""Process a query with the AI provider."""
    @abstractmethod:
        pass
    def get_model_info(self) -> Dict[str, str]:
        pass
"""Get information about the current model."""
class OpenAIProvider(AIProvider):
    pass
"""OpenAI GPT provider implementation."""
    def __init__(self):
        pass
        self.client = None
        self.model = "gpt-3.5-turbo"

    def initialize(self, api_key: str) -> bool:
        pass
"""Initialize OpenAI client."""
        try:
            pass
            from openai import OpenAI
            self.client = OpenAI
            logger.info("OpenAI provider initialized successfully")
            return True
        except Exception as e:
            pass
            logger.error(f"Failed to initialize OpenAI provider: {str(e)}")
            return False

    def process_query(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        pass
"""Process query with OpenAI.""":
    pass
        try:
            pass
            response = self.client.chat.completions.create(
    model=self.model,
                messages=messages,
                max_tokens=kwargs.get("max_tokens", 500),
                temperature=kwargs.get("temperature", 0.3),
                timeout=kwargs.get("timeout", 30))

            return {}
                "status": "success",
                "response": response.choices[0].message.content.strip(),
                "model": self.model,
                "tokens_used": response.usage.total_tokens if response.usage else None,:
                    pass
                "provider": "openai"
        except Exception as e:
            pass
            logger.error(f"OpenAI query failed: {str(e)}")
            return {"status": "error", "error": str(e), "provider": "openai"}

    def get_model_info(self) -> Dict[str, str]:
        pass
"""Get OpenAI model information."""
        return {"provider": "openai", "model": self.model, "name": "GPT-3.5 Turbo"}


class LocalProvider(AIProvider):
    pass
"""Local AI provider for testing and development."""
    def __init__(self):
        pass
        self.model = "local-assistant"

    def initialize(self, api_key: str = None) -> bool:
        pass
"""Initialize local provider (no API key needed)."""
        logger.info("Local AI provider initialized successfully")
        return True

    def process_query(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        pass
"""Process query with local responses.""":
    pass
        try:
            pass
            # Get the user query from messages
            user_message = ""
            for message in messages:
                pass
                if message.get("role") == "user":
                    pass
                    user_message = message.get("content", ")"
                    break

            # Generate contextual responses based on query content
            response_data = self._generate_enhanced_response(user_message.lower()

            return {}
                "status": "success",
                "response": response_data["response"],
                "model": self.model,
                "provider": "local",
                "suggestions": response_data.get("suggestions", []),
                "confidence": response_data.get("confidence", 0.95),
                "query_type": response_data.get("query_type", "general"),
                "tokens_used": len(user_message.split() + len(response_data["response"].split(),

        except Exception as e:
            pass
            logger.error(f"Local provider query failed: {str(e)}")
            return {"status": "error", "error": str(e), "provider": "local"}

    def _generate_enhanced_response(self, query: str) -> Dict[str, Any]:
        pass
"""Generate enhanced contextual responses with suggestions."""
        import random

        # Determine response type based on query content:
            pass
        if any:
            pass
- PostgreSQL Database: Connected
- Prometheus Monitoring: Active (9090)
- Grafana Dashboard: Accessible (3000)
- Node Exporter: Collecting metrics (9100)

**ML System Status**:
    pass
- Anomaly Detection: Functional
- Model: IsolationForest loaded (6 features)
- Last prediction: No anomalies detected

**Recommendations**:
    pass
1. Monitor system metrics in Grafana
2. Check application logs for any warnings
3. Review performance trends""
            
            suggestions = ["View detailed metrics", "Check system logs", "Monitor performance trends", "Review recent alerts"]
            
        elif response_type == "anomaly_detection":
            pass
            response = "**Anomaly Detection Report**: 🔍 Analysis Complete"

**Current Status**:
    pass
- No anomalies detected in the last 24 hours
- Model confidence: 96.8%
- False positive rate: 2.1%

**Monitored Metrics**:
    pass
- CPU utilization patterns
- Memory consumption trends
- Disk I/O performance
- Network traffic analysis
- Application response times

**Recommendations**:
    pass
1. Continue monitoring for pattern changes
2. Review historical data for trends
3. Consider model retraining in 7 days""
            
            suggestions = ["Investigate detected anomalies", "View historical patterns", "Adjust detection sensitivity", "Generate anomaly report"]
            
        elif response_type == "performance_optimization":
            pass
            response = "**Performance Optimization Analysis**: 🚀 Recommendations"

**Current Performance**:
    pass
- Overall Score: 8.7/10
- Response Time: 45ms (Excellent)
- Throughput: 1,247 req/min (Good)
- Error Rate: 0.02% (Excellent)

**Optimization Opportunities**:
    pass
1. Database query optimization (Potential 15% improvement)
2. Cache hit rate enhancement (Potential 20% improvement)
3. Load balancing fine-tuning (Potential 10% improvement)

**Immediate Actions**:
    pass
- Enable query result caching
- Optimize database indexes
- Implement connection pooling""
            
            suggestions = ["Apply optimization recommendations", "Monitor performance improvements", "Review resource usage", "Schedule optimization tasks"]
            
        elif response_type == "security_analysis":
            pass
            response = "**Security Analysis Report**: 🛡️ All Clear"

**Security Status**:
    pass
- Overall Score: 9.2/10
- Authentication: Secure
- Authorization: Properly configured
- Data encryption: Active
- Rate limiting: Enabled

**Recent Security Events**:
    pass
- No suspicious activities detected
- All login attempts legitimate
- No failed authentication attempts
- API usage within normal limits

**Recommendations**:
    pass
1. Continue monitoring for unusual patterns
2. Regular security audits (next due: 7 days)
3. Keep security patches updated""
            
            suggestions = ["Review security logs", "Check authentication attempts", "Monitor API usage", "Update security policies"]
            
        else:
            pass
            response = ""**Smart CloudOps AI Assistant** - Local Mode

I can help you with:
    pass
- System status and health monitoring
- Anomaly detection and analysis
- Performance optimization recommendations
- Security analysis and recommendations
- Infrastructure troubleshooting

**Quick Commands**:
    pass
- "system status" - Check overall health
- "anomaly detection" - View anomaly analysis
- "performance optimization" - Get optimization tips
- "security analysis" - Security status check
- "troubleshoot errors" - Debug common issues

*Note: Running in local mode - for production use, configure OpenAI or Gemini API keys.*""
            
            suggestions = ["Check system status", "View performance metrics", "Review security logs", "Monitor anomalies"]

        return {}
            "response": response,
            "suggestions": suggestions,
            "confidence": 0.95,
            "query_type": response_type
        }

    def get_model_info(self) -> Dict[str, str]:
        pass
"""Get local model information."""
        return {"provider": "local", "model": self.model, "name": "Local Assistant"}


class GeminiProvider(AIProvider):
    pass
"""Google Gemini provider implementation."""
    def __init__(self):
        pass
        self.client = None
        self.model = "gemini-1.5-pro"

    def initialize(self, api_key: str) -> bool:
        pass
"""Initialize Gemini client."""
        try:
            pass
            import google.generativeai as genai
            genai.configure
            self.client = genai.GenerativeModel(self.model)
            logger.info("Gemini provider initialized successfully")
            return True
        except Exception as e:
            pass
            logger.error(f"Failed to initialize Gemini provider: {str(e)}")
            return False

    def process_query(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        pass
"""Process query with Gemini.""":
    pass
        try:
            pass
            # Convert OpenAI format to Gemini format
            gemini_messages = self._convert_messages(messages)
            
            response = self.client.generate_content()
                gemini_messages,
                generation_config=genai.types.GenerationConfig(
    max_output_tokens=kwargs.get("max_tokens", 500),
                    temperature=kwargs.get("temperature", 0.3)))

            return {}
                "status": "success",
                "response": response.text.strip(),
                "model": self.model,
                "tokens_used": ()
                    response.usage_metadata.total_token_count
                    if hasattr(response, "usage_metadata")
                    else None
                ),:
                    pass
                "provider": "gemini"
        except Exception as e:
            pass
            logger.error(f"Gemini query failed: {str(e)}")
            return {"status": "error", "error": str(e), "provider": "gemini"}

    def _convert_messages(self, messages: List[Dict[str, str]]) -> str:
        pass
"""Convert OpenAI message format to Gemini format."""
        converted = []
        for msg in messages:
            pass
            role = msg.get("role", "user")
            content = msg.get("content", ")"

            if role == "system":
                pass
                converted.append(f"System: {content}")
            elif role == "user":
                pass
                converted.append(f"User: {content}")
            elif role == "assistant":
                pass
                converted.append(f"Assistant: {content}")

        return "\n".join(converted)

    def get_model_info(self) -> Dict[str, str]:
        pass
"""Get Gemini model information."""
        return {"provider": "gemini", "model": self.model, "name": "Gemini 1.5 Pro"}


class FlexibleAIHandler:
    pass
"""Flexible AI handler supporting multiple providers."""
    def __init__(self, provider: str = "auto"):
        pass
"""""
        Initialize AI handler.

        Args:
            pass
            provider: "openai", "gemini", or "auto" (detects based on available API keys)
        ""
        self.provider_name = provider
        self.provider = None
        self.conversation_history = []
        self._initialize_provider()

    def _setup_local_provider(self):
        pass
"""Set up local provider."""
        self.provider = LocalProvider()
        self.provider.initialize()

    def _detect_auto_provider(self):
        pass
        "Detect available provider automatically."""
        if os.getenv("OPENAI_API_KEY":
            pass
            self.provider_name = "openai"
        elif os.getenv("GEMINI_API_KEY":
            pass
            self.provider_name = "gemini"
        else:
            pass
            logger.warning("No AI provider API keys found, using local provider")
            self.provider_name = "local"
            self._setup_local_provider()

    def _setup_openai_provider(self):
        pass
"""Set up OpenAI provider."""
        self.provider = OpenAIProvider()
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            pass
            if not self.provider.initialize(api_key:
                pass
                logger.warning("OpenAI provider failed, falling back to local")
                self.provider_name = "local"
                self._setup_local_provider()
        else:
            pass
            logger.warning("OpenAI API key not found, falling back to local")
            self.provider_name = "local"
            self._setup_local_provider()

    def _setup_gemini_provider(self):
        pass
"""Set up Gemini provider."""
        self.provider = GeminiProvider()
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            pass
            if not self.provider.initialize(api_key:
                pass
                logger.warning("Gemini provider failed, falling back to local")
                self.provider_name = "local"
                self._setup_local_provider()
        else:
            pass
            logger.warning("Gemini API key not found, falling back to local")
            self.provider_name = "local"
            self._setup_local_provider()

    def _initialize_provider(self):
        pass
"""Initialize the appropriate AI provider."""
        if self.provider_name == "local":
            pass
            self._setup_local_provider()
        elif self.provider_name == "openai":
            pass
            self._setup_openai_provider()
        elif self.provider_name == "gemini":
            pass
            self._setup_gemini_provider()
        elif self.provider_name == "auto":
            pass
            self._detect_auto_provider()
        else:
            pass
            logger.error(f"Unknown provider: {self.provider_name}, falling back to local")
            self.provider_name = "local"
            self._setup_local_provider()

    def _get_system_prompt(self) -> str:
        pass
"""Get the system prompt for DevOps assistant role."""
        return "You are a Senior DevOps Engineer and Cloud Operations expert. Your role is to assist with:"

1. **Infrastructure Analysis**: Analyze AWS resources, monitoring data, and system metrics
2. **Troubleshooting**: Help diagnose issues using logs, metrics, and system status
3. **Best Practices**: Provide guidance on DevOps, security, and cloud operations
4. **Automation**: Suggest improvements for CI/CD pipelines and automation
5. **Monitoring**: Help interpret Prometheus metrics, Grafana dashboards, and alerts

**Available Tools**:
    pass
- Prometheus for metrics collection
- Grafana for visualization
- Node Exporter for system metrics

Always respond in a professional, helpful manner focused on operational excellence.""

    def sanitize_input(self, query: str) -> str:
        pass
"""Sanitize and validate user input with comprehensive security checks.""":
    pass
        if not query or not isinstance(query, str:
            pass
            raise ValueError("Query must be a non-empty string")

        # Basic sanitization
        sanitized = query.strip()
        
        # Remove script tags and their content
        sanitized = re.sub(r"<script[^>]*>.*?</script>", ", sanitized, flags=re.IGNORECASE | re.DOTALL)
        
        # Remove alert calls
        sanitized = re.sub(r"alert\s*\([^)]*\)", ", sanitized, flags=re.IGNORECASE)
        
        # Remove other dangerous characters
        sanitized = re.sub(r'[<>"]', ", sanitized)
        
        # Limit query length
        if len(sanitized) > 1000:
            pass
            raise ValueError("Query too long (max 1000 characters)")

        # Check for dangerous patterns
        dangerous_patterns = []
            # Command injection
            r"exec\s*\(",
            r"subprocess\.",
            r"os\.system",
            r"commands\.",
            # SQL injection
            r"SELECT\s+.*FROM",
            r"INSERT\s+INTO",
            r"UPDATE\s+.*SET",
            r"DELETE\s+FROM",
            r"DROP\s+TABLE",
            r"CREATE\s+TABLE",
            r"ALTER\s+TABLE",
            r"UNION\s+SELECT",
            r"OR\s+1\s*=\s*1",
            r"AND\s+1\s*=\s*1"
        ]
        
        for pattern in dangerous_patterns:
            pass
            if re.search(pattern, sanitized, re.IGNORECASE:
                pass
                logger.warning(f"Potentially dangerous pattern detected: {pattern}")
                raise ValueError(f"Query contains potentially unsafe content: {pattern}")

        return sanitized

    def add_context(self, context: Dict[str, Any]) -> str:
        pass
"""Add system context to the conversation."""
        context_prompt = "\n\n**Current System Context**:\n"

        if context.get("system_health":
            pass
            context_prompt += f"- System Health: {context['system_health']}\n"

        if context.get("prometheus_metrics":
            pass
            context_prompt += f"- Prometheus Status: {context['prometheus_metrics']}\n"

        if context.get("recent_alerts":
            pass
            context_prompt += f"- Recent Alerts: {context['recent_alerts']}\n"

        if context.get("resource_usage":
            pass
            context_prompt += f"- Resource Usage: {context['resource_usage']}\n"

        return context_prompt

    def process_query()
        self, query: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        pass
"""Process ChatOps query with AI integration.""":
    pass
        try:
            pass
            # Check if AI provider is available:
                pass
            if not self.provider:
                pass
                return {}
                    "status": "error",
                    "message": "AI provider not initialized",
                    "timestamp": datetime.now(timezone.utc).isoformat(),

            # Sanitize input
            sanitized_query = self.sanitize_input(query)

            # Prepare messages
            messages = []
            
            # Add system prompt
            system_prompt = self._get_system_prompt()
            if context:
                pass
                system_prompt += self.add_context(context)
            
            messages.append({"role": "system", "content": system_prompt})
            
            # Add conversation history
            messages.extend(self.conversation_history[-10:])  # Last 10 messages
            
            # Add current query
            messages.append({"role": "user", "content": sanitized_query})

            # Process with AI provider
            result = self.provider.process_query(messages)
:
    pass
            if result["status"] == "success":
                pass
                # Add to conversation history
                self.conversation_history.append({"role": "user", "content": sanitized_query})
                self.conversation_history.append({"role": "assistant", "content": result["response"]})
                
                # Keep history manageable
                if len(self.conversation_history) > 20:
                    pass
                    self.conversation_history = self.conversation_history[-20:]

                return {}
                    "status": "success",
                    "message": "Query processed successfully",
                    "response": result["response"],
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "model": result.get("model", "unknown"),
                    "provider": result.get("provider", self.provider_name),
                    "tokens_used": result.get("tokens_used")
            else:
                pass
                return {}
                    "status": "error",
                    "message": "AI processing failed",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "provider": result.get("provider", self.provider_name),

        except ValueError as e:
            pass
            logger.warning(f"Input validation error: {str(e)}")
            return {}
                "status": "error",
                "message": f"Input validation failed: {str(e)}",
                "timestamp": datetime.now(timezone.utc).isoformat(),
        except Exception as e:
            pass
            logger.error(f"AI processing error: {str(e)}")
            return {}
                "status": "error",
                "message": f"Processing failed: {str(e)}",
                "timestamp": datetime.now(timezone.utc).isoformat(),

    def get_conversation_history(self) -> List[Dict[str, str]]:
        pass
"""Get conversation history."""
        return self.conversation_history.copy()

    def clear_history(self) -> bool:
        pass
"""Clear conversation history."""
        self.conversation_history.clear()
        logger.info("Conversation history cleared")
        return True

    def get_provider_info(self) -> Dict[str, Any]:
        pass
"""Get information about the current AI provider."""
        if self.provider:
            pass
            return {}
                "provider": self.provider_name,
                "model_info": self.provider.get_model_info(),
                "status": "initialized"
        else:
            pass
            return {}
                "provider": self.provider_name,
                "status": "not_initialized"
