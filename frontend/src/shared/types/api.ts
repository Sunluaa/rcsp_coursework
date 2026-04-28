export type RoleName = "admin" | "editor" | "employee";
export type ContentStatus = "draft" | "published" | "archived";
export type TaskStatus = "todo" | "in_progress" | "done" | "cancelled";
export type TaskPriority = "low" | "medium" | "high";

export interface Role {
  id: number;
  name: RoleName;
  description?: string | null;
}

export interface User {
  id: number;
  email: string;
  full_name: string;
  role: Role;
  is_active: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface Category {
  id: number;
  name: string;
  slug: string;
  description?: string | null;
}

export interface Tag {
  id: number;
  name: string;
  slug: string;
}

export interface Attachment {
  id: number;
  original_filename: string;
  content_type: string;
  size: number;
  storage_provider: string;
  article_id?: number | null;
  news_post_id?: number | null;
  uploaded_by: number;
  created_at: string;
}

export interface Article {
  id: number;
  title: string;
  slug: string;
  content: string;
  status: ContentStatus;
  author_id: number;
  category_id?: number | null;
  created_at: string;
  updated_at: string;
  published_at?: string | null;
  author: User;
  category?: Category | null;
  tags: Tag[];
  attachments: Attachment[];
}

export interface NewsPost extends Article {}

export interface KnowledgeTask {
  id: number;
  title: string;
  description?: string | null;
  status: TaskStatus;
  priority: TaskPriority;
  creator_id: number;
  assignee_id: number;
  related_article_id?: number | null;
  related_news_post_id?: number | null;
  due_date?: string | null;
  created_at: string;
  updated_at: string;
  creator: User;
  assignee: User;
}

export interface SearchItem {
  type: "article" | "news";
  id: number;
  title: string;
  snippet: string;
  status: ContentStatus;
  category?: Category | null;
  tags: Tag[];
}
