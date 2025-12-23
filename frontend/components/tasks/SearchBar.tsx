"use client";

import { Search, X, Loader2 } from "lucide-react";
import { useCallback, useRef, useState } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { useAutocomplete } from "@/hooks/useSearch";

interface SearchBarProps {
  value: string;
  onChange: (value: string) => void;
  onClear: () => void;
  placeholder?: string;
  className?: string;
  isSearching?: boolean;
}

/**
 * SearchBar component with debounced input and autocomplete suggestions.
 * Provides instant search with clear button and loading indicator.
 */
export function SearchBar({
  value,
  onChange,
  onClear,
  placeholder = "Search tasks...",
  className,
  isSearching = false,
}: SearchBarProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [isFocused, setIsFocused] = useState(false);
  const [showSuggestions, setShowSuggestions] = useState(false);

  // Get autocomplete suggestions
  const { data: suggestionsData, isLoading: isLoadingSuggestions } = useAutocomplete(
    value,
    5
  );
  const suggestions = suggestionsData?.data?.suggestions || [];

  // Handle input change
  const handleChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      onChange(e.target.value);
      setShowSuggestions(true);
    },
    [onChange]
  );

  // Handle clear
  const handleClear = useCallback(() => {
    onClear();
    setShowSuggestions(false);
    inputRef.current?.focus();
  }, [onClear]);

  // Handle suggestion click
  const handleSuggestionClick = useCallback(
    (suggestion: { id: string; title: string }) => {
      onChange(suggestion.title);
      setShowSuggestions(false);
    },
    [onChange]
  );

  // Handle keyboard navigation
  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === "Escape") {
        setShowSuggestions(false);
        inputRef.current?.blur();
      }
    },
    []
  );

  // Handle focus/blur
  const handleFocus = useCallback(() => {
    setIsFocused(true);
    if (value.length >= 1) {
      setShowSuggestions(true);
    }
  }, [value]);

  const handleBlur = useCallback(() => {
    setIsFocused(false);
    // Delay hiding suggestions to allow click to register
    setTimeout(() => setShowSuggestions(false), 200);
  }, []);

  return (
    <div className={cn("relative", className)}>
      <div
        className={cn(
          "relative flex items-center rounded-md border transition-colors",
          isFocused ? "border-primary ring-1 ring-primary/20" : "border-input",
          "bg-background"
        )}
      >
        {/* Search icon */}
        <div className="pointer-events-none absolute left-3 flex items-center">
          {isSearching || isLoadingSuggestions ? (
            <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
          ) : (
            <Search className="h-4 w-4 text-muted-foreground" />
          )}
        </div>

        {/* Input */}
        <Input
          ref={inputRef}
          type="search"
          placeholder={placeholder}
          value={value}
          onChange={handleChange}
          onFocus={handleFocus}
          onBlur={handleBlur}
          onKeyDown={handleKeyDown}
          className="border-0 pl-10 pr-10 focus-visible:ring-0 focus-visible:ring-offset-0"
          aria-label="Search tasks"
          aria-expanded={showSuggestions && suggestions.length > 0}
          aria-controls="search-suggestions"
          aria-autocomplete="list"
        />

        {/* Clear button */}
        {value && (
          <Button
            type="button"
            variant="ghost"
            size="icon"
            className="absolute right-1 h-7 w-7 hover:bg-muted"
            onClick={handleClear}
            aria-label="Clear search"
          >
            <X className="h-4 w-4" />
          </Button>
        )}
      </div>

      {/* Autocomplete suggestions dropdown */}
      {showSuggestions && suggestions.length > 0 && (
        <div
          id="search-suggestions"
          role="listbox"
          className="absolute top-full left-0 right-0 z-50 mt-1 max-h-60 overflow-auto rounded-md border bg-popover p-1 shadow-md"
        >
          {suggestions.map((suggestion) => (
            <button
              key={suggestion.id}
              role="option"
              aria-selected={false}
              className={cn(
                "flex w-full items-center gap-2 rounded-sm px-2 py-1.5 text-sm",
                "hover:bg-accent hover:text-accent-foreground",
                "focus:bg-accent focus:text-accent-foreground focus:outline-none"
              )}
              onClick={() => handleSuggestionClick(suggestion)}
            >
              <Search className="h-3 w-3 text-muted-foreground" />
              <span className="flex-1 truncate text-left">{suggestion.title}</span>
              <span
                className={cn(
                  "text-xs",
                  suggestion.status === "completed"
                    ? "text-green-600"
                    : "text-muted-foreground"
                )}
              >
                {suggestion.status}
              </span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

/**
 * Highlight matching text in a string.
 *
 * @param text - Text to highlight
 * @param query - Query to match
 * @returns JSX with highlighted matches
 */
export function HighlightedText({
  text,
  query,
  className,
}: {
  text: string;
  query: string;
  className?: string;
}) {
  if (!query || !query.trim()) {
    return <span className={className}>{text}</span>;
  }

  const regex = new RegExp(`(${escapeRegExp(query)})`, "gi");
  const parts = text.split(regex);

  return (
    <span className={className}>
      {parts.map((part, index) =>
        regex.test(part) ? (
          <mark key={index} className="bg-yellow-200 dark:bg-yellow-800 rounded px-0.5">
            {part}
          </mark>
        ) : (
          <span key={index}>{part}</span>
        )
      )}
    </span>
  );
}

/**
 * Escape special regex characters in a string.
 */
function escapeRegExp(string: string): string {
  return string.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}
