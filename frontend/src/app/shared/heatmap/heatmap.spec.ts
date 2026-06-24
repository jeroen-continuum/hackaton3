import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Heatmap } from './heatmap';

describe('Heatmap', () => {
  let fixture: ComponentFixture<Heatmap>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Heatmap],
    }).compileComponents();
    fixture = TestBed.createComponent(Heatmap);
    fixture.componentRef.setInput('breakdown', {
      buyer_intent: 0.8,
      impact_potential: 0.6,
      financial_fit: 0.5,
      sector_fit: 1.0,
      warm_connection: 0.3,
    });
    fixture.detectChanges();
  });

  it('renders 5 rows', () => {
    const rows = fixture.nativeElement.querySelectorAll('.row');
    expect(rows.length).toBe(5);
  });

  it('100% bar for sector_fit=1.0', () => {
    const fills = fixture.nativeElement.querySelectorAll('.bar-fill');
    const widths = Array.from(fills).map((el: any) => el.style.width);
    expect(widths).toContain('100%');
  });
});
