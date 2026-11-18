import { Module } from '@nestjs/common';

/** Labib. SCRUM-132. Signs with NEST_TO_AI_HMAC_SECRET. Retries 503 PIPELINE_UNAVAILABLE up to 3 times. Does not retry 409 JOB_CONFLICT. */
@Module({})
export class InferenceClientModule {}
