"use client";

import { useState } from "react";
import { Check, ChevronsUpDown, Plus } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
  CommandSeparator,
} from "@/components/ui/command";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { useTags, useCreateTag } from "@/hooks/useTags";
import type { TagWithCount as _TagWithCount } from "@/lib/types/tag";
import { TAG_COLORS } from "@/lib/types/tag";
import { TagBadge } from "./TagBadge";

interface TagPickerProps {
  selectedTagIds: string[];
  onTagsChange: (tagIds: string[]) => void;
  maxTags?: number;
  className?: string;
}

/**
 * A dropdown picker for selecting multiple tags.
 * Allows creating new tags inline.
 */
export function TagPicker({
  selectedTagIds,
  onTagsChange,
  maxTags = 10,
  className,
}: TagPickerProps) {
  const [open, setOpen] = useState(false);
  const [search, setSearch] = useState("");
  const [showColorPicker, setShowColorPicker] = useState(false);
  const [newTagColor, setNewTagColor] = useState<string>(TAG_COLORS[0]);

  const { data: tagsData, isLoading } = useTags();
  const createTag = useCreateTag();

  const tags = tagsData?.data?.tags || [];
  const selectedTags = tags.filter((tag) => selectedTagIds.includes(tag.id));

  const filteredTags = tags.filter((tag) =>
    tag.name.toLowerCase().includes(search.toLowerCase())
  );

  const canAddMore = selectedTagIds.length < maxTags;
  const exactMatch = tags.some(
    (tag) => tag.name.toLowerCase() === search.toLowerCase()
  );

  const handleSelect = (tagId: string) => {
    if (selectedTagIds.includes(tagId)) {
      onTagsChange(selectedTagIds.filter((id) => id !== tagId));
    } else if (canAddMore) {
      onTagsChange([...selectedTagIds, tagId]);
    }
  };

  const handleRemove = (tagId: string) => {
    onTagsChange(selectedTagIds.filter((id) => id !== tagId));
  };

  const handleCreateTag = async () => {
    if (!search.trim() || exactMatch) return;

    try {
      const result = await createTag.mutateAsync({
        name: search.trim(),
        color: newTagColor,
      });

      if (result.data && canAddMore) {
        onTagsChange([...selectedTagIds, result.data.id]);
      }

      setSearch("");
      setShowColorPicker(false);
      setNewTagColor(TAG_COLORS[0]);
    } catch {
      // Error is handled by the mutation
    }
  };

  return (
    <div className={cn("space-y-2", className)}>
      {/* Selected Tags Display */}
      {selectedTags.length > 0 && (
        <div className="flex flex-wrap gap-1">
          {selectedTags.map((tag) => (
            <TagBadge
              key={tag.id}
              tag={tag}
              size="sm"
              onRemove={() => handleRemove(tag.id)}
            />
          ))}
        </div>
      )}

      {/* Tag Picker Dropdown */}
      <Popover open={open} onOpenChange={setOpen}>
        <PopoverTrigger asChild>
          <Button
            variant="outline"
            role="combobox"
            aria-expanded={open}
            aria-label="Select tags"
            className="w-full justify-between"
            disabled={isLoading}
          >
            <span className="text-muted-foreground">
              {selectedTags.length === 0
                ? "Select tags..."
                : `${selectedTags.length} tag${selectedTags.length > 1 ? "s" : ""} selected`}
            </span>
            <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
          </Button>
        </PopoverTrigger>
        <PopoverContent className="w-[280px] p-0" align="start">
          <Command>
            <CommandInput
              placeholder="Search or create tags..."
              value={search}
              onValueChange={setSearch}
            />
            <CommandList>
              <CommandEmpty>
                {search.trim() && !exactMatch ? (
                  <div className="p-2">
                    {!showColorPicker ? (
                      <Button
                        variant="ghost"
                        className="w-full justify-start"
                        onClick={() => setShowColorPicker(true)}
                      >
                        <Plus className="mr-2 h-4 w-4" />
                        Create &quot;{search}&quot;
                      </Button>
                    ) : (
                      <div className="space-y-3">
                        <p className="text-sm text-muted-foreground">
                          Choose a color for &quot;{search}&quot;:
                        </p>
                        <div className="grid grid-cols-8 gap-1">
                          {TAG_COLORS.map((color) => (
                            <button
                              key={color}
                              type="button"
                              onClick={() => setNewTagColor(color)}
                              className={cn(
                                "h-6 w-6 rounded-full border-2 transition-transform hover:scale-110",
                                newTagColor === color
                                  ? "border-foreground"
                                  : "border-transparent"
                              )}
                              style={{ backgroundColor: color }}
                              aria-label={`Select color ${color}`}
                            />
                          ))}
                        </div>
                        <div className="flex gap-2">
                          <Button
                            size="sm"
                            onClick={handleCreateTag}
                            disabled={createTag.isPending}
                            className="flex-1"
                          >
                            {createTag.isPending ? "Creating..." : "Create Tag"}
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => setShowColorPicker(false)}
                          >
                            Cancel
                          </Button>
                        </div>
                      </div>
                    )}
                  </div>
                ) : (
                  <p className="text-sm text-muted-foreground p-2">
                    No tags found.
                  </p>
                )}
              </CommandEmpty>

              {filteredTags.length > 0 && (
                <CommandGroup heading="Available Tags">
                  {filteredTags.map((tag) => {
                    const isSelected = selectedTagIds.includes(tag.id);
                    const canSelect = isSelected || canAddMore;

                    return (
                      <CommandItem
                        key={tag.id}
                        value={tag.name}
                        onSelect={() => handleSelect(tag.id)}
                        disabled={!canSelect}
                        className={cn(!canSelect && "opacity-50")}
                      >
                        <div className="flex items-center gap-2 flex-1">
                          <div
                            className="h-3 w-3 rounded-full shrink-0"
                            style={{ backgroundColor: tag.color }}
                          />
                          <span className="truncate">{tag.name}</span>
                          <span className="ml-auto text-xs text-muted-foreground">
                            {tag.task_count}
                          </span>
                        </div>
                        <Check
                          className={cn(
                            "ml-2 h-4 w-4 shrink-0",
                            isSelected ? "opacity-100" : "opacity-0"
                          )}
                        />
                      </CommandItem>
                    );
                  })}
                </CommandGroup>
              )}

              {search.trim() && !exactMatch && filteredTags.length > 0 && (
                <>
                  <CommandSeparator />
                  <CommandGroup>
                    <CommandItem onSelect={() => setShowColorPicker(true)}>
                      <Plus className="mr-2 h-4 w-4" />
                      Create &quot;{search}&quot;
                    </CommandItem>
                  </CommandGroup>
                </>
              )}
            </CommandList>
          </Command>

          {!canAddMore && (
            <p className="text-xs text-muted-foreground p-2 border-t">
              Maximum {maxTags} tags allowed
            </p>
          )}
        </PopoverContent>
      </Popover>
    </div>
  );
}
