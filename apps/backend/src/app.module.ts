import { MiddlewareConsumer, Module, NestModule } from '@nestjs/common';
import { RequestIdMiddleware } from './common/http/request-id.middleware';
import { AuthModule } from './auth/auth.module';
import { PrismaModule } from './prisma/prisma.module';
import { UsersModule } from './users/users.module';
import { OrganizationsModule } from './organizations/organizations.module';
import { HealthModule } from './health/health.module';
import { StorageModule } from './storage/storage.module';
import { CamerasModule } from './cameras/cameras.module';
import { VideosModule } from './videos/videos.module';
import { ClipsModule } from './clips/clips.module';
import { HmacModule } from './common/hmac/hmac.module';
import { InferenceClientModule } from './inference-client/inference-client.module';
import { InternalCallbacksModule } from './internal-callbacks/internal-callbacks.module';
import { SearchModule } from './search/search.module';
import { AlertsModule } from './alerts/alerts.module';

@Module({
  imports: [
    PrismaModule,
    AuthModule,
    UsersModule,
    OrganizationsModule,
    HealthModule,
    StorageModule,
    CamerasModule,
    VideosModule,
    ClipsModule,
    HmacModule,
    InferenceClientModule,
    InternalCallbacksModule,
    SearchModule,
    AlertsModule,
  ],
})
export class AppModule implements NestModule {
  configure(consumer: MiddlewareConsumer): void {
    consumer.apply(RequestIdMiddleware).forRoutes('{*path}');
  }
}
