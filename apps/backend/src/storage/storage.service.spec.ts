import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { CreateBucketCommand, HeadBucketCommand, S3Client } from '@aws-sdk/client-s3';
import { mkdtemp, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { StorageService } from './storage.service.js';

describe('StorageService', () => {
  let service: StorageService;
  let temporaryDirectory: string;

  beforeEach(async () => {
    temporaryDirectory = await mkdtemp(
      path.join(tmpdir(), 'shawaf-storage-'),
    );

    process.env.STORAGE_DRIVER = 'local';
    process.env.STORAGE_LOCAL_DIR = temporaryDirectory;
    process.env.MINIO_BUCKET = 'shawaf-media';

    service = new StorageService();
  });

  afterEach(async () => {
    await rm(temporaryDirectory, { recursive: true, force: true });
  });

  it('builds the required original video key', () => {
    expect(service.buildOriginalVideoKey('video-123')).toBe(
      'videos/video-123/original.mp4',
    );
  });

  it('builds the required clip key', () => {
    expect(service.buildClipKey('video-123', 10, 30)).toBe(
      'clips/video-123/10-30-h264_720p.mp4',
    );
  });

  it('rejects invalid video identifiers', () => {
    expect(() => service.buildOriginalVideoKey('../outside')).toThrow();
  });

  it('rejects invalid clip time ranges', () => {
    expect(() => service.buildClipKey('video-123', 30, 10)).toThrow();
    expect(() => service.buildClipKey('video-123', -1, 10)).toThrow();
  });

  it('uploads an object and returns its metadata', async () => {
    const result = await service.putObject({
      key: 'videos/video-123/original.mp4',
      body: Buffer.from('sample-video'),
      contentType: 'video/mp4',
    });

    expect(result).toEqual({
      key: 'videos/video-123/original.mp4',
      size: 12,
      contentType: 'video/mp4',
    });
  });

  it('returns size and content type from headObject', async () => {
    const key = 'videos/video-123/original.mp4';

    await service.putObject({
      key,
      body: Buffer.from('sample-video'),
      contentType: 'video/mp4',
    });

    await expect(service.headObject(key)).resolves.toEqual({
      key,
      size: 12,
      contentType: 'video/mp4',
    });
  });

  it('returns not found for a missing object', async () => {
    await expect(
      service.headObject('videos/video-123/original.mp4'),
    ).rejects.toMatchObject({
      response: {
        code: 'OBJECT_NOT_FOUND',
      },
    });
  });

  it('rejects unsafe object keys', async () => {
    await expect(
      service.putObject({
        key: 'videos/../outside/original.mp4',
        body: Buffer.from('test'),
        contentType: 'video/mp4',
      }),
    ).rejects.toThrow();
  });

  it('does not pretend local storage provides signed URLs', async () => {
    await expect(
      service.signedGetUrl('videos/video-123/original.mp4'),
    ).rejects.toMatchObject({
      response: {
        code: 'SIGNED_URL_UNAVAILABLE',
      },
    });
  });
  it('does not recreate an existing MinIO bucket', async () => {
    process.env.STORAGE_DRIVER = 'minio';
    process.env.MINIO_ENDPOINT = 'http://localhost:9000';
    process.env.MINIO_ACCESS_KEY = 'test-access';
    process.env.MINIO_SECRET_KEY = 'test-secret';

    service = new StorageService();

    const sendSpy = vi
      .spyOn(S3Client.prototype, 'send')
      .mockResolvedValue({} as never);

    await service.putObject({
      key: 'videos/video-123/original.mp4',
      body: Buffer.from('sample-video'),
      contentType: 'video/mp4',
    });

    expect(sendSpy.mock.calls[0][0]).toBeInstanceOf(HeadBucketCommand);
    expect(
      sendSpy.mock.calls.some(([command]) =>
        command instanceof CreateBucketCommand,
      ),
    ).toBe(false);
  });

  it('creates the MinIO bucket when it does not exist', async () => {
    process.env.STORAGE_DRIVER = 'minio';
    process.env.MINIO_ENDPOINT = 'http://localhost:9000';
    process.env.MINIO_ACCESS_KEY = 'test-access';
    process.env.MINIO_SECRET_KEY = 'test-secret';

    service = new StorageService();

    const notFoundError = Object.assign(
      new Error('Bucket not found'),
      { $metadata: { httpStatusCode: 404 } },
    );

    const sendSpy = vi
      .spyOn(S3Client.prototype, 'send')
      .mockRejectedValueOnce(notFoundError)
      .mockResolvedValue({} as never);

    await service.putObject({
      key: 'videos/video-123/original.mp4',
      body: Buffer.from('sample-video'),
      contentType: 'video/mp4',
    });

    expect(sendSpy.mock.calls[0][0]).toBeInstanceOf(HeadBucketCommand);
    expect(sendSpy.mock.calls[1][0]).toBeInstanceOf(CreateBucketCommand);
  });

  it('does not create a bucket when MinIO returns a permission error', async () => {
    process.env.STORAGE_DRIVER = 'minio';
    process.env.MINIO_ENDPOINT = 'http://localhost:9000';
    process.env.MINIO_ACCESS_KEY = 'test-access';
    process.env.MINIO_SECRET_KEY = 'test-secret';

    service = new StorageService();

    const forbiddenError = Object.assign(
      new Error('Access denied'),
      { $metadata: { httpStatusCode: 403 } },
    );

    const sendSpy = vi
      .spyOn(S3Client.prototype, 'send')
      .mockRejectedValueOnce(forbiddenError);

    await expect(
      service.putObject({
        key: 'videos/video-123/original.mp4',
        body: Buffer.from('sample-video'),
        contentType: 'video/mp4',
      }),
    ).rejects.toThrow('Access denied');

    expect(sendSpy).toHaveBeenCalledTimes(1);
    expect(
      sendSpy.mock.calls.some(([command]) =>
        command instanceof CreateBucketCommand,
      ),
    ).toBe(false);
  });

});
