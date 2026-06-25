import { Component, inject, input, signal, effect } from '@angular/core';
import { RouterLink } from '@angular/router';

import { ApiService } from '../../core/api';
import { CompanyDetail } from '../../core/models';
import { Heatmap } from '../../shared/heatmap/heatmap';
import { ConnectionsPanel } from './connections-panel/connections-panel';

@Component({
  selector: 'app-company-detail',
  imports: [RouterLink, Heatmap, ConnectionsPanel],
  templateUrl: './company-detail.html',
  styleUrl: './company-detail.scss',
})
export class CompanyDetailPage {
  private api = inject(ApiService);
  id = input.required<string>(); // from route param (withComponentInputBinding)
  company = signal<CompanyDetail | null>(null);

  constructor() {
    effect(() => {
      this.reload();
    });
  }

  /** Re-fetch the company so the heatmap (warm_connection) + rank reflect a new tie. */
  reload() {
    this.api.company(Number(this.id())).subscribe((c) => this.company.set(c));
  }
}
