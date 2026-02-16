"use client"

import React, { useEffect, useState } from "react"
import { Sun, Moon, Square } from "lucide-react"
import Message from "./Message"
import Composer from "./Composer"
import { cls } from "./utils"

function ThinkingIndicator({ onPause }) {
  return (
    <div className={cls("flex gap-3", "justify-start")}>
      <div className="mt-0.5 grid h-7 w-7 shrink-0 place-items-center rounded-full bg-zinc-900 text-[10px] font-bold text-foreground dark:bg-white dark:text-zinc-900">
        AI
      </div>
      <div className="max-w-[80%] rounded-2xl border border-zinc-200 bg-white px-3 py-2 text-sm shadow-sm dark:border-zinc-800 dark:bg-zinc-900 dark:text-zinc-100">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1">
            <div className="h-2 w-2 animate-bounce rounded-full bg-zinc-400 [animation-delay:-0.3s]"></div>
            <div className="h-2 w-2 animate-bounce rounded-full bg-zinc-400 [animation-delay:-0.15s]"></div>
            <div className="h-2 w-2 animate-bounce rounded-full bg-zinc-400"></div>
          </div>
          <span className="text-sm text-zinc-500">AI is thinking...</span>
          <button
            onClick={onPause}
            className="ml-2 inline-flex items-center gap-1 rounded-full border border-zinc-300 px-2 py-1 text-xs text-zinc-600 hover:bg-zinc-50 dark:border-zinc-700 dark:text-zinc-400 dark:hover:bg-zinc-800"
          >
            <Square className="h-3 w-3" /> Stop
          </button>
        </div>
      </div>
    </div>
  )
}

export default function AIAssistantUI() {
  const [theme, setTheme] = useState("light")

  useEffect(() => {
    if (typeof window !== "undefined" && window.matchMedia?.("(prefers-color-scheme: dark)").matches) {
      setTheme("dark")
    }
  }, [])

  useEffect(() => {
    if (theme === "dark") {
      document.documentElement.classList.add("dark")
    } else {
      document.documentElement.classList.remove("dark")
    }
    document.documentElement.style.colorScheme = theme
  }, [theme])

  const [userMessage, setUserMessage] = useState(null)
  const [assistantMessage, setAssistantMessage] = useState(null)
  const [isThinking, setIsThinking] = useState(false)

  async function handleSend(content) {
    if (!content.trim()) return

    setUserMessage({ content })
    setAssistantMessage({ content: "" })
    setIsThinking(true)

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
      const response = await fetch(`${apiUrl}/generate`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ prompt: content }),
      })

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let fullText = ""

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const chunk = decoder.decode(value)
        fullText += chunk
        setAssistantMessage({ content: fullText })
      }
    } catch (error) {
      setAssistantMessage({ content: "Error connecting to server." })
    } finally {
      setIsThinking(false)
    }
  }

  function handlePause() {
    setIsThinking(false)
  }

  return (
    <div className="flex h-screen w-full flex-col bg-zinc-50 text-zinc-900 dark:bg-zinc-950 dark:text-zinc-100">
      {/* Minimal header */}
      <header className="flex items-center justify-between border-b border-zinc-200/60 px-4 py-3 dark:border-zinc-800">
        <div className="flex items-center gap-2 text-sm font-semibold tracking-tight">
          <span className="grid h-7 w-7 place-items-center rounded-full bg-zinc-900 text-[10px] font-bold text-white dark:bg-white dark:text-zinc-900">
            AI
          </span>
          AI Assistant
        </div>
        <button
          className="inline-flex items-center gap-2 rounded-full border border-zinc-200 bg-white px-2.5 py-1.5 text-sm hover:bg-zinc-100 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-zinc-400 dark:border-zinc-800 dark:bg-zinc-950 dark:hover:bg-zinc-800"
          onClick={() => setTheme((t) => (t === "dark" ? "light" : "dark"))}
          aria-label="Toggle theme"
        >
          {theme === "dark" ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
        </button>
      </header>

      {/* Chat area */}
      <div className="flex flex-1 flex-col overflow-hidden">
        <div className="flex-1 overflow-y-auto px-4 py-6 sm:px-8">
          <div className="mx-auto max-w-3xl space-y-5">
            {!userMessage && !assistantMessage && (
              <div className="flex flex-col items-center justify-center py-20 text-center">
                <div className="mb-4 grid h-12 w-12 place-items-center rounded-full bg-zinc-900 text-sm font-bold text-white dark:bg-white dark:text-zinc-900">
                  AI
                </div>
                <h2 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">How can I help you today?</h2>
                <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">
                  Send a message to get started.
                </p>
              </div>
            )}

            {userMessage && (
              <Message role="user">
                <div className="whitespace-pre-wrap">{userMessage.content}</div>
              </Message>
            )}

            {isThinking && <ThinkingIndicator onPause={handlePause} />}

            {assistantMessage && (
              <Message role="assistant">
                <div className="whitespace-pre-wrap">{assistantMessage.content}</div>
              </Message>
            )}
          </div>
        </div>

        <Composer
          onSend={handleSend}
          busy={isThinking}
        />
      </div>
    </div>
  )
}
