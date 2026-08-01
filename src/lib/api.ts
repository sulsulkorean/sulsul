import { Post } from "@/interfaces/post";
import fs from "fs";
import matter from "gray-matter";
import { join } from "path";
import { DEFAULT_AUTHOR, DEFAULT_COVER_IMAGE } from "./constants";

const postsDirectory = join(process.cwd(), "_posts");

export function getPostSlugs() {
  if (!fs.existsSync(postsDirectory)) return [];
  return fs.readdirSync(postsDirectory).filter((file) => file.endsWith(".md"));
}

export function getPostBySlug(slug: string): Post {
  const realSlug = slug.replace(/\.md$/, "");
  const fullPath = join(postsDirectory, `${realSlug}.md`);
  const fileContents = fs.readFileSync(fullPath, "utf8");
  const { data, content } = matter(fileContents);

  const coverImage = data.coverImage || DEFAULT_COVER_IMAGE;

  return {
    ...data,
    slug: realSlug,
    content,
    coverImage,
    author: data.author?.name ? data.author : DEFAULT_AUTHOR,
    ogImage: { url: data.ogImage?.url || coverImage },
  } as Post;
}

export function getAllPosts(): Post[] {
  return getPostSlugs()
    .map((slug) => getPostBySlug(slug))
    .sort((post1, post2) => (post1.date > post2.date ? -1 : 1));
}

export function wordCount(content: string) {
  return content.trim().split(/\s+/).filter(Boolean).length;
}
