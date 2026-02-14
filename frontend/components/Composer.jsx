"use client"

import { useRef, useState, useEffect } from "react"
import { Send, Loader2 } from "lucide-react"
import { cls } from "./utils"

export default function Composer({ onSend, busy }) {
  const [value, setValue] = useState("")
  const inputRef = useRef(null)

  useEffect(() => {
    if (inputRef.current) {
      const textarea = inputRef.current
      const lineHeight = 24
      const minHeight = 24

      textarea.style.height = "auto"
      const scrollHeight = textarea.scrollHeight
      const calculatedLines = Math.max(1, Math.ceil(scrollHeight / lineHeight))

      if (calculatedLines <= 8) {
        textarea.style.height = `${Math.max(minHeight, scrollHeight)}px`
        textarea.style.overflowY = "hidden"
      } else {
        textarea.style.height = `${8 * lineHeight}px`
        textarea.style.overflowY = "auto"
      }
    }
  }, [value])

  function handleSend() {
    if (!value.trim() || busy) return
    onSend?.(value)
    setValue("")
    inputRef.current?.focus()
  }

  const hasContent = value.trim().length > 0

  return (
    <div className="border-t border-zinc-200/60 p-4 dark:border-zinc-800">
      <div
        className={cls(
          "mx-auto flex flex-col rounded-3xl border bg-white shadow-sm transition-all duration-200 dark:bg-zinc-950",
          "max-w-3xl border-zinc-200 dark:border-zinc-800",
        )}
      >
        <div className="flex-1 px-4 pt-4 pb-2">
          <textarea
            ref={inputRef}
            value={value}
            onChange={(e) => setValue(e.target.value)}
            placeholder="How can I help you today?"
            rows={1}
            className={cls(
              "w-full resize-none bg-transparent text-sm outline-none placeholder:text-zinc-400 transition-all duration-200",
              "min-h-[24px] text-left leading-6",
            )}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault()
                handleSend()
              }
            }}
          />
        </div>

        <div className="flex items-center justify-end px-3 pb-3">
          <button
            onClick={handleSend}
            disabled={busy || !hasContent}
            className={cls(
              "inline-flex shrink-0 items-center justify-center rounded-full p-2.5 transition-colors",
              hasContent
                ? "bg-zinc-900 text-white hover:bg-zinc-800 dark:bg-white dark:text-zinc-900 dark:hover:bg-zinc-200"
                : "cursor-not-allowed bg-zinc-200 text-zinc-400 dark:bg-zinc-800 dark:text-zinc-600",
            )}
          >
            {busy ? <Loader2 className="h-5 w-5 animate-spin" /> : <Send className="h-5 w-5" />}
          </button>
        </div>
      </div>

      <div className="mx-auto mt-2 max-w-3xl px-1 text-center text-[11px] text-zinc-400 dark:text-zinc-500">
        AI can make mistakes. Check important info.
      </div>
    </div>
  )
}
