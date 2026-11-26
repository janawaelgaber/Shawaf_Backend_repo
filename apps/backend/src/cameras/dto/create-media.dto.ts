import { IsNotEmpty, IsString, IsUUID, MaxLength } from 'class-validator';

export class CreateSiteDto {
  @IsString()
  @IsNotEmpty()
  @MaxLength(120)
  name!: string;
}

export class CreateCameraDto {
  @IsUUID()
  site_id!: string;

  @IsString()
  @IsNotEmpty()
  @MaxLength(120)
  display_name!: string;
}
