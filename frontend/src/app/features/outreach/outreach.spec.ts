import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { of, throwError } from 'rxjs';
import { OutreachPage } from './outreach';
import { ApiService } from '../../core/api';

const mockApi = {
  outreach: () => throwError(() => new Error('no asset')),
  generateOutreach: () => of({ status: 'generated', company_id: 1 }),
  getContacts: () => of({ contacts: [], persisted: false }),
  markContacted: () => of({}),
};

describe('OutreachPage', () => {
  let fixture: ComponentFixture<OutreachPage>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [OutreachPage],
      providers: [
        provideRouter([]),
        { provide: ApiService, useValue: mockApi },
      ],
    }).compileComponents();
    fixture = TestBed.createComponent(OutreachPage);
    fixture.componentRef.setInput('id', '1');
    fixture.detectChanges();
  });

  it('shows "Generate AI draft" button', () => {
    expect(fixture.nativeElement.textContent).toContain('Generate AI draft');
  });

  it('shows "No draft yet" when no asset', () => {
    expect(fixture.nativeElement.textContent).toContain('No draft yet');
  });
});
