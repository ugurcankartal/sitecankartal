/**
 * API Service for Personal Portfolio
 * Handles all API calls to Django REST backend
 */

// Use environment variable in production, fallback to relative path or localhost for development
// In production, use relative path to avoid CORS issues
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '/api/v1';

// Types
export interface Profile {
  id: number;
  name: string;
  title: string;
  description: string | null;
  profile_image_url: string | null;
  email: string | null;
  phone: string | null;
  location: string | null;
  social_links: SocialLink[];
}

export interface SocialLink {
  id: number;
  platform: string;
  url: string;
  icon_name: string | null;
  display_order: number;
}

export interface TimelineEntry {
  id: number;
  year: string;
  title: string;
  company: string;
  description: string | null;
  icon_name: string | null;
  skills: string[];
  display_order: number;
}

export interface AboutSectionConfig {
  id: number;
  title: string;
  subtitle: string | null;
  skills_title: string | null;
}

export interface Skill {
  id: number;
  name: string;
  level: number;
  color: string | null;
  display_order: number;
}

export interface Project {
  id: number;
  title: string;
  description: string;
  image_url: string | null;
  tags: string[];
  icon_name: string | null;
  gradient: string | null;
  github_url: string | null;
  demo_url: string | null;
  is_featured: boolean;
  status: boolean;
  display_order: number;
}

export interface BlogPost {
  id: number;
  title: string;
  excerpt: string;
  content: string | null;
  image_url: string | null;
  url: string | null;
  category: string | null;
  date: string;
  read_time: string | null;
  author: string | null;
  is_featured: boolean;
  is_published: boolean;
}

export interface ContactFormData {
  name: string;
  email: string;
  subject: string;
  message: string;
}

export interface UserInfo {
  id: number;
  full_name: string | null;
  email: string | null;
  phone: string | null;
  bio: string | null;
  location: string | null;
  profile_image_url?: string | null;
  social_links?: UserSocialLink[];
}

export interface UserSocialLink {
  id: number;
  platform: string;
  url: string;
  icon_name: string | null;
  display_order: number;
}

// API Functions
export const api = {
  // Profile
  async getProfile(): Promise<Profile> {
    const response = await fetch(`${API_BASE_URL}/profile`);
    if (!response.ok) {
      throw new Error('Failed to fetch profile');
    }
    return response.json();
  },

  // Timeline
  async getTimeline(): Promise<TimelineEntry[]> {
    const response = await fetch(`${API_BASE_URL}/timeline`);
    if (!response.ok) {
      throw new Error('Failed to fetch timeline');
    }
    return response.json();
  },

  // About Section
  async getAboutSection(): Promise<AboutSectionConfig> {
    const response = await fetch(`${API_BASE_URL}/about`);
    if (!response.ok) {
      throw new Error('Failed to fetch about section');
    }
    return response.json();
  },

  // Skills
  async getSkills(): Promise<Skill[]> {
    const response = await fetch(`${API_BASE_URL}/skills`);
    if (!response.ok) {
      throw new Error('Failed to fetch skills');
    }
    return response.json();
  },

  // Projects
  async getProjects(): Promise<Project[]> {
    const response = await fetch(`${API_BASE_URL}/projects`);
    if (!response.ok) {
      throw new Error('Failed to fetch projects');
    }
    return response.json();
  },

  // Blog
  async getBlogPosts(featured?: boolean): Promise<BlogPost[]> {
    const url = featured 
      ? `${API_BASE_URL}/blog?featured=true`
      : `${API_BASE_URL}/blog`;
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error('Failed to fetch blog posts');
    }
    const data = await response.json();
    return data.posts || data;
  },
  
  // Get blog posts with pagination info
  async getBlogPostsWithInfo(featured?: boolean, perPage?: number): Promise<{ posts: BlogPost[]; total: number; pages: number; current_page: number }> {
    const url = featured 
      ? `${API_BASE_URL}/blog?featured=true${perPage ? `&per_page=${perPage}` : ''}`
      : `${API_BASE_URL}/blog${perPage ? `?per_page=${perPage}` : ''}`;
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error('Failed to fetch blog posts');
    }
    const data = await response.json();
    return {
      posts: data.posts || data,
      total: data.total || (data.posts ? data.posts.length : data.length),
      pages: data.pages || 1,
      current_page: data.current_page || 1
    };
  },

  // User (Project Owner)
  async getUserInfo(): Promise<UserInfo> {
    const response = await fetch(`${API_BASE_URL}/user`);
    if (!response.ok) {
      throw new Error('Failed to fetch user info');
    }
    return response.json();
  },

  // Contact
  async submitContact(data: ContactFormData): Promise<{ message: string; id: number }> {
    const response = await fetch(`${API_BASE_URL}/contact`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    if (!response.ok) {
      throw new Error('Failed to submit contact form');
    }
    return response.json();
  },

  // Health check
  async healthCheck(): Promise<{ status: string; message: string }> {
    const response = await fetch(`${API_BASE_URL}/health`);
    if (!response.ok) {
      throw new Error('API health check failed');
    }
    return response.json();
  },
};
