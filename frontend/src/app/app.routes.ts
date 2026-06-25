import { Routes } from '@angular/router';

import { Dashboard } from './features/dashboard/dashboard';
import { CompanyDetailPage } from './features/company-detail/company-detail';
import { OutreachPage } from './features/outreach/outreach';
import { EmployeesPage } from './features/employees/employees';

export const routes: Routes = [
  { path: '', component: Dashboard },
  { path: 'employees', component: EmployeesPage },
  { path: 'company/:id', component: CompanyDetailPage },
  { path: 'company/:id/outreach', component: OutreachPage },
  { path: '**', redirectTo: '' },
];
