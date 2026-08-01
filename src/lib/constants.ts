export const SITE_NAME = "SULSUL Korean";

export const SITE_TAGLINE = "Speak Korean in Seoul — not just study it";

export const SITE_DESCRIPTION =
  "Survival Korean you can actually say out loud: real phrases for cafes, taxis, convenience stores and small talk, with romanization and when to use each one.";

/** Set NEXT_PUBLIC_SITE_URL in Vercel to the live blog domain. */
export const SITE_URL = (
  process.env.NEXT_PUBLIC_SITE_URL ?? "https://blog.sulsul.app"
).replace(/\/$/, "");

export const APP_URL = "https://sulsul.app";

export const appLink = (campaign: string) =>
  `${APP_URL}/?utm_source=blog&utm_medium=${campaign}&utm_campaign=seo`;

export const DEFAULT_COVER_IMAGE = "/assets/blog/covers/start-speaking.png";

export const DEFAULT_AUTHOR = {
  name: "Yona",
  picture: "/assets/blog/authors/yona.png",
};

export const AUTHOR_BIO =
  "Yona is the founder of SULSUL, a Korean speaking app built around 100 survival patterns after years of watching learners memorise grammar tables and still order in English in Seoul.";
