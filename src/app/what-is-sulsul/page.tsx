import Container from "@/app/_components/container";
import Header from "@/app/_components/header";
import {
  APP_URL,
  AUTHOR_BIO,
  SITE_NAME,
  SITE_TAGLINE,
  SITE_URL,
  appLink,
} from "@/lib/constants";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "What is SULSUL?",
  description:
    "SULSUL is a Korean speaking gym for your first trip to Seoul: 100 survival patterns, speak-along practice, AI pronunciation coaching, and real-life missions. PDF workbook is a bonus.",
  alternates: { canonical: `${SITE_URL}/what-is-sulsul` },
  openGraph: {
    title: "What is SULSUL?",
    description:
      "A Korean speaking gym — not another streak app. Speak 100 survival patterns out loud, get fixed by AI, then run cafe and delivery missions.",
    url: `${SITE_URL}/what-is-sulsul`,
  },
};

export default function WhatIsSulsulPage() {
  const entity = {
    "@context": "https://schema.org",
    "@type": "SoftwareApplication",
    name: "SULSUL",
    applicationCategory: "EducationalApplication",
    operatingSystem: "Web",
    url: APP_URL,
    description:
      "Korean speaking gym built around 100 survival patterns, speak-along shadowing, AI pronunciation coaching, survival missions, and My Sentence AI. PDF workbook is a bonus.",
    offers: {
      "@type": "Offer",
      url: APP_URL,
      category: "Subscription and one-off packages",
    },
    author: {
      "@type": "Person",
      name: "Yona",
      description: AUTHOR_BIO,
    },
  };

  return (
    <main>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(entity) }}
      />
      <Container>
        <Header />
        <article className="max-w-2xl mx-auto mb-32 prose dark:prose-invert">
          <h1 className="text-4xl md:text-5xl font-bold tracking-tighter mb-4">
            What is SULSUL?
          </h1>
          <p className="text-xl text-slate-600 dark:text-slate-300 mb-8">
            {SITE_TAGLINE}.
          </p>

          <h2>Short answer</h2>
          <p>
            <strong>SULSUL</strong> is a Korean <em>speaking gym</em> for people
            who have studied Korean for months and still freeze when a real
            Korean speaks to them. You practice 100 survival patterns out loud,
            get instant fixes from an AI pronunciation coach, then run real
            situations — cafe, delivery, taxi, convenience store — as missions.
            The 100-pattern PDF workbook comes along as a bonus. The mouth is
            the point.
          </p>

          <h2>How is it different from studying?</h2>
          <p>
            Most Korean study happens with your eyes. You read a lesson, tap
            through a quiz, watch a video, and none of it moves your mouth. Then
            a barista asks you a question and nothing comes out.
          </p>
          <p>
            SULSUL is built the other way round. Every session ends with you
            having said something out loud and been told how it landed. The
            workbook supports that practice — it is not the product.
          </p>

          <h2>The loop</h2>
          <ol>
            <li>Pick one survival pattern</li>
            <li>Listen, then shadow it out loud</li>
            <li>Get an instant fix from the AI pronunciation coach</li>
            <li>Pass the mission for that real-life situation</li>
            <li>
              Use <strong>My Sentence AI</strong> to turn the pattern into your
              own line
            </li>
          </ol>

          <h2>Who it is for</h2>
          <p>
            K-pop and K-drama fans, and first-time Korea travellers, who want to
            order coffee, buy convenience-store snacks, ask for directions, and
            greet people without switching back to English.
          </p>

          <h2>What does it cost?</h2>
          <p>
            A private Korean tutor usually runs $30–50 for a single hour. SULSUL
            costs less than one of those sessions and you can keep training your
            speaking every day, for months.
          </p>
          <p>
            There are short packages and monthly plans depending on how long you
            have before your trip.{" "}
            <a href={appLink("what_is_pricing")}>
              See the current plans on sulsul.app
            </a>
            .
          </p>

          <h2>Amazon book vs site Starter</h2>
          <p>
            They do different jobs. The Amazon book is the textbook you read.
            SULSUL Premium is where you practise those patterns out loud and get
            corrected on the spot. If you already own the book, Premium adds the
            speaking practice rather than the same pages again.
          </p>

          <h2>Founder</h2>
          <p>{AUTHOR_BIO}</p>

          <p className="mt-10">
            <a
              href={appLink("what_is")}
              className="inline-block bg-pink-500 hover:bg-pink-600 text-white font-bold py-3 px-8 rounded-full no-underline"
            >
              Start speaking with {SITE_NAME} →
            </a>
          </p>
        </article>
      </Container>
    </main>
  );
}
