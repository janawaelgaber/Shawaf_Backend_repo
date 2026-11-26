import {
  Body,
  Controller,
  Get,
  Param,
  ParseUUIDPipe,
  Post,
  Put,
  Req,
  UnauthorizedException,
} from '@nestjs/common';
import { Request } from 'express';
import { CamerasService } from './cameras.service';
import { CreateSiteDto, CreateCameraDto } from './dto/create-media.dto';
import {
  UpsertStreamDto,
  UpsertDetectionRulesDto,
} from './dto/stream.dto';

type AuthenticatedRequest = Request & {
  user?: {
    user_id: string;
    organization_id: string;
    role: string;
  };
};

@Controller()
export class CamerasController {
  constructor(private readonly camerasService: CamerasService) {}

  private organizationId(req: AuthenticatedRequest): string {
    const id = req.user?.organization_id;
    if (!id) throw new UnauthorizedException();
    return id;
  }

  @Post('sites')
  async createSite(@Req() req: AuthenticatedRequest, @Body() dto: CreateSiteDto) {
    return { data: await this.camerasService.createSite(this.organizationId(req), dto) };
  }

  @Post('cameras')
  async createCamera(@Req() req: AuthenticatedRequest, @Body() dto: CreateCameraDto) {
    return { data: await this.camerasService.createCamera(this.organizationId(req), dto) };
  }

  @Get('cameras')
  async listCameras(@Req() req: AuthenticatedRequest) {
    return {
      data: { items: await this.camerasService.listCameras(this.organizationId(req)) },
    };
  }

  @Get('cameras/:cameraId')
  async getCamera(
    @Req() req: AuthenticatedRequest,
    @Param('cameraId', new ParseUUIDPipe()) cameraId: string,
  ) {
    return { data: await this.camerasService.getCamera(this.organizationId(req), cameraId) };
  }

  @Put('cameras/:cameraId/stream')
  async upsertStream(
    @Req() req: AuthenticatedRequest,
    @Param('cameraId', new ParseUUIDPipe()) cameraId: string,
    @Body() dto: UpsertStreamDto,
  ) {
    return {
      data: await this.camerasService.upsertStream(
        this.organizationId(req), cameraId, dto,
      ),
    };
  }

  @Put('cameras/:cameraId/detection-rules')
  async upsertDetectionRules(
    @Req() req: AuthenticatedRequest,
    @Param('cameraId', new ParseUUIDPipe()) cameraId: string,
    @Body() dto: UpsertDetectionRulesDto,
  ) {
    return {
      data: await this.camerasService.upsertDetectionRules(
        this.organizationId(req), cameraId, dto,
      ),
    };
  }

  @Post('cameras/:cameraId/monitoring/start')
  async startMonitoring(
    @Req() req: AuthenticatedRequest,
    @Param('cameraId', new ParseUUIDPipe()) cameraId: string,
  ) {
    return {
      data: await this.camerasService.setMonitoring(
        this.organizationId(req), cameraId, 'on',
      ),
    };
  }

  @Post('cameras/:cameraId/monitoring/stop')
  async stopMonitoring(
    @Req() req: AuthenticatedRequest,
    @Param('cameraId', new ParseUUIDPipe()) cameraId: string,
  ) {
    return {
      data: await this.camerasService.setMonitoring(
        this.organizationId(req), cameraId, 'off',
      ),
    };
  }
}
