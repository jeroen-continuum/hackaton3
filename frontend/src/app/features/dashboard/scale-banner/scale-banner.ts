import { Component, effect, input, signal } from '@angular/core';
import { DecimalPipe } from '@angular/common';

import { PondStats } from '../../../core/models';

/**
 * Scale + speed headline: an animated funnel from the full pond, to the
 * companies matching the current ICP, down to the 10 shortlisted — plus the
 * backend query time. Recomputes (and re-animates) whenever `stats` changes.
 */
@Component({
  selector: 'app-scale-banner',
  imports: [DecimalPipe],
  templateUrl: './scale-banner.html',
  styleUrl: './scale-banner.scss',
})
export class ScaleBanner {
  stats = input<PondStats | null>(null);

  /** Count-up display values, eased toward the real totals. */
  totalShown = signal(0);
  matchedShown = signal(0);

  constructor() {
    effect((onCleanup) => {
      const s = this.stats();
      if (!s) return;
      const stopTotal = countUp(this.totalShown(), s.total, (v) => this.totalShown.set(v));
      const stopMatched = countUp(this.matchedShown(), s.matched, (v) => this.matchedShown.set(v));
      onCleanup(() => {
        stopTotal();
        stopMatched();
      });
    });
  }
}

/** Animate `from → to` over ~700ms (ease-out), calling `set` each frame. Returns a canceller. */
function countUp(from: number, to: number, set: (v: number) => void): () => void {
  const DURATION = 700;
  const start = performance.now();
  let raf = 0;
  const tick = (now: number) => {
    const t = Math.min(1, (now - start) / DURATION);
    const eased = 1 - Math.pow(1 - t, 3);
    set(Math.round(from + (to - from) * eased));
    if (t < 1) raf = requestAnimationFrame(tick);
  };
  raf = requestAnimationFrame(tick);
  return () => cancelAnimationFrame(raf);
}
