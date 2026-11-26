import {
  BadRequestException,
  Injectable,
  NotFoundException,
} from '@nestjs/common';
import { Prisma } from '@prisma/client';
import { PrismaService } from '../prisma/prisma.service';
import { ShawafException, ErrorCode } from '../common/errors/shawaf-exception';
import {
  UpsertStreamDto,
  UpsertDetectionRulesDto,
} from './dto/stream.dto';

const ALLOWED_LABELS = [
  'fight',
  'fall',
  'running',
  'crowd_formation',
  'fire',
];

@Injectable()
export class CamerasService {
  constructor(private readonly prisma: PrismaService) {}

  async createSite(organizationId: string, dto: { name: string }) {
    const site = await this.prisma.site.create({
      data: { organizationId, name: dto.name },
      select: { id: true, organizationId: true, name: true },
    });

    return {
      id: site.id,
      organization_id: site.organizationId,
      name: site.name,
    };
  }

  async createCamera(
    organizationId: string,
    dto: { site_id: string; display_name: string },
  ) {
    const site = await this.prisma.site.findFirst({
      where: { id: dto.site_id, organizationId },
      select: { id: true },
    });

    if (!site) throw new NotFoundException('Site not found');

    const camera = await this.prisma.camera.create({
      data: {
        organizationId,
        siteId: dto.site_id,
        displayName: dto.display_name,
      },
      select: {
        id: true,
        organizationId: true,
        siteId: true,
        displayName: true,
      },
    });

    return this.cameraResponse(camera);
  }

  async listCameras(organizationId: string) {
    const cameras = await this.prisma.camera.findMany({
      where: { organizationId },
      select: {
        id: true,
        organizationId: true,
        siteId: true,
        displayName: true,
      },
      orderBy: { displayName: 'asc' },
    });

    return cameras.map((camera) => this.cameraResponse(camera));
  }

  async getCamera(organizationId: string, cameraId: string) {
    const camera = await this.prisma.camera.findFirst({
      where: { id: cameraId, organizationId },
      select: {
        id: true,
        organizationId: true,
        siteId: true,
        displayName: true,
      },
    });

    if (!camera) throw new NotFoundException('Camera not found');
    return this.cameraResponse(camera);
  }

  private cameraResponse(camera: {
    id: string;
    organizationId: string;
    siteId: string;
    displayName: string;
  }) {
    return {
      id: camera.id,
      organization_id: camera.organizationId,
      site_id: camera.siteId,
      display_name: camera.displayName,
    };
  }

  private async ensureCamera(organizationId: string, cameraId: string) {
    const camera = await this.prisma.camera.findFirst({
      where: { id: cameraId, organizationId },
      select: { id: true },
    });

    if (!camera) throw new NotFoundException('Camera not found');
  }

  private streamResponse(stream: {
    cameraId: string;
    mode: string;
    rtspUrl: string | null;
    configVersion: number;
    monitoring: string;
    rules: Prisma.JsonValue;
  }) {
    return {
      camera_id: stream.cameraId,
      mode: stream.mode,
      rtsp_url: stream.rtspUrl,
      config_version: stream.configVersion,
      monitoring: stream.monitoring,
      rules: stream.rules,
    };
  }

  async upsertStream(
    organizationId: string,
    cameraId: string,
    dto: UpsertStreamDto,
  ) {
    await this.ensureCamera(organizationId, cameraId);

    if (!dto.rtsp_url.startsWith('rtsp://') &&
        !dto.rtsp_url.startsWith('rtsps://')) {
      throw new ShawafException(
        ErrorCode.VALIDATION_FAILED,
        'rtsp_url must use rtsp:// or rtsps://',
      );
    }

    const stream = await this.prisma.cameraStream.upsert({
      where: { cameraId },
      create: {
        cameraId,
        mode: dto.mode,
        rtspUrl: dto.rtsp_url,
      },
      update: {
        mode: dto.mode,
        rtspUrl: dto.rtsp_url,
        configVersion: { increment: 1 },
      },
    });

    return this.streamResponse(stream);
  }

  async upsertDetectionRules(
    organizationId: string,
    cameraId: string,
    dto: UpsertDetectionRulesDto,
  ) {
    await this.ensureCamera(organizationId, cameraId);

    for (const rule of dto.rules) {
      if (!ALLOWED_LABELS.includes(rule.label)) {
        throw new ShawafException(
          ErrorCode.LIVE_EVENT_LABEL_UNKNOWN,
          `Unknown live event label: ${rule.label}`,
        );
      }
    }

    const existing = await this.prisma.cameraStream.findUnique({
      where: { cameraId },
    });

    if (!existing) throw new NotFoundException('Stream not configured');

    const stream = await this.prisma.cameraStream.update({
      where: { cameraId },
      data: {
        rules: dto.rules as unknown as Prisma.InputJsonValue,
        configVersion: { increment: 1 },
      },
    });

    return this.streamResponse(stream);
  }

  async setMonitoring(
    organizationId: string,
    cameraId: string,
    monitoring: 'on' | 'off',
  ) {
    await this.ensureCamera(organizationId, cameraId);

    const existing = await this.prisma.cameraStream.findUnique({
      where: { cameraId },
    });

    if (!existing) throw new NotFoundException('Stream not configured');

    const stream = await this.prisma.cameraStream.update({
      where: { cameraId },
      data: { monitoring },
    });

    return this.streamResponse(stream);
  }
}
