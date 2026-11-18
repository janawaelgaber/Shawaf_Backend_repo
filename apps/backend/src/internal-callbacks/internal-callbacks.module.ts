import { Module } from '@nestjs/common';

/** Labib. SCRUM-117 and SCRUM-133. Verifies AI_TO_NEST_HMAC_SECRET. Every callback answers { data: { accepted, duplicate } }. */
@Module({})
export class InternalCallbacksModule {}
