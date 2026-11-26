
import {
  Injectable,
  NotFoundException,
  ServiceUnavailableException,
} from '@nestjs/common';

import {
  CreateBucketCommand,
  GetObjectCommand,
  HeadBucketCommand,
  HeadObjectCommand,
  PutObjectCommand,
  S3Client,
} from '@aws-sdk/client-s3';

import { getSignedUrl } from '@aws-sdk/s3-request-presigner';

import {
  mkdir,
  readFile,
  writeFile,
} from 'node:fs/promises';

import path from 'node:path';
import { Buffer } from 'node:buffer';

import {
  PutObjectInput,
  ObjectMetadata,
  StorageDriver,
} from './storage.types.js';

@Injectable()
export class StorageService {
  private readonly driver: StorageDriver;
  private readonly bucket: string;
  private readonly localDirectory: string;
  private readonly s3Client?: S3Client;

  private bucketReady = false;
  private bucketInitialization?: Promise<void>;

  constructor() {
    const configuredDriver = process.env.STORAGE_DRIVER ?? 'local';

    if (
      configuredDriver !== 'local' &&
      configuredDriver !== 'minio'
    ) {
      throw new Error(
        'STORAGE_DRIVER must be either local or minio.',
      );
    }

    this.driver = configuredDriver;
    this.bucket = process.env.MINIO_BUCKET ?? 'shawaf-media';

    this.localDirectory = path.resolve(
      process.env.STORAGE_LOCAL_DIR ?? './storage-data',
    );

    if (this.driver === 'minio') {
      const endpoint = process.env.MINIO_ENDPOINT;
      const accessKey = process.env.MINIO_ACCESS_KEY;
      const secretKey = process.env.MINIO_SECRET_KEY;

      if (!endpoint || !accessKey || !secretKey) {
        throw new Error(
          'MINIO_ENDPOINT, MINIO_ACCESS_KEY, and MINIO_SECRET_KEY are required when STORAGE_DRIVER=minio.',
        );
      }

      this.s3Client = new S3Client({
        endpoint,
        region: process.env.MINIO_REGION ?? 'us-east-1',
        forcePathStyle: true,
        credentials: {
          accessKeyId: accessKey,
          secretAccessKey: secretKey,
        },
      });
    }
  }

  buildOriginalVideoKey(videoId: string): string {
    this.validateSegment(videoId, 'videoId');

    return `videos/${videoId}/original.mp4`;
  }

  buildClipKey(
    videoId: string,
    startMs: number,
    endMs: number,
  ): string {
    this.validateSegment(videoId, 'videoId');

    if (
      !Number.isSafeInteger(startMs) ||
      !Number.isSafeInteger(endMs) ||
      startMs < 0 ||
      endMs <= startMs
    ) {
      throw new Error(
        'Clip startMs and endMs must be valid non-negative milliseconds, with endMs greater than startMs.',
      );
    }

    return `clips/${videoId}/${startMs}-${endMs}-h264_720p.mp4`;
  }

  async putObject(
    input: PutObjectInput,
  ): Promise<ObjectMetadata> {
    this.validateKey(input.key);

    if (
      !input.contentType ||
      !input.contentType.trim()
    ) {
      throw new Error('contentType is required.');
    }

    const body = Buffer.from(input.body);

    if (this.driver === 'local') {
      const objectPath = this.getLocalObjectPath(input.key);
      const metadataPath = this.getLocalMetadataPath(input.key);

      await mkdir(path.dirname(objectPath), {
        recursive: true,
      });

      await mkdir(path.dirname(metadataPath), {
        recursive: true,
      });

      await writeFile(objectPath, body);

      await writeFile(
        metadataPath,
        JSON.stringify({
          contentType: input.contentType,
        }),
        'utf8',
      );

      return {
        key: input.key,
        size: body.byteLength,
        contentType: input.contentType,
      };
    }

    await this.ensureBucket();

    await this.s3Client!.send(
      new PutObjectCommand({
        Bucket: this.bucket,
        Key: input.key,
        Body: body,
        ContentType: input.contentType,
      }),
    );

    return {
      key: input.key,
      size: body.byteLength,
      contentType: input.contentType,
    };
  }

  async headObject(key: string): Promise<ObjectMetadata> {
    this.validateKey(key);

    if (this.driver === 'local') {
      const objectPath = this.getLocalObjectPath(key);
      const metadataPath = this.getLocalMetadataPath(key);

      try {
        const [body, metadataContent] = await Promise.all([
          readFile(objectPath),
          readFile(metadataPath, 'utf8'),
        ]);

        const metadata = JSON.parse(metadataContent) as {
          contentType?: string;
        };

        return {
          key,
          size: body.byteLength,
          contentType:
            metadata.contentType ?? 'application/octet-stream',
        };
      } catch (error) {
        if (
          error instanceof Error &&
          'code' in error &&
          error.code === 'ENOENT'
        ) {
          throw new NotFoundException({
            code: 'OBJECT_NOT_FOUND',
            message: 'The requested storage object was not found.',
          });
        }

        throw error;
      }
    }

    try {
      const result = await this.s3Client!.send(
        new HeadObjectCommand({
          Bucket: this.bucket,
          Key: key,
        }),
      );

      return {
        key,
        size: result.ContentLength ?? 0,
        contentType:
          result.ContentType ?? 'application/octet-stream',
      };
    } catch (error) {
      if (
        error instanceof Error &&
        ['NotFound', 'NoSuchKey', '404'].includes(error.name)
      ) {
        throw new NotFoundException({
          code: 'OBJECT_NOT_FOUND',
          message: 'The requested storage object was not found.',
        });
      }

      throw error;
    }
  }

  async signedGetUrl(
    key: string,
    expiresInSeconds = 900,
  ): Promise<string> {
    this.validateKey(key);

    if (
      !Number.isInteger(expiresInSeconds) ||
      expiresInSeconds < 1 ||
      expiresInSeconds > 604800
    ) {
      throw new Error(
        'URL expiry must be between 1 and 604800 seconds.',
      );
    }

    if (this.driver === 'local') {
      throw new ServiceUnavailableException({
        code: 'SIGNED_URL_UNAVAILABLE',
        message:
          'Signed download URLs require the MinIO storage driver.',
      });
    }

    await this.ensureBucket();

    return getSignedUrl(
      this.s3Client!,
      new GetObjectCommand({
        Bucket: this.bucket,
        Key: key,
      }),
      {
        expiresIn: expiresInSeconds,
      },
    );
  }

  private async ensureBucket(): Promise<void> {
    if (this.bucketReady) {
      return;
    }

    if (!this.bucketInitialization) {
      this.bucketInitialization = this.initializeBucket();
    }

    try {
      await this.bucketInitialization;
      this.bucketReady = true;
    } catch (error) {
      this.bucketInitialization = undefined;
      throw error;
    }
  }

  private async initializeBucket(): Promise<void> {
    try {
      await this.s3Client!.send(
        new HeadBucketCommand({
          Bucket: this.bucket,
        }),
      );

      return;
    } catch (error) {
      const statusCode = (
        error as {
          $metadata?: {
            httpStatusCode?: number;
          };
        }
      )?.$metadata?.httpStatusCode;

      const errorName =
        error instanceof Error ? error.name : '';

      const bucketDoesNotExist =
        statusCode === 404 ||
        ['NotFound', 'NoSuchBucket'].includes(errorName);

      if (!bucketDoesNotExist) {
        throw error;
      }
    }

    await this.s3Client!.send(
      new CreateBucketCommand({
        Bucket: this.bucket,
      }),
    );
  }

  private validateKey(key: string): void {
    if (
      !key ||
      key.startsWith('/') ||
      key.includes('\\') ||
      key.includes('\0') ||
      key.split('/').some(
        (part) =>
          !part ||
          part === '.' ||
          part === '..',
      )
    ) {
      throw new Error('Invalid storage object key.');
    }

    const validOriginalVideo =
      /^videos\/[^/]+\/original\.mp4$/.test(key);

    const validClip =
      /^clips\/[^/]+\/\d+-\d+-h264_720p\.mp4$/.test(key);

    if (!validOriginalVideo && !validClip) {
      throw new Error(
        'Storage object key does not match an approved media key format.',
      );
    }
  }

  private validateSegment(
    value: string,
    name: string,
  ): void {
    if (
      !value ||
      value === '.' ||
      value === '..' ||
      !/^[A-Za-z0-9_-]+$/.test(value)
    ) {
      throw new Error(`${name} is invalid.`);
    }
  }

  private getLocalObjectPath(key: string): string {
    const resolved = path.resolve(
      this.localDirectory,
      ...key.split('/'),
    );

    const relative = path.relative(
      this.localDirectory,
      resolved,
    );

    if (
      relative.startsWith('..') ||
      path.isAbsolute(relative)
    ) {
      throw new Error('Invalid local storage path.');
    }

    return resolved;
  }

  private getLocalMetadataPath(key: string): string {
    const metadataDirectory = path.join(
      this.localDirectory,
      '.shawaf-metadata',
    );

    const filename =
      Buffer.from(key).toString('base64url') + '.json';

    return path.join(metadataDirectory, filename);
  }
}
