import { ArgumentsHost, Catch, ExceptionFilter, HttpException } from '@nestjs/common';
import { Response } from 'express';

export const ErrorCode = {
  INVALID_CREDENTIALS: { status: 401, code: 'INVALID_CREDENTIALS' },
  ACCOUNT_DISABLED: { status: 401, code: 'ACCOUNT_DISABLED' },
  RATE_LIMITED: { status: 429, code: 'RATE_LIMITED' },
  INVITE_NOT_ALLOWED: { status: 403, code: 'INVITE_NOT_ALLOWED' },
  CAMERA_NOT_FOUND: { status: 404, code: 'CAMERA_NOT_FOUND' },
  INVALID_SIGNATURE: { status: 401, code: 'INVALID_SIGNATURE' },
  JOB_CONFLICT: { status: 409, code: 'JOB_CONFLICT' },
  JOB_NOT_FOUND: { status: 404, code: 'JOB_NOT_FOUND' },
  PIPELINE_UNAVAILABLE: { status: 503, code: 'PIPELINE_UNAVAILABLE' },
  VALIDATION_FAILED: { status: 400, code: 'VALIDATION_FAILED' },
  LIVE_EVENT_LABEL_UNKNOWN: { status: 400, code: 'LIVE_EVENT_LABEL_UNKNOWN' },
  LIVE_STREAM_CONFLICT: { status: 409, code: 'LIVE_STREAM_CONFLICT' },
} as const;

export class ShawafException extends HttpException {
  constructor(
    error: (typeof ErrorCode)[keyof typeof ErrorCode],
    message: string,
    details: unknown = null,
  ) {
    super({ code: error.code, message, details }, error.status);
  }
}

@Catch(ShawafException)
export class ShawafExceptionFilter implements ExceptionFilter {
  catch(exception: ShawafException, host: ArgumentsHost): void {
    const http = host.switchToHttp();
    const response = http.getResponse<Response>();
    const body = exception.getResponse() as { code: string; message: string; details: unknown };
    const requestId = response.locals.requestId as string | undefined;
    response.status(exception.getStatus()).json({
      error: {
        code: body.code,
        message: body.message,
        request_id: requestId ?? null,
        details: body.details,
      },
    });
  }
}
