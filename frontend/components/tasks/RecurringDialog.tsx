"use client";

import { useState } from "react";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { Checkbox } from "@/components/ui/checkbox";
import { Calendar } from "@/components/ui/calendar";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { CalendarIcon, Loader2 } from "lucide-react";
import { format } from "date-fns";
import { cn } from "@/lib/utils";
import { useToast } from "@/hooks/use-toast";
import { useCreateRecurrence, useUpdateRecurrence, useRecurrencePattern } from "@/hooks/useRecurring";
import type { RecurrencePatternCreate } from "@/hooks/useRecurring";

interface RecurringDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  taskId: string;
  mode?: "create" | "edit";
}

const DAYS_OF_WEEK = [
  { value: 0, label: "Mon" },
  { value: 1, label: "Tue" },
  { value: 2, label: "Wed" },
  { value: 3, label: "Thu" },
  { value: 4, label: "Fri" },
  { value: 5, label: "Sat" },
  { value: 6, label: "Sun" },
];

export function RecurringDialog({ open, onOpenChange, taskId, mode = "create" }: RecurringDialogProps) {
  const { data: existingPattern } = useRecurrencePattern(mode === "edit" ? taskId : undefined);
  const createRecurrence = useCreateRecurrence();
  const updateRecurrence = useUpdateRecurrence();
  const { toast } = useToast();

  const [frequency, setFrequency] = useState<"daily" | "weekly" | "monthly">(
    existingPattern?.frequency || "weekly"
  );
  const [interval, setInterval] = useState<number>(existingPattern?.interval || 1);
  const [daysOfWeek, setDaysOfWeek] = useState<number[]>(existingPattern?.days_of_week || []);
  const [dayOfMonth, setDayOfMonth] = useState<number | undefined>(existingPattern?.day_of_month || undefined);
  const [endDate, setEndDate] = useState<Date | undefined>(
    existingPattern?.end_date ? new Date(existingPattern.end_date) : undefined
  );

  const handleSubmit = async () => {
    try {
      const data: RecurrencePatternCreate = {
        frequency,
        interval,
        days_of_week: frequency === "weekly" && daysOfWeek.length > 0 ? daysOfWeek : null,
        day_of_month: frequency === "monthly" && dayOfMonth ? dayOfMonth : null,
        end_date: endDate ? endDate.toISOString() : null,
      };

      if (mode === "create") {
        await createRecurrence.mutateAsync({ taskId, data });
        toast({ title: "Success", description: "Recurrence pattern created" });
      } else {
        await updateRecurrence.mutateAsync({ taskId, data });
        toast({ title: "Success", description: "Recurrence pattern updated" });
      }

      onOpenChange(false);
    } catch {
      toast({ 
        title: "Error", 
        description: `Failed to ${mode} recurrence pattern`,
        variant: "destructive"
      });
    }
  };

  const toggleDayOfWeek = (day: number) => {
    setDaysOfWeek((prev) =>
      prev.includes(day) ? prev.filter((d) => d !== day) : [...prev, day].sort()
    );
  };

  const isLoading = createRecurrence.isPending || updateRecurrence.isPending;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>{mode === "create" ? "Make Task Recurring" : "Edit Recurrence"}</DialogTitle>
          <DialogDescription>
            Configure how often this task should repeat.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6 py-4">
          {/* Frequency Selection */}
          <div className="space-y-2">
            <Label htmlFor="frequency">Repeat</Label>
            <Select value={frequency} onValueChange={(value: "daily" | "weekly" | "monthly") => setFrequency(value)}>
              <SelectTrigger id="frequency">
                <SelectValue placeholder="Select frequency" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="daily">Daily</SelectItem>
                <SelectItem value="weekly">Weekly</SelectItem>
                <SelectItem value="monthly">Monthly</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Interval */}
          <div className="space-y-2">
            <Label htmlFor="interval">
              Every {interval} {frequency === "daily" ? "day(s)" : frequency === "weekly" ? "week(s)" : "month(s)"}
            </Label>
            <Input
              id="interval"
              type="number"
              min={1}
              max={365}
              value={interval}
              onChange={(e) => setInterval(Math.max(1, parseInt(e.target.value) || 1))}
            />
          </div>

          {/* Days of Week (for weekly) */}
          {frequency === "weekly" && (
            <div className="space-y-2">
              <Label>On these days</Label>
              <div className="flex gap-2 flex-wrap">
                {DAYS_OF_WEEK.map((day) => (
                  <div key={day.value} className="flex items-center space-x-2">
                    <Checkbox
                      id={`day-${day.value}`}
                      checked={daysOfWeek.includes(day.value)}
                      onCheckedChange={() => toggleDayOfWeek(day.value)}
                    />
                    <label
                      htmlFor={`day-${day.value}`}
                      className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                    >
                      {day.label}
                    </label>
                  </div>
                ))}
              </div>
              {frequency === "weekly" && daysOfWeek.length === 0 && (
                <p className="text-sm text-muted-foreground">
                  Select at least one day for weekly recurrence
                </p>
              )}
            </div>
          )}

          {/* Day of Month (for monthly) */}
          {frequency === "monthly" && (
            <div className="space-y-2">
              <Label htmlFor="dayOfMonth">On day of month</Label>
              <Input
                id="dayOfMonth"
                type="number"
                min={1}
                max={31}
                placeholder="Day (1-31)"
                value={dayOfMonth || ""}
                onChange={(e) => setDayOfMonth(parseInt(e.target.value) || undefined)}
              />
              <p className="text-sm text-muted-foreground">
                Leave empty to use the same day each month
              </p>
            </div>
          )}

          {/* End Date */}
          <div className="space-y-2">
            <Label>End Date (optional)</Label>
            <Popover>
              <PopoverTrigger asChild>
                <Button
                  variant="outline"
                  className={cn(
                    "w-full justify-start text-left font-normal",
                    !endDate && "text-muted-foreground"
                  )}
                >
                  <CalendarIcon className="mr-2 h-4 w-4" />
                  {endDate ? format(endDate, "PPP") : "No end date"}
                </Button>
              </PopoverTrigger>
              <PopoverContent className="w-auto p-0" align="start">
                <Calendar
                  mode="single"
                  selected={endDate}
                  onSelect={setEndDate}
                  initialFocus
                  disabled={(date) => date < new Date()}
                />
                {endDate && (
                  <div className="p-3 border-t">
                    <Button
                      variant="outline"
                      size="sm"
                      className="w-full"
                      onClick={() => setEndDate(undefined)}
                    >
                      Clear end date
                    </Button>
                  </div>
                )}
              </PopoverContent>
            </Popover>
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)} disabled={isLoading}>
            Cancel
          </Button>
          <Button onClick={handleSubmit} disabled={isLoading}>
            {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            {mode === "create" ? "Create Recurrence" : "Update Recurrence"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
