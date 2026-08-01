import { Metadata } from "next";
import { notFound } from "next/navigation";
import { getAllPosts, getPostBySlug } from "@/lib/api";
import {
  DEFAULT_COVER_IMAGE,
  SITE_NAME,
  SITE_URL,
} from "@/lib/constants";
import {
  blogPostingJsonLd,
  breadcrumbJsonLd,
  faqPageJsonLd,
} from "@/lib/jsonLd";
import markdownToHtml from "@/lib/markdownToHtml";
import Alert from "@/app/_components/alert";
import Container from "@/app/_components/container";
import Header from "@/app/_components/header";
import { PostBody } from "@/app/_components/post-body";
import { PostHeader } from "@/app/_components/post-header";

export default async function Post(props: Params) {
  const params = await props.params;
  const post = getPostBySlug(params.slug);

  if (!post) {
    return notFound();
  }

  const content = await markdownToHtml(post.content || "");
  const schemas = [
    blogPostingJsonLd(post),
    breadcrumbJsonLd(post),
    faqPageJsonLd(post),
  ].filter(Boolean);

  return (
    <main>
      <Alert preview={post.preview} />
      <Container>
        <Header />
        <article className="mb-32">
          {schemas.map((schema, i) => (
            <script
              key={i}
              type="application/ld+json"
              dangerouslySetInnerHTML={{ __html: JSON.stringify(schema) }}
            />
          ))}
          <PostHeader
            title={post.title}
            coverImage={post.coverImage}
            date={post.date}
            author={post.author}
          />
          {post.updated && post.updated !== post.date && (
            <div className="max-w-2xl mx-auto -mt-4 mb-8 text-sm text-slate-500">
              Updated {new Date(post.updated).toLocaleDateString("en-US", {
                year: "numeric",
                month: "long",
                day: "numeric",
              })}
            </div>
          )}
          <PostBody content={content} />
        </article>
      </Container>
    </main>
  );
}

type Params = {
  params: Promise<{
    slug: string;
  }>;
};

export async function generateMetadata(props: Params): Promise<Metadata> {
  const params = await props.params;
  const post = getPostBySlug(params.slug);

  if (!post) {
    return notFound();
  }

  const image = post.ogImage?.url || post.coverImage || DEFAULT_COVER_IMAGE;
  const url = `${SITE_URL}/posts/${post.slug}`;

  return {
    title: post.title,
    description: post.excerpt,
    keywords: post.keywords,
    authors: [{ name: post.author?.name || "Yona" }],
    alternates: {
      canonical: url,
    },
    openGraph: {
      type: "article",
      url,
      siteName: SITE_NAME,
      title: post.title,
      description: post.excerpt,
      publishedTime: post.date,
      modifiedTime: post.updated || post.date,
      authors: [post.author?.name || "Yona"],
      images: [{ url: image, width: 1300, height: 630, alt: post.title }],
    },
    twitter: {
      card: "summary_large_image",
      title: post.title,
      description: post.excerpt,
      images: [image],
    },
  };
}

export async function generateStaticParams() {
  const posts = getAllPosts();
  return posts.map((post) => ({
    slug: post.slug,
  }));
}
