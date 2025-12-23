import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  CheckCircle2,
  Circle,
  Plus,
  Trash2,
  GripVertical
} from "lucide-react";
import { Subtask } from "@/lib/types/task";
import {
  useToggleSubtask,
  useDeleteSubtask,
  useCreateSubtask,
  useUpdateSubtask,
  useReorderSubtasks
} from "@/hooks/useSubtasks";
import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  DragEndEvent,
} from "@dnd-kit/core";
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  useSortable,
  verticalListSortingStrategy,
} from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";

interface SubtaskListProps {
  taskId: string;
  subtasks: Subtask[];
  onSubtasksChange?: (subtasks: Subtask[]) => void;
}

interface SortableSubtaskItemProps {
  subtask: Subtask;
  editingSubtaskId: string | null;
  editText: string;
  onToggle: (subtaskId: string, currentStatus: boolean) => void;
  onDelete: (subtaskId: string) => void;
  onStartEdit: (subtask: Subtask) => void;
  onSaveEdit: (subtaskId: string) => void;
  onCancelEdit: () => void;
  setEditText: (text: string) => void;
}

function SortableSubtaskItem({
  subtask,
  editingSubtaskId,
  editText,
  onToggle,
  onDelete,
  onStartEdit,
  onSaveEdit,
  onCancelEdit,
  setEditText,
}: SortableSubtaskItemProps) {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id: subtask.id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
  };

  return (
    <li
      ref={setNodeRef}
      style={style}
      className="flex items-center gap-2 p-2 rounded-md hover:bg-muted/50 transition-colors"
    >
      <div {...attributes} {...listeners} className="cursor-grab active:cursor-grabbing">
        <GripVertical className="h-4 w-4 text-muted-foreground" />
      </div>

      {editingSubtaskId === subtask.id ? (
        <div className="flex-1 flex gap-2">
          <Input
            type="text"
            value={editText}
            onChange={(e) => setEditText(e.target.value)}
            autoFocus
            className="flex-1"
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                onSaveEdit(subtask.id);
              } else if (e.key === "Escape") {
                onCancelEdit();
              }
            }}
          />
          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={() => onSaveEdit(subtask.id)}
          >
            Save
          </Button>
          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={onCancelEdit}
          >
            Cancel
          </Button>
        </div>
      ) : (
        <>
          <Button
            variant="ghost"
            size="sm"
            className="h-auto p-0"
            onClick={() => onToggle(subtask.id, subtask.is_completed)}
            aria-label={subtask.is_completed ? "Mark as incomplete" : "Mark as complete"}
          >
            {subtask.is_completed ? (
              <CheckCircle2 className="h-5 w-5 text-green-600" />
            ) : (
              <Circle className="h-5 w-5 text-muted-foreground" />
            )}
          </Button>

          <span
            className={`flex-1 ${subtask.is_completed ? 'line-through text-muted-foreground' : ''}`}
            onDoubleClick={() => onStartEdit(subtask)}
          >
            {subtask.description}
          </span>

          <div className="flex gap-1">
            <Button
              variant="ghost"
              size="sm"
              className="h-auto p-1 text-muted-foreground hover:text-foreground"
              onClick={() => onStartEdit(subtask)}
              aria-label="Edit subtask"
            >
              <Plus className="h-4 w-4 rotate-45" />
            </Button>
            <Button
              variant="ghost"
              size="sm"
              className="h-auto p-1 text-destructive hover:text-destructive-foreground"
              onClick={() => onDelete(subtask.id)}
              aria-label="Delete subtask"
            >
              <Trash2 className="h-4 w-4" />
            </Button>
          </div>
        </>
      )}
    </li>
  );
}

export function SubtaskList({ taskId, subtasks }: SubtaskListProps) {
  const [newSubtaskDescription, setNewSubtaskDescription] = useState("");
  const [editingSubtaskId, setEditingSubtaskId] = useState<string | null>(null);
  const [editText, setEditText] = useState("");
  const [localSubtasks, setLocalSubtasks] = useState<Subtask[]>(subtasks);

  const { mutate: toggleSubtask } = useToggleSubtask();
  const { mutate: deleteSubtask } = useDeleteSubtask();
  const { mutate: createSubtask } = useCreateSubtask();
  const { mutate: updateSubtask } = useUpdateSubtask();
  const { mutate: reorderSubtasks } = useReorderSubtasks();

  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 8, // Prevent accidental drags
      },
    }),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );

  // Update local state when props change
  React.useEffect(() => {
    setLocalSubtasks(subtasks);
  }, [subtasks]);

  const handleAddSubtask = () => {
    if (newSubtaskDescription.trim() === "") return;
    
    createSubtask(
      { taskId, description: newSubtaskDescription.trim() },
      {
        onSuccess: () => {
          setNewSubtaskDescription("");
        }
      }
    );
  };

  const handleToggleSubtask = (subtaskId: string, currentStatus: boolean) => {
    toggleSubtask({
      subtaskId,
      isCompleted: !currentStatus
    });
  };

  const handleDeleteSubtask = (subtaskId: string) => {
    deleteSubtask(subtaskId);
  };

  const startEditing = (subtask: Subtask) => {
    setEditingSubtaskId(subtask.id);
    setEditText(subtask.description);
  };

  const saveEdit = (subtaskId: string) => {
    if (editText.trim() === "") return;
    
    updateSubtask({
      subtaskId,
      data: { description: editText.trim() }
    }, {
      onSuccess: () => {
        setEditingSubtaskId(null);
        setEditText("");
      }
    });
  };

  const cancelEdit = () => {
    setEditingSubtaskId(null);
    setEditText("");
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      e.preventDefault();
      handleAddSubtask();
    }
  };

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;

    if (over && active.id !== over.id) {
      const oldIndex = localSubtasks.findIndex((s) => s.id === active.id);
      const newIndex = localSubtasks.findIndex((s) => s.id === over.id);

      // Optimistic update
      const reordered = arrayMove(localSubtasks, oldIndex, newIndex);
      setLocalSubtasks(reordered);

      // Send reorder request to backend
      reorderSubtasks({
        taskId,
        subtaskIds: reordered.map((s) => s.id),
      });
    }
  };

  return (
    <div className="space-y-2">
      {/* Add new subtask */}
      <div className="flex items-center gap-2">
        <Input
          type="text"
          placeholder="Add a subtask..."
          value={newSubtaskDescription}
          onChange={(e) => setNewSubtaskDescription(e.target.value)}
          onKeyDown={handleKeyDown}
          className="flex-1"
        />
        <Button
          type="button"
          variant="outline"
          size="sm"
          onClick={handleAddSubtask}
          disabled={!newSubtaskDescription.trim()}
        >
          <Plus className="h-4 w-4" />
        </Button>
      </div>

      {/* Subtask list with drag-and-drop */}
      {localSubtasks.length > 0 && (
        <DndContext
          sensors={sensors}
          collisionDetection={closestCenter}
          onDragEnd={handleDragEnd}
        >
          <SortableContext
            items={localSubtasks.map((s) => s.id)}
            strategy={verticalListSortingStrategy}
          >
            <ul className="space-y-1">
              {localSubtasks.map((subtask) => (
                <SortableSubtaskItem
                  key={subtask.id}
                  subtask={subtask}
                  editingSubtaskId={editingSubtaskId}
                  editText={editText}
                  onToggle={handleToggleSubtask}
                  onDelete={handleDeleteSubtask}
                  onStartEdit={startEditing}
                  onSaveEdit={saveEdit}
                  onCancelEdit={cancelEdit}
                  setEditText={setEditText}
                />
              ))}
            </ul>
          </SortableContext>
        </DndContext>
      )}
    </div>
  );
}