/* eslint-disable prettier/prettier */
import type { components } from './schema.d.ts';

// Something went wrong
export type Swr = any;

export type PaginationType<D> = {
  data: D[];
  total: number;
  limit: number;
  skip: number;
};

export type FindingMetaData = {
  scanType?: string;
  incrementNumber?: number;
};

export type AuditCountOverTime = components['schemas']['AuditCountOverTime'];
export type AuditMultiple = components['schemas']['AuditMultiple'];
export type AuditRead = components['schemas']['AuditRead'];
export type DateCountModel = components['schemas']['DateCountModel'];
export type DateFilter = components['schemas']['DateFilter'];
export type DetailedFindingRead = components['schemas']['DetailedFindingRead'];
export type AugmentedDetailedFindingRead = DetailedFindingRead & FindingMetaData;
export type FindingCountModel_RepositoryRead_ = components['schemas']['FindingCountModel_RepositoryRead_'];
export type FindingCountOverTime = components['schemas']['FindingCountOverTime'];
export type FindingCreate = components['schemas']['FindingCreate'];
export type FindingPatch = components['schemas']['FindingPatch'];
export type FindingRead = components['schemas']['FindingRead'];
export type FindingStatus = components['schemas']['FindingStatus'];
export type PaginationModel_AuditRead_ = components['schemas']['PaginationModel_AuditRead_'];
export type PaginationModel_DateCountModel_ = components['schemas']['PaginationModel_DateCountModel_'];
export type PaginationModel_DetailedFindingRead_ = components['schemas']['PaginationModel_DetailedFindingRead_'];
export type PaginationModel_FindingRead_ = components['schemas']['PaginationModel_FindingRead_'];
export type PaginationModel_RepositoryEnrichedRead_ = components['schemas']['PaginationModel_RepositoryEnrichedRead_'];
export type PaginationModel_RepositoryRead_ = components['schemas']['PaginationModel_RepositoryRead_'];
export type PaginationModel_RulePackRead_ = components['schemas']['PaginationModel_RulePackRead_'];
export type PaginationModel_ScanRead_ = components['schemas']['PaginationModel_ScanRead_'];
export type PaginationModel_VCSInstanceRead_ = components['schemas']['PaginationModel_VCSInstanceRead_'];
export type PersonalAuditMetrics = components['schemas']['PersonalAuditMetrics'];
export type RepositoryCreate = components['schemas']['RepositoryCreate'];
export type RepositoryEnrichedRead = components['schemas']['RepositoryEnrichedRead'];
export type RepositoryRead = components['schemas']['RepositoryRead'];
export type RuleFindingCountModel = components['schemas']['RuleFindingCountModel'];
export type RulePackRead = components['schemas']['RulePackRead'];
export type ScanCreate = components['schemas']['ScanCreate'];
export type ScanRead = components['schemas']['ScanRead'];
export type ScanType = components['schemas']['ScanType'];
export type StatusCount = components['schemas']['StatusCount'];
export type VCSInstanceCreate = components['schemas']['VCSInstanceCreate'];
export type VCSInstanceRead = components['schemas']['VCSInstanceRead'];
export type VCSProviders = components['schemas']['VCSProviders'];
