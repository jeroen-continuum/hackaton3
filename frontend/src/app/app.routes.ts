import { Routes } from '@angular/router';

import { Dashboard } from './features/dashboard/dashboard';
import { CompanyDetailPage } from './features/company-detail/company-detail';
import { OutreachPage } from './features/outreach/outreach';

export const routes: Routes = [
  { path: '', component: Dashboard },
  { path: 'company/:id', component: CompanyDetailPage },
  { path: 'company/:id/outreach', component: OutreachPage },
  { path: '**', redirectTo: '' },
];
