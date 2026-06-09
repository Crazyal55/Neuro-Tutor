/**
 * Subject and course materials API client.
 */

const API_BASE_URL = (import.meta as any).env?.VITE_API_URL || 'http://localhost:8000/api';

export type MaterialKind = 'slides' | 'book' | 'notes' | 'homework' | 'other';
export type MaterialStatus = 'pending' | 'processing' | 'ready' | 'failed';

export interface SubjectSummary {
  id: string;
  name: string;
  description?: string | null;
  created_at: string;
  material_count: number;
}

export interface MaterialSummary {
  id: string;
  subject_id: string;
  filename: string;
  file_type: string;
  material_kind: MaterialKind;
  status: MaterialStatus;
  error?: string | null;
  chunk_count: number;
  uploaded_at: string;
}

export interface SourceCitation {
  filename: string;
  locator: string;
  score: number;
}

export async function getSubjects(): Promise<SubjectSummary[]> {
  const response = await fetch(`${API_BASE_URL}/subjects/`);
  if (!response.ok) {
    throw new Error(`Failed to load subjects (${response.status})`);
  }
  const data = await response.json();
  return data.subjects;
}

export async function createSubject(name: string, description?: string): Promise<SubjectSummary> {
  const response = await fetch(`${API_BASE_URL}/subjects/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, description }),
  });
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to create subject (${response.status})`);
  }
  return response.json();
}

export async function deleteSubject(subjectId: string): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/subjects/${subjectId}`, {
    method: 'DELETE',
  });
  if (!response.ok && response.status !== 204) {
    throw new Error(`Failed to delete subject (${response.status})`);
  }
}

export async function getMaterials(subjectId: string): Promise<MaterialSummary[]> {
  const response = await fetch(`${API_BASE_URL}/subjects/${subjectId}/materials`);
  if (!response.ok) {
    throw new Error(`Failed to load materials (${response.status})`);
  }
  const data = await response.json();
  return data.materials;
}

export async function uploadMaterial(
  subjectId: string,
  file: File,
  materialKind: MaterialKind = 'other',
): Promise<MaterialSummary> {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('material_kind', materialKind);

  const response = await fetch(`${API_BASE_URL}/subjects/${subjectId}/materials`, {
    method: 'POST',
    body: formData,
  });
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to upload material (${response.status})`);
  }
  return response.json();
}

export async function deleteMaterial(subjectId: string, materialId: string): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/subjects/${subjectId}/materials/${materialId}`, {
    method: 'DELETE',
  });
  if (!response.ok && response.status !== 204) {
    throw new Error(`Failed to delete material (${response.status})`);
  }
}
