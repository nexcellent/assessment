import Link from 'next/link';

export default function NotFound() {
  return (
    <div className="rounded-md border border-border bg-card px-6 py-12 text-center">
      <p className="eyebrow justify-center">Not found</p>
      <h1 className="text-2xl text-ink">There is no profile with this id.</h1>
      <Link
        href="/"
        className="mt-8 inline-block rounded-pill border border-ink px-7 py-3 font-head text-[0.92rem] font-medium text-ink transition-colors hover:bg-muted"
      >
        All profiles
      </Link>
    </div>
  );
}
