import { Component, inject, input, signal, effect } from '@angular/core';
import { RouterLink } from '@angular/router';

import { ApiService } from '../../core/api';
import { Contact, OutreachAsset } from '../../core/models';

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
  contacts = signal<Contact[]>([]);
  unlocked = signal(false);
  generating = signal(false);
  loadingContacts = signal(false);
  sent = signal(false);

  constructor() {
    effect(() => {
      const cid = Number(this.id());
      this.api.outreach(cid).subscribe({
        next: (a) => this.asset.set(a),
        error: () => this.asset.set(null),
      });
    });
  }

  generate() {
    this.generating.set(true);
    this.api.generateOutreach(Number(this.id())).subscribe(() => {
      this.api.outreach(Number(this.id())).subscribe((a) => {
        this.asset.set(a);
        this.generating.set(false);
      });
    });
  }

  loadContacts() {
    this.loadingContacts.set(true);
    this.api.getContacts(Number(this.id())).subscribe((r) => {
      this.contacts.set(r.contacts);
      this.loadingContacts.set(false);
    });
  }

  markSent() {
    this.api.markContacted(Number(this.id())).subscribe(() => {
      this.sent.set(true);
    });
  }
}
