"use client"

import { useState, useRef, useEffect, useCallback, useMemo } from "react"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Send, Bot, User, Loader2 } from "lucide-react"
import { apiClient } from "@/lib/api"
import { cn } from "@/lib/utils"

interface Message {
  id: string
  content: string
  sender: "user" | "ai"
  timestamp: Date
  suggestions?: string[]
  status?: "sending" | "sent" | "error"
}

export function ChatOpsInterface() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState("")
  const [isTyping, setIsTyping] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [])

  useEffect(() => {
    scrollToBottom()
  }, [messages, scrollToBottom])

  // Focus input on mount for better UX
  useEffect(() => {
    inputRef.current?.focus()
  }, [])

  const handleSend = useCallback(async () => {
    if (!input.trim() || isTyping) return

    const userMessage: Message = {
      id: Date.now().toString(),
      content: input.trim(),
      sender: "user",
      timestamp: new Date(),
      status: "sending"
    }

    setMessages((prev) => [...prev, userMessage])
    setInput("")
    setIsTyping(true)
    setError(null)

    try {
      // Real API call to backend with corrected endpoint
      const response = await apiClient.sendChatMessage(input.trim())
      
                    if (response.status === 'success' && response.data) {
                // Handle different response formats from backend
                const aiContent = response.data.response || 
                                response.data.message || 
                                "AI response received"
        
        const aiResponse: Message = {
          id: (Date.now() + 1).toString(),
          content: aiContent,
          sender: "ai",
          timestamp: new Date(),
                            suggestions: response.data.suggestions || 
                              ["Ask another question", "View system status", "Check metrics"],
          status: "sent"
        }
        
        setMessages((prev) => [
          ...prev.slice(0, -1), 
          { ...prev[prev.length - 1], status: "sent" }, 
          aiResponse
        ])
      } else {
        // Handle error response
        const errorMessage = response.error || "Failed to get response from AI"
        throw new Error(errorMessage)
      }
    } catch (error) {
      console.error('ChatOps API error:', error)
      const errorMessage = error instanceof Error ? error.message : "Failed to send message. Please try again."
      setError(errorMessage)
      
      // Update user message status to error
      setMessages((prev) => 
        prev.map(msg => 
          msg.id === userMessage.id 
            ? { ...msg, status: "error" as const }
            : msg
        )
      )
    } finally {
      setIsTyping(false)
    }
  }, [input, isTyping])

  const handleKeyPress = useCallback((e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }, [handleSend])

  const handleSuggestion = useCallback((suggestion: string) => {
    setInput(suggestion)
    // Auto-send suggestion after a short delay
    setTimeout(() => {
      setInput(suggestion)
      // Trigger send after setting input
      setTimeout(() => handleSend(), 100)
    }, 100)
  }, [handleSend])

  const formatTimestamp = useCallback((timestamp: Date) => {
    return timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }, [])

  // Group messages by date for better organization
  const messageGroups = useMemo(() => {
    const groups: { date: string; messages: Message[] }[] = []
    let currentDate = ""
    
    messages.forEach(message => {
      const messageDate = message.timestamp.toDateString()
      if (messageDate !== currentDate) {
        currentDate = messageDate
        groups.push({ date: messageDate, messages: [] })
      }
      groups[groups.length - 1].messages.push(message)
    })
    
    return groups
  }, [messages])

  return (
    <div className="flex flex-col h-[calc(100vh-12rem)] sm:h-[calc(100vh-8rem)] bg-background border rounded-lg">
      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 scroll-smooth">
        {messageGroups.map((group) => (
          <div key={group.date} className="space-y-4">
            {/* Date Header */}
            <div className="text-center">
              <span className="text-xs text-muted-foreground bg-muted px-2 py-1 rounded">
                {new Date(group.date).toLocaleDateString()}
              </span>
            </div>
            
            {/* Messages */}
            {group.messages.map((message) => (
              <div
                key={message.id}
                className={cn(
                  "flex gap-3 animate-in fade-in-0 slide-in-from-bottom-2 duration-300",
                  message.sender === "user" ? "justify-end" : "justify-start"
                )}
              >
                {message.sender === "ai" && (
                  <Avatar className="w-8 h-8 shrink-0">
                    <AvatarFallback className="bg-primary text-primary-foreground">
                      <Bot className="w-4 h-4" />
                    </AvatarFallback>
                  </Avatar>
                )}
                
                <div className={cn(
                  "flex flex-col max-w-[85%] sm:max-w-[70%]",
                  message.sender === "user" ? "items-end" : "items-start"
                )}>
                  <Card className={cn(
                    "p-3 space-y-2",
                    message.sender === "user" 
                      ? "bg-primary text-primary-foreground" 
                      : "bg-muted",
                    message.status === "error" && "border-destructive/50 bg-destructive/10"
                  )}>
                    <div className="flex items-center gap-2">
                      {message.sender === "user" && (
                        <Avatar className="w-6 h-6">
                          <AvatarFallback className="bg-primary-foreground text-primary text-xs">
                            <User className="w-3 h-3" />
                          </AvatarFallback>
                        </Avatar>
                      )}
                      
                      <div className="flex-1">
                        <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                        
                        {/* Status indicators */}
                        {message.status === "sending" && (
                          <div className="flex items-center gap-1 mt-1">
                            <Loader2 className="w-3 h-3 animate-spin" />
                            <span className="text-xs">Sending...</span>
                          </div>
                        )}
                        
                        {message.status === "error" && (
                          <div className="flex items-center gap-1 mt-1 text-destructive">
                            <span className="text-xs">Failed to send</span>
                          </div>
                        )}
                      </div>
                    </div>
                  </Card>
                  
                  {/* Timestamp */}
                  <time 
                    className="text-xs text-muted-foreground mt-1"
                    dateTime={message.timestamp.toISOString()}
                    aria-label={`Message sent at ${formatTimestamp(message.timestamp)}`}
                  >
                    {formatTimestamp(message.timestamp)}
                  </time>
                  
                  {/* Suggestions for AI messages */}
                  {message.sender === "ai" && message.suggestions && message.suggestions.length > 0 && (
                    <div className="flex flex-wrap gap-2 mt-2">
                      {message.suggestions.map((suggestion, index) => (
                        <Button
                          key={index}
                          variant="outline"
                          size="sm"
                          className="h-7 px-2 text-xs"
                          onClick={() => handleSuggestion(suggestion)}
                        >
                          {suggestion}
                        </Button>
                      ))}
                    </div>
                  )}
                </div>
                
                {message.sender === "user" && (
                  <Avatar className="w-8 h-8 shrink-0">
                    <AvatarFallback className="bg-primary text-primary-foreground">
                      <User className="w-4 h-4" />
                    </AvatarFallback>
                  </Avatar>
                )}
              </div>
            ))}
          </div>
        ))}
        
        {/* Typing indicator */}
        {isTyping && (
          <div className="flex gap-3 animate-in fade-in-0 slide-in-from-bottom-2 duration-300">
            <Avatar className="w-8 h-8 shrink-0">
              <AvatarFallback className="bg-primary text-primary-foreground">
                <Bot className="w-4 h-4" />
              </AvatarFallback>
            </Avatar>
            <Card className="p-3 bg-muted">
              <div className="flex items-center gap-2">
                <Loader2 className="w-4 h-4 animate-spin" />
                <span className="text-sm">AI is thinking...</span>
              </div>
            </Card>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>
      
      {/* Error message */}
      {error && (
        <div className="px-4 py-2 bg-destructive/10 border border-destructive/50 rounded-lg mx-4 mb-4">
          <p className="text-sm text-destructive">{error}</p>
        </div>
      )}
      
      {/* Input Form */}
      <form 
        onSubmit={(e) => {
          e.preventDefault()
          handleSend()
        }}
        className="p-4 border-t bg-background"
      >
        <div className="flex gap-2">
          <Input
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyPress}
            placeholder="Ask about system status, metrics, or get help..."
            disabled={isTyping}
            className="flex-1"
            aria-label="Chat message input"
            aria-describedby="chat-input-help"
          />
          <Button 
            type="submit" 
            disabled={!input.trim() || isTyping}
            aria-label="Send message"
          >
            <Send className="w-4 h-4" />
          </Button>
        </div>
        <div id="chat-input-help" className="sr-only">
          Type your message and press Enter or click Send to submit
        </div>
      </form>
    </div>
  )
}
