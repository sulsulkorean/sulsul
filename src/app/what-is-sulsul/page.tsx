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
    offers: [
      {
        "@type": "Offer",
        name: "Digital Starter",
        price: "28.99",
        priceCurrency: "USD",
        description: "3 months Premium speaking habit + PDF workbook",
      },
      {
        "@type": "Offer",
        name: "Full Pack",
        price: "69.99",
        priceCurrency: "USD",
        description: "1-year Premium speaking gym + PDF workbook",
      },
      {
        "@type": "Offer",
        name: "Monthly",
        price: "8.99",
        priceCurrency: "USD",
        description: "Keep your Korean mouth warm after a package or Amazon book",
      },
      {
        "@type": "Offer",
        name: "Annual",
        price: "69.99",
        priceCurrency: "USD",
        description: "One year of speaking maintenance",
      },
    ],
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

          <h2>What SULSUL is not</h2>
          <ul>
            <li>Not a streak / flashcard app (Duolingo lane)</li>
            <li>Not a 1,000-lesson content library (TTMIK / Sejong lane)</li>
            <li>Not a YouTube binge — watching is not speaking</li>
            <li>Not a PDF-first product. The PDF is a bonus, not the hero.</li>
          </ul>

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

          <h2>Pricing (facts only)</h2>
          <ul>
            <li>
              <strong>Digital Starter — $28.99</strong>: 3 months to build your
              speaking habit · PDF included
            </li>
            <li>
              <strong>Full Pack — $69.99</strong>: 1-year Premium speaking gym ·
              best for your Korea trip year
            </li>
            <li>
              <strong>Monthly — $8.99</strong> / <strong>Annual — $69.99</strong>:
              keep your Korean mouth warm after a package or an Amazon book
            </li>
            <li>
              <strong>AI Extra Pack — $3.99</strong> for 30 coaching sessions
              (add-on, not the main offer)
            </li>
          </ul>
          <p>
            Secure PayPal checkout — instant access by email. No fake
            strikethrough prices. No invented &quot;original&quot; $299 anchors.
          </p>

          <h2>Amazon book vs site Starter</h2>
          <p>
            Same price ($28.99), different jobs. The Amazon book is the pattern
            textbook. SULSUL Premium is the speaking gym that keeps those
            patterns warm in your mouth. You do not buy the same PDF twice.
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
