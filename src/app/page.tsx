import Container from "@/app/_components/container";
import { HeroPost } from "@/app/_components/hero-post";
import { Intro } from "@/app/_components/intro";
import { MoreStories } from "@/app/_components/more-stories";
import { getAllPosts } from "@/lib/api";
import { appLink } from "@/lib/constants";
import Link from "next/link";

export default function Index() {
  const allPosts = getAllPosts();
  const heroPost = allPosts[0];
  const morePosts = allPosts.slice(1);

  return (
    <main>
      <Container>
        <Intro />
        {heroPost ? (
          <HeroPost
            title={heroPost.title}
            coverImage={heroPost.coverImage}
            date={heroPost.date}
            author={heroPost.author}
            slug={heroPost.slug}
            excerpt={heroPost.excerpt}
          />
        ) : (
          <section className="mb-16 md:mb-20 p-8 rounded-2xl bg-pink-50 dark:bg-slate-800 border border-pink-100 dark:border-slate-700">
            <h2 className="text-3xl md:text-4xl font-bold tracking-tight mb-4">
              New posts are on the way
            </h2>
            <p className="text-lg mb-6 text-slate-600 dark:text-slate-300">
              We&apos;re publishing survival Korean you can actually say out
              loud — cafes, taxis, convenience stores, and the moments that
              used to freeze you. While you wait, meet the app.
            </p>
            <div className="flex flex-wrap gap-4">
              <a
                href={appLink("home_empty")}
                className="bg-pink-500 hover:bg-pink-600 text-white font-bold py-3 px-8 rounded-full"
              >
                Start speaking on SULSUL →
              </a>
              <Link href="/what-is-sulsul" className="font-bold underline py-3">
                What is SULSUL?
              </Link>
            </div>
          </section>
        )}
        {morePosts.length > 0 && <MoreStories posts={morePosts} />}
      </Container>
    </main>
  );
}
