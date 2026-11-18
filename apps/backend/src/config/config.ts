export const nestConfig = {
  port: 4000,
  publicPrefix: '/api/v1',
  internalPrefix: '/internal/v1',
  databaseUrl: process.env.DATABASE_URL ?? '',
  nestToAiHmacSecret: process.env.NEST_TO_AI_HMAC_SECRET ?? '',
  aiToNestHmacSecret: process.env.AI_TO_NEST_HMAC_SECRET ?? '',
  s3Bucket: process.env.S3_BUCKET ?? 'shawaf-media',
  playbackPadMs: Number(process.env.PLAYBACK_PAD_MS ?? '2000'),
};
