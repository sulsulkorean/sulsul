import Container from "@/app/_components/container";
import { APP_URL, SITE_NAME, SITE_TAGLINE, appLink } from "@/lib/constants";

export function Footer() {
  return (
    <footer className="bg-neutral-50 border-t border-neutral-200 dark:bg-slate-800">
      <Container>
        <div className="py-16 flex flex-col lg:flex-row items-center gap-8">
          <div className="lg:w-1/2 text-center lg:text-left">
            <h3 className="text-3xl lg:text-4xl font-bold tracking-tighter leading-tight mb-3">
              {SITE_NAME}
            </h3>
            <p className="text-lg text-slate-600 dark:text-slate-300 mb-2">
              {SITE_TAGLINE}
            </p>
            <p className="text-sm text-slate-500">
              Practise 100 survival patterns out loud, get corrected as you
              speak, then use them in Seoul.
            </p>
          </div>
          <div className="flex flex-col sm:flex-row justify-center items-center gap-4 lg:pl-4 lg:w-1/2">
            <a
              href={appLink("footer")}
              className="mx-3 bg-pink-500 hover:bg-pink-600 border border-pink-500 text-white font-bold py-3 px-10 duration-200 transition-colors rounded-full"
            >
              Start speaking →
            </a>
            <a
              href="/what-is-sulsul"
              className="mx-3 font-bold hover:underline"
            >
              What is SULSUL?
            </a>
            <a
              href={`${APP_URL}/`}
              className="mx-3 font-bold hover:underline text-slate-500"
            >
              sulsul.app
            </a>
          </div>
        </div>
        <div className="pb-10 text-center text-xs text-slate-400">
          © {new Date().getFullYear()} {SITE_NAME}. Survival Korean for your
          first trip.
        </div>
      </Container>
    </footer>
  );
}

export default Footer;
