import { Component, inject, input, signal, effect } from '@angular/core';
import { RouterLink } from '@angular/router';

import { ApiService } from '../../core/api';
import { CompanyDetail } from '../../core/models';
import { Heatmap } from '../../shared/heatmap/heatmap';

@Component({
  selector: 'app-company-detail',
  imports: [RouterLink, Heatmap],
  templateUrl: './company-detail.html',
  styleUrl: './company-detail.scss',
})
export class CompanyDetailPage {
  private api = inject(ApiService);
  id = input.required<string>(); // from route param (withComponentInputBinding)
  company = signal<CompanyDetail | null>(null);

  constructor() {
    effect(() => {
      const cid = Number(this.id());
      this.api.company(cid).subscribe((c) => this.company.set(c));
    });
  }
}
