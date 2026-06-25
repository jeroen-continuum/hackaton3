export interface ScoreBreakdown {
  buyer_intent: number;
  impact_potential: number;
  financial_fit: number;
  sector_fit: number;
  warm_connection: number;
}

export interface CompanyListItem {
  id: number;
  name: string;
  sector: string | null;
  region: string;
  rank: number;
  score: number;
  breakdown: ScoreBreakdown;
  municipality: string | null;
  latitude: number | null;
  longitude: number | null;
}

export interface CompanyDetail {
  id: number;
  name: string;
  enterprise_number: string;
  sector: string | null;
  nace_code: string | null;
  region: string;
  website: string | null;
  address?: string | null;
  municipality?: string | null;
  latitude?: number | null;
  longitude?: number | null;
  financials: { employees?: number; revenue?: number; ebitda?: number } | null;
  contacts: { name: string; title?: string; email?: string }[];
  vacancies: { title: string; is_it_role: boolean }[];
  tech: { technologies: string[]; legacy_score: number } | null;
  score: { total: number; rank: number; breakdown: ScoreBreakdown } | null;
}

export interface Employee {
  id: number;
  name: string;
  email: string | null;
  title: string | null;
  active: boolean;
}

export type ConnectionType = 'EMPLOYER' | 'CLIENT' | 'PERSONAL';

export interface Connection {
  id: number;
  employee_id: number;
  employee_name: string;
  employee_title: string | null;
  type: ConnectionType;
  start_date: string | null;
  end_date: string | null;
  note: string | null;
  strength: number;
}

/** Warm ties for a company, strongest first; is_client inferred from a CLIENT tie. */
export interface CompanyConnections {
  connections: Connection[];
  is_client: boolean;
}

export interface OutreachAsset {
  email_subject: string;
  email_body: string;
  teaser_title: string;
  teaser_preview: string;
  teaser_full: string;
}

export interface Contact {
  name: string;
  title: string;
  email: string;
}

export interface FilterParams {
  regions: string[];
  nace_include_prefixes: string[];
  nace_exclude_prefixes: string[];
  min_employees: number;
  max_employees: number;
  // Financial filter as an EBITDA range (€). max_ebitda null = no upper bound.
  min_ebitda: number;
  max_ebitda: number | null;
  apply_size: boolean;
  apply_financial: boolean;
  // Keep only companies we have a warm connection to.
  only_warm?: boolean;
  // Drop companies that are already our clients.
  exclude_clients?: boolean;
  // Area filter — all omitted/null = no geographic restriction.
  center_lat?: number | null;
  center_lon?: number | null;
  radius_km?: number | null;
}

/** A chosen area (center + radius), or null when the area filter is off. */
export interface Area {
  center_lat: number;
  center_lon: number;
  radius_km: number;
}

/** Pond scale + speed headline for the dashboard banner. */
export interface PondStats {
  total: number;
  matched: number;
  shortlist: number;
  elapsed_ms: number;
}

/** One geocoded location with its company count, for the map density layer. */
export interface DensityPoint {
  lat: number;
  lon: number;
  count: number;
}

export interface FilterDefaults extends FilterParams {
  center_lat: number;
  center_lon: number;
  available_sectors: string[];
  nace_sector_labels: Record<string, string>;
}
