import { Component, input } from '@angular/core';
import { DecimalPipe } from '@angular/common';
import { ScoreBreakdown } from '../../core/models';

const LABELS: Record<keyof ScoreBreakdown, string> = {
  buyer_intent: 'Buyer intent',
  impact_potential: 'Impact potential',
  financial_fit: 'Financial fit',
  sector_fit: 'Sector fit',
  warm_connection: 'Warm connection',
};

@Component({
  selector: 'app-heatmap',
  imports: [DecimalPipe],
  templateUrl: './heatmap.html',
  styleUrl: './heatmap.scss',
})
export class Heatmap {
  breakdown = input.required<ScoreBreakdown>();

  get rows() {
    const b = this.breakdown();
    return (Object.keys(LABELS) as (keyof ScoreBreakdown)[]).map((key) => ({
      label: LABELS[key],
      value: b[key] ?? 0,
    }));
  }

  /** green (high) -> red (low) heat colour. */
  color(value: number): string {
    const hue = Math.round(value * 120); // 0=red, 120=green
    return `hsl(${hue} 70% 45%)`;
  }
}
