import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import {
  CompanyListItem, CompanyDetail, OutreachAsset, Contact, FilterParams, FilterDefaults,
  PondStats, DensityPoint,
} from './models';

const BASE = 'http://localhost:8000';

@Injectable({ providedIn: 'root' })
export class ApiService {
  private http = inject(HttpClient);

  top10(): Observable<CompanyListItem[]> {
    return this.http.get<CompanyListItem[]>(`${BASE}/companies/top10`);
  }

  filterDefaults(): Observable<FilterDefaults> {
    return this.http.get<FilterDefaults>(`${BASE}/companies/filters/defaults`);
  }

  rank(filters: FilterParams): Observable<CompanyListItem[]> {
    return this.http.post<CompanyListItem[]>(`${BASE}/companies/rank`, filters);
  }

  stats(filters: FilterParams): Observable<PondStats> {
    return this.http.post<PondStats>(`${BASE}/companies/stats`, filters);
  }

  density(): Observable<DensityPoint[]> {
    return this.http.get<DensityPoint[]>(`${BASE}/companies/density`);
  }

  company(id: number): Observable<CompanyDetail> {
    return this.http.get<CompanyDetail>(`${BASE}/companies/${id}`);
  }

  outreach(id: number): Observable<OutreachAsset> {
    return this.http.get<OutreachAsset>(`${BASE}/companies/${id}/outreach`);
  }

  markContacted(id: number): Observable<unknown> {
    return this.http.post(`${BASE}/companies/${id}/mark-contacted`, {});
  }

  generateOutreach(id: number): Observable<{ status: string; company_id: number }> {
    return this.http.post<{ status: string; company_id: number }>(
      `${BASE}/companies/${id}/outreach/generate`, {}
    );
  }

  getContacts(id: number): Observable<{ contacts: Contact[]; persisted: boolean }> {
    return this.http.get<{ contacts: Contact[]; persisted: boolean }>(
      `${BASE}/companies/${id}/contacts`
    );
  }
}
