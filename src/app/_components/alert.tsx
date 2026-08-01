import Container from "@/app/_components/container";
import { appLink } from "@/lib/constants";
import cn from "classnames";

type Props = {
  preview?: boolean;
};

const Alert = ({ preview }: Props) => {
  if (!preview) return null;

  return (
    <div className={cn("border-b dark:bg-slate-800 bg-neutral-800 border-neutral-800 text-white")}>
      <Container>
        <div className="py-2 text-center text-sm">
          This page is a preview.{" "}
          <a
            href="/api/exit-preview"
            className="underline hover:text-teal-300 duration-200 transition-colors"
          >
            Click here
          </a>{" "}
          to exit preview mode. Or{" "}
          <a
            href={appLink("alert")}
            className="underline hover:text-teal-300 duration-200 transition-colors"
          >
            open SULSUL
          </a>
          .
        </div>
      </Container>
    </div>
  );
};

export default Alert;
