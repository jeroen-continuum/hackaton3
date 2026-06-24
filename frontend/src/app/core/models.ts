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
}

export interface CompanyDetail {
  id: number;
  name: string;
  enterprise_number: string;
  sector: string | null;
  nace_code: string | null;
  region: string;
  website: string | null;
  financials: { employees?: number; revenue?: number; ebitda?: number } | null;
  contacts: { name: string; title?: string; email?: string }[];
  vacancies: { title: string; is_it_role: boolean }[];
  tech: { technologies: string[]; legacy_score: number } | null;
  score: { total: number; rank: number; breakdown: ScoreBreakdown } | null;
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
