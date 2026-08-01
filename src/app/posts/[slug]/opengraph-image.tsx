import { ImageResponse } from "next/og";
import fs from "fs";
import path from "path";
import { getAllPosts, getPostBySlug } from "@/lib/api";
import { SITE_NAME } from "@/lib/constants";

export const alt = "SULSUL Korean";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

type Params = { params: Promise<{ slug: string }> };

function mascotDataUri() {
  const file = path.join(
    process.cwd(),
    "public/assets/blog/mascot/main.png"
  );
  const base64 = fs.readFileSync(file).toString("base64");
  return `data:image/png;base64,${base64}`;
}

export function generateStaticParams() {
  return getAllPosts().map((post) => ({ slug: post.slug }));
}

export default async function OpengraphImage(props: Params) {
  const { slug } = await props.params;

  let title = SITE_NAME;
  let category = "Survival Korean";
  const post = getPostBySlug(slug);
  if (post) {
    title = post.title || title;
    category = post.category || category;
  }

  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          justifyContent: "space-between",
          padding: "60px 68px",
          background: "linear-gradient(135deg, #FE64AB 0%, #A81F6F 100%)",
          color: "white",
          fontFamily: "sans-serif",
        }}
      >
        <div
          style={{
            display: "flex",
            fontSize: 26,
            fontWeight: 700,
            letterSpacing: 4,
            textTransform: "uppercase",
            opacity: 0.85,
          }}
        >
          {category}
        </div>

        <div style={{ display: "flex", alignItems: "flex-end", gap: 28 }}>
          <div
            style={{
              display: "flex",
              flex: 1,
              fontSize: title.length > 55 ? 56 : 68,
              fontWeight: 800,
              lineHeight: 1.12,
              letterSpacing: -1.5,
            }}
          >
            {title}
          </div>
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src={mascotDataUri()} width={200} height={200} alt="" />
        </div>

        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            fontSize: 27,
            fontWeight: 600,
            opacity: 0.92,
          }}
        >
          <div style={{ display: "flex" }}>{SITE_NAME}</div>
          <div style={{ display: "flex" }}>sulsul.app</div>
        </div>
      </div>
    ),
    size
  );
}
