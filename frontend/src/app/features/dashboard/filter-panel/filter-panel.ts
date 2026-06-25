import { Component, computed, input, linkedSignal, output } from '@angular/core';

import { FilterDefaults, FilterParams } from '../../../core/models';

@Component({
  selector: 'app-filter-panel',
  templateUrl: './filter-panel.html',
  styleUrl: './filter-panel.scss',
})
export class FilterPanel {
  /** Defaults from the backend; also defines the available sectors/regions. */
  defaults = input<FilterDefaults | null>(null);
  /** Emitted (with the assembled filters) when the user clicks Apply. */
  apply = output<FilterParams>();

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
      apply_size: this.applySize(),
      apply_financial: this.applyFinancial(),
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
      const inc = new Set(d.nace_include_prefixes);
      this.selectedSectors.set(
        Object.entries(this.sectorPrefixes())
          .filter(([, prefixes]) => prefixes.some((p) => inc.has(p)))
          .map(([sector]) => sector),
      );
    }
    this.emit();
  }
}
