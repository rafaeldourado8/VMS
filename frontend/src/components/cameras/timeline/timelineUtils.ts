export const timeToX = (time: number, width: number, viewStart: number, viewEnd: number) => {
  const range = viewEnd - viewStart;
  return ((time - viewStart) / range) * width;
};

export const xToTime = (x: number, width: number, viewStart: number, viewEnd: number) => {
  const range = viewEnd - viewStart;
  return viewStart + (x * (range / width));
};

export const getTimeIntervals = (range: number) => {
  if (range > 12 * 3600 * 1000) {
    return { major: 2 * 3600 * 1000, minor: 3600 * 1000 };
  } else if (range > 3600 * 1000) {
    return { major: 3600 * 1000, minor: 900 * 1000 };
  } else if (range > 60 * 60 * 1000) {
    return { major: 30 * 60 * 1000, minor: 10 * 60 * 1000 };
  }
  return { major: 10 * 60 * 1000, minor: 60 * 1000 };
};
