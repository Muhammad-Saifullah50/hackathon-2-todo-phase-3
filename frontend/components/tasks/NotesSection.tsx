"use client";

/**
 * NotesSection Component - Displays task notes with expand/collapse toggle and markdown support.
 * Shows formatted notes text with last updated timestamp.
 */

import { useState } from "react";
import { ChevronDown, ChevronRight, FileText, Clock } from "lucide-react";
import { Button } from "@/components/ui/button";
import { formatDistanceToNow } from "date-fns";

interface NotesSectionProps {
  notes: string | null;
  updatedAt: string;
  defaultExpanded?: boolean;
}

export function NotesSection({
  notes,
  updatedAt,
  defaultExpanded = false,
}: NotesSectionProps) {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded);

  // If no notes, don't render anything
  if (!notes || notes.trim() === "") {
    return null;
  }

  // Simple markdown parsing for basic styles
  const renderMarkdown = (text: string) => {
    let html = text;

    // Bold: **text** or __text__
    html = html.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
    html = html.replace(/__(.*?)__/g, "<strong>$1</strong>");

    // Italic: *text* or _text_
    html = html.replace(/\*(.*?)\*/g, "<em>$1</em>");
    html = html.replace(/_(.*?)_/g, "<em>$1</em>");

    // Line breaks
    html = html.replace(/\n/g, "<br />");

    // Lists: - item or * item
    html = html.replace(/^[\-\*]\s+(.+)$/gm, "<li>$1</li>");
    html = html.replace(/(<li>[\s\S]*?<\/li>)/, "<ul>$1</ul>");

    return html;
  };

  return (
    <div className="border rounded-lg p-3 bg-muted/30">
      {/* Header with toggle */}
      <Button
        variant="ghost"
        size="sm"
        className="w-full justify-start h-auto p-0 hover:bg-transparent"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center gap-2 w-full">
          {isExpanded ? (
            <ChevronDown className="h-4 w-4 text-muted-foreground" />
          ) : (
            <ChevronRight className="h-4 w-4 text-muted-foreground" />
          )}
          <FileText className="h-4 w-4 text-muted-foreground" />
          <span className="text-sm font-medium">Notes</span>
          <span className="text-xs text-muted-foreground ml-auto flex items-center gap-1">
            <Clock className="h-3 w-3" />
            Updated {formatDistanceToNow(new Date(updatedAt), { addSuffix: true })}
          </span>
        </div>
      </Button>

      {/* Content */}
      {isExpanded && (
        <div className="mt-2 pt-2 border-t">
          <div
            className="text-sm text-muted-foreground prose prose-sm max-w-none dark:prose-invert"
            dangerouslySetInnerHTML={{ __html: renderMarkdown(notes) }}
            style={{
              lineHeight: "1.6",
            }}
          />
        </div>
      )}
    </div>
  );
}
