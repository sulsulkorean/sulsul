import Container from "@/app/_components/container";
import Header from "@/app/_components/header";
import Image from "next/image";
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
  title: "What Is SULSUL Korean? The Book and Speaking App",
  description:
    "SULSUL Korean connects a practical 100-pattern book with a web speaking app for listening, shadowing, pronunciation feedback, missions, and personalized Korean.",
  alternates: { canonical: `${SITE_URL}/what-is-sulsul` },
  openGraph: {
    title: "What Is SULSUL Korean? The Book and Speaking App",
    description:
      "Learn 100 practical Korean patterns in the book, then hear them, say them, and use them in SULSUL's interactive web app.",
    url: `${SITE_URL}/what-is-sulsul`,
    images: [
      {
        url: "/assets/blog/covers/app-screen-1.png",
        width: 1300,
        height: 730,
        alt: "SULSUL Korean book and speaking app",
      },
    ],
  },
};

export default function WhatIsSulsulPage() {
  const faq = [
    {
      question: "Do I need the SULSUL book to use the app?",
      answer:
        "No. You can start through sulsul.app. The book gives you a structured, visual path through the 100 patterns, while the app supplies the listening and speaking practice.",
    },
    {
      question: "Is SULSUL a mobile app?",
      answer:
        "SULSUL is a web app. It opens in a browser on your phone, tablet, or computer, so you can practise without waiting for an app-store download.",
    },
    {
      question: "What does the app add to the book?",
      answer:
        "The app lets you hear the Korean, shadow it aloud, check what the speech engine heard, practise likely replies in missions, review patterns, and create a sentence that fits your own life.",
    },
    {
      question: "What if I already bought the Amazon book?",
      answer:
        "Use the QR path inside the book to connect your copy with the reader route in SULSUL. The app will show the access available for that purchase path.",
    },
  ];

  const entity = {
    "@context": "https://schema.org",
    "@type": "SoftwareApplication",
    name: "SULSUL",
    applicationCategory: "EducationalApplication",
    operatingSystem: "Web",
    url: APP_URL,
    description:
      "A Korean speaking system that connects a 100-pattern practical Korean book with listening, shadowing, pronunciation feedback, survival missions, review, and My Sentence AI.",
    image: `${SITE_URL}/assets/blog/covers/app-screen-1.png`,
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
  const faqEntity = {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    mainEntity: faq.map((item) => ({
      "@type": "Question",
      name: item.question,
      acceptedAnswer: {
        "@type": "Answer",
        text: item.answer,
      },
    })),
  };

  return (
    <main className="overflow-hidden bg-white text-slate-950 dark:bg-slate-950 dark:text-white">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(entity) }}
      />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(faqEntity) }}
      />
      <Container>
        <Header />
        <article className="mx-auto mb-28 max-w-6xl">
          <section className="relative mb-24 grid items-center gap-12 lg:grid-cols-[0.9fr_1.1fr]">
            <div>
              <p className="mb-5 inline-flex rounded-full bg-pink-50 px-4 py-2 text-xs font-bold uppercase tracking-[0.2em] text-pink-600 dark:bg-pink-950/50 dark:text-pink-300">
                Book + interactive web app
              </p>
              <h1 className="max-w-3xl text-5xl font-black tracking-[-0.05em] sm:text-6xl lg:text-7xl">
                What is{" "}
                <span className="text-[#FE64AB]">SULSUL Korean?</span>
              </h1>
              <p className="mt-7 max-w-xl text-xl font-semibold leading-relaxed text-slate-700 dark:text-slate-200 sm:text-2xl">
                Learn the line in the book. Hear it, say it, and use it in the
                app — before a real person in Seoul is waiting for your answer.
              </p>
              <p className="mt-5 max-w-xl text-base leading-7 text-slate-600 dark:text-slate-400">
                SULSUL connects 100 practical Korean patterns with listening,
                shadowing, pronunciation feedback, survival missions, review,
                and personalized sentence practice.
              </p>
              <div className="mt-8 flex flex-col gap-3 sm:flex-row">
                <a
                  href={appLink("what_is_hero")}
                  className="rounded-full bg-[#FE64AB] px-7 py-4 text-center font-bold text-white shadow-lg shadow-pink-200 transition hover:-translate-y-0.5 hover:bg-pink-500 dark:shadow-none"
                >
                  Open the speaking app →
                </a>
                <a
                  href="#how-it-works"
                  className="rounded-full border border-slate-300 px-7 py-4 text-center font-bold text-slate-800 transition hover:border-[#FE64AB] hover:text-[#FE64AB] dark:border-slate-700 dark:text-white"
                >
                  See how it works
                </a>
              </div>
            </div>
            <div className="relative">
              <div className="absolute -inset-5 -z-10 rounded-[2.5rem] bg-gradient-to-br from-pink-100 via-amber-50 to-sky-100 blur-2xl dark:from-pink-950/50 dark:via-slate-900 dark:to-sky-950/40" />
              <Image
                src="/assets/blog/covers/app-screen-1.png"
                width={1300}
                height={730}
                priority
                alt="SULSUL Korean speaking practice for a real trip to Seoul"
                className="w-full rounded-[2rem] border border-white/80 shadow-2xl dark:border-slate-800"
              />
            </div>
          </section>

          <section className="mb-24 rounded-[2rem] bg-slate-950 px-6 py-12 text-white sm:px-12 lg:px-16">
            <p className="text-sm font-bold uppercase tracking-[0.2em] text-[#FE64AB]">
              The short answer
            </p>
            <h2 className="mt-4 max-w-4xl text-3xl font-black tracking-tight sm:text-4xl">
              SULSUL is one connected Korean speaking system — not a pile of
              disconnected lessons.
            </h2>
            <p className="mt-6 max-w-4xl text-lg leading-8 text-slate-300">
              The book gives you a clear path through 100 useful patterns,
              cultural context, and real-life situations. The web app turns
              those same patterns into something your mouth can retrieve:
              listen, shadow, check your attempt, handle the reply, and make
              the sentence your own.
            </p>
          </section>

          <section className="mb-24 text-center">
            <p className="text-sm font-bold uppercase tracking-[0.2em] text-[#FE64AB]">
              One system, two jobs
            </p>
            <h2 className="mx-auto mt-4 max-w-3xl text-4xl font-black tracking-tight sm:text-5xl">
              The book shows you what to say. The app trains you to say it.
            </h2>
            <div className="mt-12 overflow-hidden rounded-[2rem] border border-slate-200 bg-[#fffaf6] p-3 shadow-xl dark:border-slate-800 dark:bg-slate-900">
              <Image
                src="/assets/blog/covers/whats-inside.png"
                width={1300}
                height={730}
                alt="Overview of SULSUL Korean patterns, missions, culture units, and study plan"
                className="w-full rounded-[1.4rem]"
              />
            </div>
          </section>

          <section className="mb-24 grid items-center gap-12 lg:grid-cols-2">
            <div className="order-2 lg:order-1">
              <Image
                src="/assets/blog/covers/book.png"
                width={1300}
                height={730}
                alt="Front and back cover of the SULSUL Korean practical textbook"
                className="w-full rounded-[2rem] border border-slate-200 shadow-xl dark:border-slate-800"
              />
            </div>
            <div className="order-1 lg:order-2">
              <p className="text-sm font-bold uppercase tracking-[0.2em] text-[#FE64AB]">
                Part 1 · The book
              </p>
              <h2 className="mt-4 text-4xl font-black tracking-tight">
                A field guide for the Korean you will actually need
              </h2>
              <p className="mt-6 text-lg leading-8 text-slate-600 dark:text-slate-300">
                SULSUL organizes beginner Korean around 100 reusable patterns,
                not isolated vocabulary lists. Change one noun or verb and the
                same frame can help you order, ask, explain, refuse, or repair a
                conversation.
              </p>
              <ul className="mt-7 space-y-4">
                {[
                  "100 practical patterns arranged as a clear learning path",
                  "Natural examples, meaning, and context for when a line fits",
                  "Cultural deep-dives that explain the situation behind the words",
                  "Role-play missions for cafés, transport, shopping, food, and daily life",
                  "A visual format made for quick review before and during a trip",
                ].map((item) => (
                  <li key={item} className="flex gap-3 text-base leading-7">
                    <span className="mt-1 flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-pink-100 text-sm font-black text-pink-600 dark:bg-pink-950">
                      ✓
                    </span>
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          </section>

          <section className="mb-24 grid items-center gap-12 lg:grid-cols-2">
            <div>
              <p className="text-sm font-bold uppercase tracking-[0.2em] text-[#FE64AB]">
                Part 2 · The web app
              </p>
              <h2 className="mt-4 text-4xl font-black tracking-tight">
                Turn recognition into a spoken response
              </h2>
              <p className="mt-6 text-lg leading-8 text-slate-600 dark:text-slate-300">
                Reading “커피 주세요” is not the same as saying it while a
                barista is looking at you. SULSUL runs in your browser and
                gives every pattern a speaking loop.
              </p>
              <div className="mt-8 grid gap-4 sm:grid-cols-2">
                {[
                  ["Listen", "Hear the Korean before you try it."],
                  ["Shadow", "Repeat aloud and check what the speech engine heard."],
                  ["Run a mission", "Practise the request, the reply, and your next line."],
                  ["Review", "Return to patterns with flashcards and guided review."],
                  ["Track progress", "See what you have practised and what needs another round."],
                  ["My Sentence AI", "Use the pattern to build a line that belongs to your life."],
                ].map(([title, copy]) => (
                  <div
                    key={title}
                    className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900"
                  >
                    <h3 className="font-black text-slate-950 dark:text-white">
                      {title}
                    </h3>
                    <p className="mt-2 text-sm leading-6 text-slate-600 dark:text-slate-400">
                      {copy}
                    </p>
                  </div>
                ))}
              </div>
            </div>
            <Image
              src="/assets/blog/covers/app-screen-3.png"
              width={1300}
              height={730}
              alt="SULSUL interactive web app with reading, shadowing, and My Sentence practice"
              className="w-full rounded-[2rem] border border-slate-200 shadow-xl dark:border-slate-800"
            />
          </section>

          <section
            id="how-it-works"
            className="mb-24 scroll-mt-8 rounded-[2rem] bg-pink-50 px-6 py-14 dark:bg-pink-950/20 sm:px-12"
          >
            <div className="mx-auto max-w-4xl text-center">
              <p className="text-sm font-bold uppercase tracking-[0.2em] text-pink-600 dark:text-pink-300">
                The SULSUL loop
              </p>
              <h2 className="mt-4 text-4xl font-black tracking-tight">
                Five steps from “I know it” to “I can say it”
              </h2>
            </div>
            <ol className="mt-12 grid gap-5 md:grid-cols-5">
              {[
                ["01", "Meet", "Learn one reusable pattern in context."],
                ["02", "Listen", "Hear the whole line and its rhythm."],
                ["03", "Speak", "Shadow it aloud instead of reading silently."],
                ["04", "Respond", "Handle the likely reply inside a mission."],
                ["05", "Personalize", "Build your own line with My Sentence AI."],
              ].map(([number, title, copy]) => (
                <li
                  key={number}
                  className="rounded-2xl bg-white p-5 shadow-sm dark:bg-slate-900"
                >
                  <span className="text-sm font-black text-[#FE64AB]">
                    {number}
                  </span>
                  <h3 className="mt-5 text-xl font-black">{title}</h3>
                  <p className="mt-2 text-sm leading-6 text-slate-600 dark:text-slate-400">
                    {copy}
                  </p>
                </li>
              ))}
            </ol>
          </section>

          <section className="mb-24 grid items-center gap-12 lg:grid-cols-[1.1fr_0.9fr]">
            <Image
              src="/assets/blog/covers/app-access.png"
              width={1300}
              height={730}
              alt="SULSUL book QR path connecting readers to speaking practice in the web app"
              className="w-full rounded-[2rem] border border-slate-200 shadow-xl dark:border-slate-800"
            />
            <div>
              <p className="text-sm font-bold uppercase tracking-[0.2em] text-[#FE64AB]">
                Book → app
              </p>
              <h2 className="mt-4 text-4xl font-black tracking-tight">
                The QR code is a bridge, not an advertisement
              </h2>
              <p className="mt-6 text-lg leading-8 text-slate-600 dark:text-slate-300">
                If you own the Amazon book, use the QR path inside it to connect
                your copy with SULSUL&apos;s reader route. If you start on the
                website, the available digital-book and app options are shown
                together. Either way, the goal is the same: move from the page
                to a spoken attempt.
              </p>
              <a
                href={appLink("what_is_access")}
                className="mt-7 inline-flex font-bold text-[#FE64AB] hover:underline"
              >
                Check the current access options →
              </a>
            </div>
          </section>

          <section className="mb-24">
            <div className="text-center">
              <p className="text-sm font-bold uppercase tracking-[0.2em] text-[#FE64AB]">
                Built for a specific learner
              </p>
              <h2 className="mt-4 text-4xl font-black tracking-tight">
                SULSUL is for you if…
              </h2>
            </div>
            <div className="mt-10 grid gap-5 md:grid-cols-3">
              {[
                [
                  "You are going to Korea",
                  "You want café, taxi, shopping, restaurant, and small-talk Korean ready before the trip.",
                ],
                [
                  "You love Korean culture",
                  "K-pop and K-drama made you curious, but you want language that works beyond a subtitle.",
                ],
                [
                  "You understand more than you can say",
                  "You have studied vocabulary or grammar, yet your mind goes blank when someone replies.",
                ],
              ].map(([title, copy]) => (
                <div
                  key={title}
                  className="rounded-3xl border border-slate-200 p-7 dark:border-slate-800"
                >
                  <h3 className="text-xl font-black">{title}</h3>
                  <p className="mt-3 leading-7 text-slate-600 dark:text-slate-400">
                    {copy}
                  </p>
                </div>
              ))}
            </div>
          </section>

          <section className="mb-24 rounded-[2rem] border border-slate-200 px-6 py-12 dark:border-slate-800 sm:px-12">
            <h2 className="text-3xl font-black tracking-tight">
              Frequently asked questions
            </h2>
            <div className="mt-8 divide-y divide-slate-200 dark:divide-slate-800">
              {faq.map((item) => (
                <div key={item.question} className="py-6 first:pt-0 last:pb-0">
                  <h3 className="text-lg font-black">{item.question}</h3>
                  <p className="mt-3 max-w-4xl leading-7 text-slate-600 dark:text-slate-400">
                    {item.answer}
                  </p>
                </div>
              ))}
            </div>
          </section>

          <section className="relative overflow-hidden rounded-[2.5rem] bg-slate-950 px-6 py-16 text-center text-white sm:px-12">
            <div className="absolute left-1/2 top-0 h-64 w-64 -translate-x-1/2 -translate-y-1/2 rounded-full bg-[#FE64AB]/30 blur-3xl" />
            <div className="relative mx-auto max-w-3xl">
              <p className="text-sm font-bold uppercase tracking-[0.2em] text-pink-300">
                {SITE_TAGLINE}
              </p>
              <h2 className="mt-5 text-4xl font-black tracking-tight sm:text-5xl">
                Your next Korean sentence should leave the page.
              </h2>
              <p className="mx-auto mt-6 max-w-2xl text-lg leading-8 text-slate-300">
                Pick one practical pattern, hear it, say it, and practise the
                reply. That is the entire SULSUL idea — repeated until speaking
                feels available when you need it.
              </p>
              <a
                href={appLink("what_is_final")}
                className="mt-9 inline-flex rounded-full bg-[#FE64AB] px-8 py-4 font-black text-white transition hover:-translate-y-0.5 hover:bg-pink-500"
              >
                Start speaking with {SITE_NAME} →
              </a>
              <p className="mt-8 text-sm text-slate-500">{AUTHOR_BIO}</p>
            </div>
          </section>
        </article>
      </Container>
    </main>
  );
}
