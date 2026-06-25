import { Component, computed, effect, input, linkedSignal, output } from '@angular/core';

import { FilterDefaults, FilterParams } from '../../../core/models';

@Component({
  selector: 'app-filter-panel',
  templateUrl: './filter-panel.html',
  styleUrl: './filter-panel.scss',
})
export class FilterPanel {
  /** Defaults from the backend; also defines the available sectors/regions. */
  defaults = input<FilterDefaults | null>(null);
  /** Emitted (with the assembled filters) whenever any filter changes. */
  apply = output<FilterParams>();

  constructor() {
    // Filtering is cheap — apply immediately on any change instead of via a button.
    effect(() => this.emit());
  }

  readonly allRegions = ['BE', 'NL'];

  // sector label -> the NACE prefixes that map to it
  sectorPrefixes = computed<Record<string, string[]>>(() => {
    const labels = this.defaults()?.nace_sector_labels ?? {};
    const map: Record<string, string[]> = {};
    for (const [prefix, sector] of Object.entries(labels)) {
      (map[sector] ??= []).push(prefix);
    }
    return map;
  });
  sectors = computed(() => Object.keys(this.sectorPrefixes()));

  // Editable copies — reset automatically when defaults() changes.
  regions = linkedSignal<string[]>(() => [...(this.defaults()?.regions ?? [])]);
  minEmployees = linkedSignal(() => this.defaults()?.min_employees ?? 0);
  maxEmployees = linkedSignal(() => this.defaults()?.max_employees ?? 0);
  applySize = linkedSignal(() => this.defaults()?.apply_size ?? true);
  applyFinancial = linkedSignal(() => this.defaults()?.apply_financial ?? true);
  onlyWarm = linkedSignal(() => this.defaults()?.only_warm ?? false);
  excludeClients = linkedSignal(() => this.defaults()?.exclude_clients ?? false);
  minEbitda = linkedSignal(() => this.defaults()?.min_ebitda ?? 0);
  maxEbitda = linkedSignal<number | null>(() => this.defaults()?.max_ebitda ?? null);
  // EBITDA shown in millions of € — easier to read than raw 1500000.
  minEbitdaM = computed(() => this.minEbitda() / 1e6);
  maxEbitdaM = computed(() => (this.maxEbitda() == null ? null : this.maxEbitda()! / 1e6));
  selectedSectors = linkedSignal<string[]>(() => {
    const d = this.defaults();
    if (!d) return [];
    const inc = new Set(d.nace_include_prefixes);
    return Object.entries(this.sectorPrefixes())
      .filter(([, prefixes]) => prefixes.some((p) => inc.has(p)))
      .map(([sector]) => sector);
  });

  toggleRegion(region: string, checked: boolean) {
    this.regions.update((rs) =>
      checked ? [...new Set([...rs, region])] : rs.filter((r) => r !== region),
    );
  }

  toggleSector(sector: string, checked: boolean) {
    this.selectedSectors.update((ss) =>
      checked ? [...new Set([...ss, sector])] : ss.filter((s) => s !== sector),
    );
  }

  emit() {
    const include = this.selectedSectors().flatMap((s) => this.sectorPrefixes()[s] ?? []);
    this.apply.emit({
      regions: this.regions(),
      nace_include_prefixes: include,
      nace_exclude_prefixes: this.defaults()?.nace_exclude_prefixes ?? [],
      min_employees: Number(this.minEmployees()),
      max_employees: Number(this.maxEmployees()),
      min_ebitda: Number(this.minEbitda()) || 0,
      max_ebitda: this.maxEbitda(), // null = no upper bound
      apply_size: this.applySize(),
      apply_financial: this.applyFinancial(),
      only_warm: this.onlyWarm(),
      exclude_clients: this.excludeClients(),
    });
  }

  reset() {
    const d = this.defaults();
    if (d) {
      this.regions.set([...d.regions]);
      this.minEmployees.set(d.min_employees);
      this.maxEmployees.set(d.max_employees);
      this.applySize.set(d.apply_size);
      this.applyFinancial.set(d.apply_financial);
      this.onlyWarm.set(d.only_warm ?? false);
      this.excludeClients.set(d.exclude_clients ?? false);
      this.minEbitda.set(d.min_ebitda);
      this.maxEbitda.set(d.max_ebitda);
      const inc = new Set(d.nace_include_prefixes);
      this.selectedSectors.set(
        Object.entries(this.sectorPrefixes())
          .filter(([, prefixes]) => prefixes.some((p) => inc.has(p)))
          .map(([sector]) => sector),
      );
    }
  }
}
