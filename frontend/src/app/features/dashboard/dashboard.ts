import { Component, computed, inject, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { DecimalPipe } from '@angular/common';

import { ApiService } from '../../core/api';
import {
  Area, CompanyListItem, DensityPoint, FilterDefaults, FilterParams, PondStats,
} from '../../core/models';
import { Heatmap } from '../../shared/heatmap/heatmap';
import { FilterPanel } from './filter-panel/filter-panel';
import { ProspectMap } from './prospect-map/prospect-map';
import { ScaleBanner } from './scale-banner/scale-banner';

@Component({
  selector: 'app-dashboard',
  imports: [RouterLink, DecimalPipe, Heatmap, FilterPanel, ProspectMap, ScaleBanner],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.scss',
})
export class Dashboard {
  private api = inject(ApiService);
  companies = signal<CompanyListItem[]>([]);
  loading = signal(true);
  defaults = signal<FilterDefaults | null>(null);
  stats = signal<PondStats | null>(null);
  density = signal<DensityPoint[]>([]);

  /** Last filters applied from the panel (null = panel untouched). */
  private lastFilters: FilterParams | null = null;
  /** Chosen area (null = area filter off). */
  private area = signal<Area | null>(null);

  /** Initial map center from the backend defaults (falls back to Belgium). */
  mapCenter = computed(() => {
    const d = this.defaults();
    return { lat: d?.center_lat ?? 50.8503, lon: d?.center_lon ?? 4.3517 };
  });

  constructor() {
    this.api.filterDefaults().subscribe((d) => {
      this.defaults.set(d);
      this.refreshStats(); // now baseFilters() resolves → fill the funnel
    });
    this.api.density().subscribe((d) => this.density.set(d));
    this.load();
  }

  /** Initial unfiltered (default-ICP) view. */
  load() {
    this.loading.set(true);
    this.api.top10().subscribe((rows) => {
      this.companies.set(rows);
      this.loading.set(false);
    });
    this.refreshStats();
  }

  /** Panel "Apply" — store the chosen filters and re-rank. */
  applyFilters(filters: FilterParams) {
    this.lastFilters = filters;
    this.rerank();
  }

  /** Map area picker changed — store and re-rank. */
  onAreaChange(area: Area | null) {
    this.area.set(area);
    this.rerank();
  }

  /** Re-run selection + scoring with the current filters + area. */
  private rerank() {
    const filters = this.currentFilters();
    if (!filters) {
      this.load();
      return;
    }
    this.loading.set(true);
    this.api.rank(filters).subscribe((rows) => {
      this.companies.set(rows);
      this.loading.set(false);
    });
    this.refreshStats();
  }

  /** Recompute the scale/speed funnel for the current filters + area. */
  private refreshStats() {
    const filters = this.currentFilters();
    if (filters) this.api.stats(filters).subscribe((s) => this.stats.set(s));
  }

  /** Current base filters merged with the chosen area (null until defaults load). */
  private currentFilters(): FilterParams | null {
    const base = this.baseFilters();
    if (!base) return null;
    const a = this.area();
    return {
      ...base,
      center_lat: a?.center_lat ?? null,
      center_lon: a?.center_lon ?? null,
      radius_km: a?.radius_km ?? null,
    };
  }

  /** Panel filters if set, else the backend defaults projected onto FilterParams. */
  private baseFilters(): FilterParams | null {
    if (this.lastFilters) return this.lastFilters;
    const d = this.defaults();
    if (!d) return null;
    return {
      regions: d.regions,
      nace_include_prefixes: d.nace_include_prefixes,
      nace_exclude_prefixes: d.nace_exclude_prefixes,
      min_employees: d.min_employees,
      max_employees: d.max_employees,
      min_ebitda: d.min_ebitda,
      max_ebitda: d.max_ebitda,
      apply_size: d.apply_size,
      apply_financial: d.apply_financial,
    };
  }

  contact(id: number, event: Event) {
    event.stopPropagation();
    this.api.markContacted(id).subscribe(() => this.load());
  }
}
