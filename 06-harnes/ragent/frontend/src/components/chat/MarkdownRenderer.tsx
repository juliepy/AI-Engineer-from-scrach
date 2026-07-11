// @ts-nocheck
/* eslint-disable */

import * as React from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Check, Copy, ImageIcon } from "lucide-react";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneDark, oneLight } from "react-syntax-highlighter/dist/esm/styles/prism";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { useThemeStore } from "@/stores/themeStore";

interface MarkdownRendererProps {
  content: string;
}

export function MarkdownRenderer({ content }: MarkdownRendererProps) {
  const theme = useThemeStore((state) => state.theme);

  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      components={{
        code({ inline, className, children, node, ...props }) {
          const match = /language-(\w+)/.exec(className || "");
          const language = match?.[1] || "text";
          const value = String(children).replace(/\n$/, "");

          // 判断是否为内联代码：inline 为 true 或者没有换行符
          if (inline || !value.includes('\n')) {
            return (
              <code
                className={cn(
                  "rounded px-1.5 py-0.5 text-[13px] font-mono bg-[#f6f8fa] text-[#24292f]",
                  "dark:bg-[#161b22] dark:text-[#c9d1d9]",
                  className
                )}
                {...props}
              >
                {children}
              </code>
            );
          }

          return (
            <div className="my-3 overflow-hidden rounded-md border border-[#d0d7de] bg-[#f6f8fa] dark:border-[#30363d] dark:bg-[#161b22]">
              <div className="flex items-center justify-between border-b border-[#d0d7de] bg-[#f6f8fa] px-3 py-1.5 dark:border-[#30363d] dark:bg-[#161b22]">
                <span className="font-mono text-[11px] font-semibold uppercase tracking-wider text-[#57606a] dark:text-[#8b949e]">
                  {language}
                </span>
                <CopyButton value={value} />
              </div>
              <div className="overflow-x-auto">
                <SyntaxHighlighter
                  language={language}
                  style={theme === "dark" ? oneDark : oneLight}
                  PreTag="div"
                  customStyle={{
                    margin: 0,
                    padding: "0.75rem 1rem",
                    background: "transparent",
                    fontSize: "13px",
                    lineHeight: "1.5"
                  }}
                  showLineNumbers={false}
                  wrapLines={true}
                >
                  {value}
                </SyntaxHighlighter>
              </div>
            </div>
          );
        },
        img({ src, alt, ...props }) {
          const [hasError, setHasError] = React.useState(false);

          if (hasError) {
            return (
              <div className="my-3 flex items-center gap-2 text-sm text-[#999999]">
                <ImageIcon className="h-4 w-4" />
                <span>图片加载失败</span>
              </div>
            );
          }

          return (
            <img
              src={src}
              alt=""
              className="my-3 max-w-full rounded-lg"
              onError={() => setHasError(true)}
              loading="lazy"
              {...props}
            />
          );
        },
        a({ children, ...props }) {
          return (
            <a
              className="text-[#0969da] underline-offset-4 hover:underline dark:text-[#58a6ff]"
              target="_blank"
              rel="noreferrer"
              {...props}
            >
              {children}
            </a>
          );
        },
        table({ children, ...props }) {
          return (
            <div className="overflow-x-auto">
              <table className="w-full border-collapse border border-[#d0d7de] rounded-md dark:border-[#30363d]" {...props}>
                {children}
              </table>
            </div>
          );
        },
        thead({ children, ...props }) {
          return (
            <thead className="bg-[#f6f8fa] dark:bg-[#161b22]" {...props}>
              {children}
            </thead>
          );
        },
        th({ children, ...props }) {
          return (
            <th className="border-b border-[#d0d7de] border-r border-r-[#d0d7de] px-3 py-2 text-left text-sm font-semibold text-[#24292f] last:border-r-0 dark:border-[#30363d] dark:border-r-[#30363d] dark:text-[#c9d1d9]" {...props}>
              {children}
            </th>
          );
        },
        td({ children, ...props }) {
          return (
            <td className="border-b border-[#d0d7de] border-r border-r-[#d0d7de] px-3 py-2.5 text-sm text-[#24292f] last:border-r-0 dark:border-[#30363d] dark:border-r-[#30363d] dark:text-[#c9d1d9]" {...props}>
              {children}
            </td>
          );
        },
        blockquote({ children, ...props }) {
          return (
            <blockquote
              className="my-3 border-l-4 border-[#3B82F6] bg-[#F0F7FF] pl-3 pr-3 py-2 italic text-[#333333] dark:border-[#60A5FA] dark:bg-[#1A2332] dark:text-[#CCCCCC]"
              {...props}
            >
              {children}
            </blockquote>
          );
        },
        ul({ children, ...props }) {
          return (
            <ul className="my-2 ml-6 list-disc space-y-1" {...props}>
              {children}
            </ul>
          );
        },
        ol({ children, ...props }) {
          return (
            <ol className="my-2 ml-6 list-decimal space-y-1" {...props}>
              {children}
            </ol>
          );
        }
      }}
      className="prose prose-gray max-w-none dark:prose-invert prose-headings:font-semibold prose-headings:text-[#1A1A1A] dark:prose-headings:text-[#EEEEEE] prose-p:text-[#333333] dark:prose-p:text-[#CCCCCC] prose-p:leading-relaxed prose-li:text-[#333333] dark:prose-li:text-[#CCCCCC] prose-strong:text-[#1A1A1A] dark:prose-strong:text-[#EEEEEE]"
    >
      {content}
    </ReactMarkdown>
  );
}

function CopyButton({ value }: { value: string }) {
  const [copied, setCopied] = React.useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(value);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch {
      setCopied(false);
    }
  };

  return (
    <Button
      variant="ghost"
      size="icon"
      onClick={handleCopy}
      aria-label="复制代码"
      className="h-7 w-7 hover:bg-[#eaeef2] dark:hover:bg-[#30363d] transition-colors"
    >
      {copied ? (
        <Check className="h-3.5 w-3.5 text-green-600 dark:text-green-400" />
      ) : (
        <Copy className="h-3.5 w-3.5 text-[#57606a] dark:text-[#8b949e]" />
      )}
    </Button>
  );
}
