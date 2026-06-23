import { Component, inject, input, signal, effect } from '@angular/core';
import { RouterLink } from '@angular/router';

import { ApiService } from '../../core/api';
import { OutreachAsset } from '../../core/models';

@Component({
  selector: 'app-outreach',
  imports: [RouterLink],
  templateUrl: './outreach.html',
  styleUrl: './outreach.scss',
})
export class OutreachPage {
  private api = inject(ApiService);
  id = input.required<string>();
  asset = signal<OutreachAsset | null>(null);
  unlocked = signal(false);

  constructor() {
    effect(() => {
      this.api.outreach(Number(this.id())).subscribe((a) => this.asset.set(a));
    });
  }
}
