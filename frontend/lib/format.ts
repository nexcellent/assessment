const MONTH_YEAR = new Intl.DateTimeFormat('en-GB', { month: 'short', year: 'numeric', timeZone: 'UTC' });

const parse = (iso: string): Date => new Date(`${iso}T00:00:00Z`);

/** "Mar 2021" for an ISO date; an empty string for none. */
export function formatMonth(iso: string | null): string {
  return iso ? MONTH_YEAR.format(parse(iso)) : '';
}

/** "Mar 2021 – Jun 2022", "Mar 2021 – today" while open, or what little is known. */
export function formatPeriod(start: string | null, end: string | null): string {
  if (!start) {
    return end ? `until ${formatMonth(end)}` : 'Period not given';
  }
  return `${formatMonth(start)} – ${end ? formatMonth(end) : 'today'}`;
}

/** "14 months"; null while the duration is unknown. */
export function formatDuration(months: number | null): string | null {
  if (months === null) {
    return null;
  }
  return months === 1 ? '1 month' : `${months} months`;
}

interface Dated {
  start_date: string | null;
  end_date: string | null;
}

/**
 * Whole years from the earliest station to the latest one, or to today while one is open.
 * Measured across the span rather than added up, so overlapping stations count once.
 */
export function yearsOfExperience(stations: Dated[], today: Date = new Date()): number {
  const dated = stations.filter((station) => station.start_date);
  if (dated.length === 0) {
    return 0;
  }
  const starts = dated.map((station) => parse(station.start_date as string).getTime());
  const ends = dated.map((station) => (station.end_date ? parse(station.end_date).getTime() : today.getTime()));
  const start = new Date(Math.min(...starts));
  const end = new Date(Math.max(...ends));
  const months = (end.getUTCFullYear() - start.getUTCFullYear()) * 12 + (end.getUTCMonth() - start.getUTCMonth());
  return Math.max(0, Math.floor(months / 12));
}
