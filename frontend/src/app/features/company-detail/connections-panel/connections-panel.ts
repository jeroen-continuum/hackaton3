import { Component, effect, inject, input, output, signal } from '@angular/core';
import { LowerCasePipe } from '@angular/common';

import { ApiService } from '../../../core/api';
import { CompanyConnections, ConnectionType, Employee } from '../../../core/models';

@Component({
  selector: 'app-connections-panel',
  imports: [LowerCasePipe],
  templateUrl: './connections-panel.html',
  styleUrl: './connections-panel.scss',
})
export class ConnectionsPanel {
  private api = inject(ApiService);

  companyId = input.required<number>();
  /** Emitted after a tie is added/removed so the parent can reload the score. */
  changed = output<void>();

  data = signal<CompanyConnections | null>(null);
  employees = signal<Employee[]>([]);
  showForm = signal(false);

  // Form fields (signals, matching the filter-panel pattern — no FormsModule).
  empId = signal<number | null>(null);
  type = signal<ConnectionType>('EMPLOYER');
  startDate = signal<string>('');
  endDate = signal<string>('');
  note = signal<string>('');

  readonly types: ConnectionType[] = ['EMPLOYER', 'CLIENT', 'PERSONAL'];

  constructor() {
    effect(() => {
      this.load(this.companyId());
    });
    this.api.listEmployees().subscribe((e) => this.employees.set(e));
  }

  private load(id: number) {
    this.api.companyConnections(id).subscribe((d) => this.data.set(d));
  }

  typeLabel(t: ConnectionType): string {
    return { EMPLOYER: 'ex-employer', CLIENT: 'ex-client', PERSONAL: 'knows someone' }[t];
  }

  save() {
    const empId = this.empId();
    if (empId == null) return;
    this.api
      .createConnection({
        employee_id: empId,
        company_id: this.companyId(),
        type: this.type(),
        start_date: this.startDate() || null,
        end_date: this.endDate() || null,
        note: this.note() || null,
      })
      .subscribe(() => {
        this.showForm.set(false);
        this.empId.set(null);
        this.startDate.set('');
        this.endDate.set('');
        this.note.set('');
        this.load(this.companyId());
        this.changed.emit();
      });
  }

  remove(id: number) {
    this.api.deleteConnection(id).subscribe(() => {
      this.load(this.companyId());
      this.changed.emit();
    });
  }
}
