export type StorageDriver = 'local' | 'minio';

export interface PutObjectInput {
  key: string;
  body: Buffer | Uint8Array;
  contentType: string;
}

export interface ObjectMetadata {
  key: string;
  size: number;
  contentType: string;
}

export interface StorageOptions {
  driver: StorageDriver;
  localDirectory: string;
  bucket: string;
  endpoint?: string;
  accessKey?: string;
  secretKey?: string;
  region: string;
}
