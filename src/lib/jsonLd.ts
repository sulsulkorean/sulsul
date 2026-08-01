import { Post } from "@/interfaces/post";
import {
  AUTHOR_BIO,
  DEFAULT_COVER_IMAGE,
  SITE_DESCRIPTION,
  SITE_NAME,
  SITE_URL,
  APP_URL,
} from "./constants";
import { wordCount } from "./api";

export function organizationJsonLd() {
  return {
    "@context": "https://schema.org",
    "@type": "Organization",
    name: SITE_NAME,
    url: SITE_URL,
    logo: `${SITE_URL}/assets/blog/authors/sulsuli.png`,
    sameAs: [APP_URL],
    description: SITE_DESCRIPTION,
  };
}

export function personJsonLd() {
  return {
    "@context": "https://schema.org",
    "@type": "Person",
    name: "Yona",
    jobTitle: "Founder",
    worksFor: { "@type": "Organization", name: SITE_NAME, url: APP_URL },
    description: AUTHOR_BIO,
    url: SITE_URL,
  };
}

export function blogPostingJsonLd(post: Post) {
  const image = post.ogImage?.url || post.coverImage || DEFAULT_COVER_IMAGE;
  const absoluteImage = image.startsWith("http") ? image : `${SITE_URL}${image}`;

  return {
    "@context": "https://schema.org",
    "@type": "BlogPosting",
    headline: post.title,
    description: post.excerpt,
    image: [absoluteImage],
    datePublished: post.date,
    dateModified: post.updated || post.date,
    wordCount: wordCount(post.content),
    keywords: post.keywords || (post.primaryKeyword ? [post.primaryKeyword] : undefined),
    author: {
      "@type": "Person",
      name: post.author?.name || "Yona",
      url: SITE_URL,
    },
    publisher: {
      "@type": "Organization",
      name: SITE_NAME,
      logo: {
        "@type": "ImageObject",
        url: `${SITE_URL}/assets/blog/authors/sulsuli.png`,
      },
    },
    mainEntityOfPage: {
      "@type": "WebPage",
      "@id": `${SITE_URL}/posts/${post.slug}`,
    },
    speakable: {
      "@type": "SpeakableSpecification",
      cssSelector: ["article h1", "article p:first-of-type"],
    },
  };
}

export function faqPageJsonLd(post: Post) {
  if (!post.faq?.length) return null;
  return {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    mainEntity: post.faq.map((item) => ({
      "@type": "Question",
      name: item.q,
      acceptedAnswer: {
        "@type": "Answer",
        text: item.a,
      },
    })),
  };
}

export function breadcrumbJsonLd(post: Post) {
  return {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    itemListElement: [
      {
        "@type": "ListItem",
        position: 1,
        name: "Home",
        item: SITE_URL,
      },
      {
        "@type": "ListItem",
        position: 2,
        name: post.category || "Blog",
        item: SITE_URL,
      },
      {
        "@type": "ListItem",
        position: 3,
        name: post.title,
        item: `${SITE_URL}/posts/${post.slug}`,
      },
    ],
  };
}
