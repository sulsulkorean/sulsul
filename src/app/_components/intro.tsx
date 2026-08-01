import { APP_URL, SITE_NAME, SITE_TAGLINE } from "@/lib/constants";

export function Intro() {
  return (
    <section className="flex-col md:flex-row flex items-center md:justify-between mt-16 mb-16 md:mb-12">
      <div>
        <h1 className="text-5xl md:text-7xl font-bold tracking-tighter leading-tight md:pr-8">
          {SITE_NAME}
        </h1>
        <p className="text-xl md:text-2xl mt-3 text-slate-600 dark:text-slate-300">
          {SITE_TAGLINE}
        </p>
      </div>
      <h4 className="text-center md:text-left text-lg mt-5 md:pl-8 max-w-md">
        Real Korean you can say out loud on your first trip — cafes, taxis,
        convenience stores, and the moments that used to freeze you.{" "}
        <a
          href={`${APP_URL}/?utm_source=blog&utm_medium=header&utm_campaign=seo`}
          className="underline hover:text-pink-500 duration-200 transition-colors font-semibold"
        >
          Open the SULSUL app →
        </a>
      </h4>
    </section>
  );
}
