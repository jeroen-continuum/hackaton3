import { Component, inject, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { DecimalPipe } from '@angular/common';

import { ApiService } from '../../core/api';
import { CompanyListItem } from '../../core/models';
import { Heatmap } from '../../shared/heatmap/heatmap';

@Component({
  selector: 'app-dashboard',
  imports: [RouterLink, DecimalPipe, Heatmap],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.scss',
})
export class Dashboard {
  private api = inject(ApiService);
  companies = signal<CompanyListItem[]>([]);
  loading = signal(true);

  constructor() {
    this.load();
  }

  load() {
    this.loading.set(true);
    this.api.top10().subscribe((rows) => {
      this.companies.set(rows);
      this.loading.set(false);
    });
  }

  contact(id: number, event: Event) {
    event.stopPropagation();
    this.api.markContacted(id).subscribe(() => this.load());
  }
}
