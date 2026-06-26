import {
  Component, OnInit, AfterViewInit, ViewChild, ElementRef, OnDestroy,
} from '@angular/core';
import { Chart, registerables } from 'chart.js';
import { DashboardService } from '../../shared/services/dashboard.service';
import { DashboardResumen } from '../../core/models/dashboard.model';

Chart.register(...registerables);

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.scss'],
})
export class DashboardComponent implements OnInit, OnDestroy {
  @ViewChild('barCanvas') barCanvasRef!: ElementRef<HTMLCanvasElement>;

  resumen: DashboardResumen | null = null;
  loading = true;
  error   = false;
  private chart?: Chart;

  readonly STATION_COLORS: Record<string, string> = {
    sin_iniciar: '#90A4AE',
    Corte:       '#78909C',
    Troquel:     '#42A5F5',
    Ensamble:    '#FFA726',
    Empaque:     '#66BB6A',
  };

  constructor(private svc: DashboardService) {}

  ngOnInit(): void {
    this.svc.getResumen().subscribe({
      next: data => {
        this.resumen = data;
        this.loading = false;
        setTimeout(() => this.buildChart(), 0);
      },
      error: () => {
        this.error   = true;
        this.loading = false;
      },
    });
  }

  ngOnDestroy(): void {
    this.chart?.destroy();
  }

  private buildChart(): void {
    if (!this.resumen || !this.barCanvasRef) return;

    const labels = Object.keys(this.resumen.ventanas_por_estacion);
    const data   = Object.values(this.resumen.ventanas_por_estacion);
    const colors = labels.map(l => this.STATION_COLORS[l] ?? '#BDBDBD');

    this.chart = new Chart(this.barCanvasRef.nativeElement, {
      type: 'bar',
      data: {
        labels,
        datasets: [{
          label: 'Ventanas',
          data,
          backgroundColor: colors,
          borderRadius: 6,
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: ctx => ` ${ctx.parsed.y} ventana(s)`,
            },
          },
        },
        scales: {
          y: {
            beginAtZero: true,
            ticks: { stepSize: 1 },
          },
        },
      },
    });
  }

  get progressColor(): string {
    if (!this.resumen) return 'primary';
    const p = this.resumen.porcentaje_global;
    return p >= 100 ? 'primary' : p > 50 ? 'accent' : 'warn';
  }
}
