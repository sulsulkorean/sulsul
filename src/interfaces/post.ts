import { type Author } from "./author";

export type FaqItem = {
  q: string;
  a: string;
};

export type PostSource = {
  title?: string;
  url?: string;
};

export type Post = {
  slug: string;
  title: string;
  date: string;
  updated?: string;
  coverImage: string;
  author: Author;
  excerpt: string;
  ogImage: {
    url: string;
  };
  content: string;
  preview?: boolean;
  category?: string;
  primaryKeyword?: string;
  keywords?: string[];
  faq?: FaqItem[];
  sources?: PostSource[];
};
