export type DataSetObject = {
  borderWidth: number;
  cubicInterpolationMode: string;
  data: number[];
  pointStyle: string;
  pointRadius: number;
  pointHoverRadius: number;
  label?: string;
  hidden?: boolean;
  borderColor?: string;
  pointBackgroundColor?: string;
  backgroundColor?: string;
};

export type DataSetObjectCollection = {
  [key: string]: DataSetObject;
};

export type AuditData = {
  time_period: string;
  audit_by_auditor_count: { [key: string]: number };
  total?: number;
};
