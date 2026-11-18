import { Module } from '@nestjs/common';

/**
 * Labib. SCRUM-28.
 * string_to_sign = timestamp + newline + METHOD + newline + path + newline + hex(sha256(raw body)).
 * Path does not include the query. Skew over 300 seconds is 401 INVALID_SIGNATURE.
 * The shared vector is ai/contracts/fixtures/hmac_test_vector.json.
 */
@Module({})
export class HmacModule {}
