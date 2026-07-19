export const formatDate = (date: Date, locale = 'en-US'): string =>
  new Intl.DateTimeFormat(locale, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  }).format(date);
