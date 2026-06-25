import {
  AfterViewInit,
  Component,
  ElementRef,
  OnDestroy,
  effect,
  input,
  output,
  signal,
  viewChild,
} from '@angular/core';
import * as L from 'leaflet';

import { Area, CompanyListItem, DensityPoint } from '../../../core/models';

/**
 * Interactive area picker + result map.
 *
 * Renders the Rolling 10 as vector pins, a draggable center marker, and a
 * radius circle. Moving the center or the radius slider emits an `Area`
 * (or `null` when the radius is 0 = area filter off) for the dashboard to
 * re-rank against.
 */
@Component({
  selector: 'app-prospect-map',
  templateUrl: './prospect-map.html',
  styleUrl: './prospect-map.scss',
})
export class ProspectMap implements AfterViewInit, OnDestroy {
  /** Companies to plot (the current Rolling 10). */
  companies = input<CompanyListItem[]>([]);
  /** Every geocoded company location + count, for the country-wide density layer. */
  density = input<DensityPoint[]>([]);
  /** Initial map center (Belgium centroid from the backend defaults). */
  defaultCenter = input<{ lat: number; lon: number }>({ lat: 50.8503, lon: 4.3517 });
  /** Emitted when the chosen area changes (null = area filter off). */
  areaChange = output<Area | null>();

  private mapEl = viewChild.required<ElementRef<HTMLDivElement>>('map');

  /** Radius in km; 0 means the area filter is disabled. */
  radiusKm = signal(0);
  /** Whether the country-wide density layer is shown. */
  showDensity = signal(true);

  private map?: L.Map;
  private center!: L.LatLng;
  private centerMarker?: L.Marker;
  private circle?: L.Circle;
  // Density added first so the Rolling-10 pins always render on top.
  private dots = L.layerGroup();
  private pins = L.layerGroup();

  constructor() {
    // Redraw company pins whenever the input list changes.
    effect(() => {
      const items = this.companies();
      if (this.map) this.renderPins(items);
    });
    // Redraw the density layer when its data or the toggle changes.
    effect(() => {
      const points = this.density();
      const show = this.showDensity();
      if (this.map) this.renderDensity(show ? points : []);
    });
  }

  ngAfterViewInit() {
    const c = this.defaultCenter();
    this.center = L.latLng(c.lat, c.lon);

    this.map = L.map(this.mapEl().nativeElement, { center: this.center, zoom: 8 });
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: '© OpenStreetMap contributors',
    }).addTo(this.map);

    // Draggable center marker (divIcon avoids Leaflet's missing-image asset issue).
    this.centerMarker = L.marker(this.center, {
      draggable: true,
      icon: L.divIcon({ className: 'center-pin', iconSize: [18, 18], iconAnchor: [9, 9] }),
    }).addTo(this.map);
    this.centerMarker.on('drag', (e) => this.onCenterMoved((e.target as L.Marker).getLatLng()));
    this.centerMarker.on('dragend', () => this.emitArea());
    this.map.on('click', (e: L.LeafletMouseEvent) => {
      this.centerMarker!.setLatLng(e.latlng);
      this.onCenterMoved(e.latlng);
      this.emitArea();
    });

    this.dots.addTo(this.map);
    this.pins.addTo(this.map);
    this.renderDensity(this.showDensity() ? this.density() : []);
    this.renderPins(this.companies());
  }

  ngOnDestroy() {
    this.map?.remove();
  }

  /** Slider handler: 0 hides the circle and turns the filter off. */
  setRadius(km: number) {
    this.radiusKm.set(km);
    this.updateCircle();
    this.emitArea();
  }

  /** Toggle the country-wide density layer. */
  setShowDensity(show: boolean) {
    this.showDensity.set(show);
  }

  private onCenterMoved(latlng: L.LatLng) {
    this.center = latlng;
    this.updateCircle();
  }

  private updateCircle() {
    const km = this.radiusKm();
    if (!this.map) return;
    if (km <= 0) {
      this.circle?.remove();
      this.circle = undefined;
      return;
    }
    if (!this.circle) {
      this.circle = L.circle(this.center, {
        radius: km * 1000,
        color: '#2563eb',
        fillColor: '#3b82f6',
        fillOpacity: 0.1,
      }).addTo(this.map);
    } else {
      this.circle.setLatLng(this.center).setRadius(km * 1000);
    }
  }

  private emitArea() {
    const km = this.radiusKm();
    this.areaChange.emit(
      km > 0
        ? { center_lat: this.center.lat, center_lon: this.center.lng, radius_km: km }
        : null,
    );
  }

  /** Plot every geocoded location as a translucent dot sized + colored by count. */
  private renderDensity(points: DensityPoint[]) {
    this.dots.clearLayers();
    for (const p of points) {
      const r = 2 + Math.log(p.count + 1) * 1.6; // log scale: 1 → tiny, thousands → big
      L.circleMarker([p.lat, p.lon], {
        radius: r,
        stroke: false,
        fillColor: heatColor(p.count),
        fillOpacity: 0.45,
      }).addTo(this.dots);
    }
  }

  private renderPins(items: CompanyListItem[]) {
    this.pins.clearLayers();
    for (const c of items) {
      if (c.latitude == null || c.longitude == null) continue;
      L.circleMarker([c.latitude, c.longitude], {
        radius: 7,
        color: '#1d4ed8',
        fillColor: '#60a5fa',
        fillOpacity: 0.9,
        weight: 2,
      })
        .bindPopup(
          `<strong>#${c.rank} ${c.name}</strong><br>` +
            `${c.sector ?? ''} · ${c.municipality ?? c.region}<br>` +
            `score ${Math.round(c.score * 100)}`,
        )
        .addTo(this.pins);
    }
  }
}

/** Blue (sparse) → amber → red (dense) ramp by company count. */
function heatColor(count: number): string {
  if (count >= 500) return '#dc2626';
  if (count >= 100) return '#f59e0b';
  if (count >= 20) return '#3b82f6';
  return '#60a5fa';
}
