import { Component, inject, signal } from '@angular/core';
import { RouterLink } from '@angular/router';

import { ApiService } from '../../core/api';
import { Employee } from '../../core/models';

@Component({
  selector: 'app-employees',
  imports: [RouterLink],
  templateUrl: './employees.html',
  styleUrl: './employees.scss',
})
export class EmployeesPage {
  private api = inject(ApiService);

  employees = signal<Employee[]>([]);
  name = signal('');
  title = signal('');
  email = signal('');

  constructor() {
    this.load();
  }

  private load() {
    this.api.listEmployees().subscribe((e) => this.employees.set(e));
  }

  add() {
    const name = this.name().trim();
    if (!name) return;
    this.api
      .createEmployee({ name, title: this.title() || undefined, email: this.email() || undefined })
      .subscribe(() => {
        this.name.set('');
        this.title.set('');
        this.email.set('');
        this.load();
      });
  }
}
