import React, { useCallback, useEffect, useRef, useState } from 'react';
import { Sheet, SheetContent, SheetHeader, SheetTitle } from '../ui/sheet';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../ui/select';
import {
  createSubject,
  deleteMaterial,
  getMaterials,
  getSubjects,
  uploadMaterial,
  type MaterialKind,
  type MaterialSummary,
  type SubjectSummary,
} from '../../services/subjectService';
import { Loader2, Trash2, Upload } from 'lucide-react';

interface MaterialsDrawerProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  selectedSubjectId: string | null;
  onSubjectCreated?: (subject: SubjectSummary) => void;
}

const MATERIAL_KINDS: MaterialKind[] = ['slides', 'book', 'notes', 'homework', 'other'];

function statusLabel(status: MaterialSummary['status']): string {
  switch (status) {
    case 'pending':
      return 'Queued';
    case 'processing':
      return 'Indexing…';
    case 'ready':
      return 'Ready';
    case 'failed':
      return 'Failed';
    default:
      return status;
  }
}

export const MaterialsDrawer: React.FC<MaterialsDrawerProps> = ({
  open,
  onOpenChange,
  selectedSubjectId,
  onSubjectCreated,
}) => {
  const [subjects, setSubjects] = useState<SubjectSummary[]>([]);
  const [activeSubjectId, setActiveSubjectId] = useState<string | null>(selectedSubjectId);
  const [materials, setMaterials] = useState<MaterialSummary[]>([]);
  const [newSubjectName, setNewSubjectName] = useState('');
  const [materialKind, setMaterialKind] = useState<MaterialKind>('notes');
  const [isLoading, setIsLoading] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const loadSubjects = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const loaded = await getSubjects();
      setSubjects(loaded);
      if (!activeSubjectId && loaded.length > 0) {
        setActiveSubjectId(selectedSubjectId ?? loaded[0].id);
      }
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : 'Failed to load subjects');
    } finally {
      setIsLoading(false);
    }
  }, [activeSubjectId, selectedSubjectId]);

  const loadMaterials = useCallback(async (subjectId: string) => {
    try {
      const loaded = await getMaterials(subjectId);
      setMaterials(loaded);
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : 'Failed to load materials');
    }
  }, []);

  useEffect(() => {
    if (open) {
      void loadSubjects();
    }
  }, [open, loadSubjects]);

  useEffect(() => {
    setActiveSubjectId(selectedSubjectId);
  }, [selectedSubjectId]);

  useEffect(() => {
    if (!open || !activeSubjectId) {
      return;
    }
    void loadMaterials(activeSubjectId);
  }, [open, activeSubjectId, loadMaterials]);

  useEffect(() => {
    if (!open || !activeSubjectId) {
      return;
    }
    const hasPending = materials.some(
      (material) => material.status === 'pending' || material.status === 'processing',
    );
    if (!hasPending) {
      return;
    }
    const interval = window.setInterval(() => {
      void loadMaterials(activeSubjectId);
    }, 3000);
    return () => window.clearInterval(interval);
  }, [open, activeSubjectId, materials, loadMaterials]);

  const handleCreateSubject = async () => {
    const name = newSubjectName.trim();
    if (!name) {
      return;
    }
    setError(null);
    try {
      const subject = await createSubject(name);
      setSubjects((prev) => [subject, ...prev]);
      setActiveSubjectId(subject.id);
      setNewSubjectName('');
      onSubjectCreated?.(subject);
    } catch (createError) {
      setError(createError instanceof Error ? createError.message : 'Failed to create subject');
    }
  };

  const handleUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file || !activeSubjectId) {
      return;
    }
    setIsUploading(true);
    setError(null);
    try {
      const material = await uploadMaterial(activeSubjectId, file, materialKind);
      setMaterials((prev) => [material, ...prev]);
    } catch (uploadError) {
      setError(uploadError instanceof Error ? uploadError.message : 'Upload failed');
    } finally {
      setIsUploading(false);
      event.target.value = '';
    }
  };

  const handleDeleteMaterial = async (materialId: string) => {
    if (!activeSubjectId) {
      return;
    }
    setError(null);
    try {
      await deleteMaterial(activeSubjectId, materialId);
      setMaterials((prev) => prev.filter((material) => material.id !== materialId));
    } catch (deleteError) {
      setError(deleteError instanceof Error ? deleteError.message : 'Delete failed');
    }
  };

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent className="w-[400px] sm:w-[540px] overflow-y-auto">
        <SheetHeader>
          <SheetTitle>Course Materials</SheetTitle>
        </SheetHeader>

        <div className="space-y-6 py-6">
          {error ? (
            <p className="text-sm text-destructive" role="alert">
              {error}
            </p>
          ) : null}

          <div className="space-y-2">
            <Label htmlFor="new-subject">New subject</Label>
            <div className="flex gap-2">
              <Input
                id="new-subject"
                value={newSubjectName}
                onChange={(event) => setNewSubjectName(event.target.value)}
                placeholder="e.g. Biology 101"
              />
              <Button type="button" onClick={() => void handleCreateSubject()}>
                Add
              </Button>
            </div>
          </div>

          <div className="space-y-2">
            <Label>Subject</Label>
            <Select
              value={activeSubjectId ?? undefined}
              onValueChange={(value) => setActiveSubjectId(value)}
            >
              <SelectTrigger>
                <SelectValue placeholder={isLoading ? 'Loading…' : 'Select a subject'} />
              </SelectTrigger>
              <SelectContent>
                {subjects.map((subject) => (
                  <SelectItem key={subject.id} value={subject.id}>
                    {subject.name} ({subject.material_count})
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {activeSubjectId ? (
            <>
              <div className="space-y-2">
                <Label>Material type</Label>
                <Select
                  value={materialKind}
                  onValueChange={(value) => setMaterialKind(value as MaterialKind)}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {MATERIAL_KINDS.map((kind) => (
                      <SelectItem key={kind} value={kind}>
                        {kind}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".pptx,.pdf,.docx,.md,.txt"
                  className="hidden"
                  onChange={(event) => void handleUpload(event)}
                />
                <Button
                  type="button"
                  variant="outline"
                  className="w-full"
                  disabled={isUploading}
                  onClick={() => fileInputRef.current?.click()}
                >
                  {isUploading ? (
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  ) : (
                    <Upload className="mr-2 h-4 w-4" />
                  )}
                  Upload file (pptx, pdf, docx, md, txt)
                </Button>
              </div>

              <div className="space-y-3">
                <Label>Materials</Label>
                {materials.length === 0 ? (
                  <p className="text-sm text-muted-foreground">No materials uploaded yet.</p>
                ) : (
                  <ul className="space-y-2">
                    {materials.map((material) => (
                      <li
                        key={material.id}
                        className="flex items-start justify-between gap-2 rounded-md border border-border p-3 text-sm"
                      >
                        <div className="min-w-0">
                          <p className="font-medium truncate">{material.filename}</p>
                          <p className="text-muted-foreground">
                            {statusLabel(material.status)}
                            {material.status === 'ready' ? ` · ${material.chunk_count} chunks` : ''}
                          </p>
                          {material.error ? (
                            <p className="text-destructive text-xs mt-1">{material.error}</p>
                          ) : null}
                        </div>
                        <Button
                          type="button"
                          variant="ghost"
                          size="icon"
                          aria-label={`Delete ${material.filename}`}
                          onClick={() => void handleDeleteMaterial(material.id)}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            </>
          ) : null}
        </div>
      </SheetContent>
    </Sheet>
  );
};
