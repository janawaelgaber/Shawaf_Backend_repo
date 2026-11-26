import { NestFactory } from '@nestjs/core';
import { ValidationPipe } from '@nestjs/common';
import { ShawafExceptionFilter } from './common/errors/shawaf-exception';
import { AppModule } from './app.module';

async function bootstrap(): Promise<void> {
  const app = await NestFactory.create(AppModule);
  app.useGlobalFilters(new ShawafExceptionFilter());
  app.useGlobalPipes(new ValidationPipe({ whitelist: true, transform: true }));
  // Public routes are /api/v1. Callbacks stay on /internal/v1.
  app.setGlobalPrefix('api/v1', { exclude: ['internal/{*path}'] });
  await app.listen(4000);
}

void bootstrap();
