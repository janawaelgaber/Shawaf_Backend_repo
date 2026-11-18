export const originalObjectKey = (videoId: string): string => `videos/${videoId}/original.mp4`;

export const clipObjectKey = (videoId: string, startMs: number, endMs: number): string =>
  `clips/${videoId}/${startMs}-${endMs}-h264_720p.mp4`;
