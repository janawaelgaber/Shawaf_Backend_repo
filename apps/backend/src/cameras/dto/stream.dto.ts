import {
  IsArray, IsIn, IsInt, IsNotEmpty, IsNumber, IsString,
  Max, Min, ValidateNested,
} from 'class-validator';
import { Type } from 'class-transformer';

export class UpsertStreamDto {
  @IsIn(['rtsp_pull'])
  mode!: string;

  @IsString()
  @IsNotEmpty()
  rtsp_url!: string;
}

export class DetectionRuleDto {
  @IsString()
  label!: string;

  @IsNumber()
  @Min(0)
  @Max(1)
  min_score!: number;

  @IsInt()
  @Min(0)
  min_duration_ms!: number;

  @IsInt()
  @Min(0)
  cooldown_s!: number;
}

export class UpsertDetectionRulesDto {
  @IsArray()
  @ValidateNested({ each: true })
  @Type(() => DetectionRuleDto)
  rules!: DetectionRuleDto[];
}
