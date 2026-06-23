import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { CompanyListItem, CompanyDetail, OutreachAsset } from './models';

const BASE = 'http://localhost:8000';

@Injectable({ providedIn: 'root' })
export class ApiService {
  private http = inject(HttpClient);

  top10(): Observable<CompanyListItem[]> {
    return this.http.get<CompanyListItem[]>(`${BASE}/companies/top10`);
  }

  company(id: number): Observable<CompanyDetail> {
    return this.http.get<CompanyDetail>(`${BASE}/companies/${id}`);
  }

  outreach(id: number): Observable<OutreachAsset> {
    return this.http.get<OutreachAsset>(`${BASE}/companies/${id}/outreach`);
  }

  markContacted(id: number): Observable<unknown> {
    return this.http.post(`${BASE}/scoring/${id}/contacted`, {});
  }
}
