import { NgModule } from '@angular/core';
import { MatToolbarModule }        from '@angular/material/toolbar';
import { MatButtonModule }         from '@angular/material/button';
import { MatIconModule }           from '@angular/material/icon';
import { MatCardModule }           from '@angular/material/card';
import { MatTableModule }          from '@angular/material/table';
import { MatSortModule }           from '@angular/material/sort';
import { MatPaginatorModule }      from '@angular/material/paginator';
import { MatProgressBarModule }    from '@angular/material/progress-bar';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatChipsModule }          from '@angular/material/chips';
import { MatFormFieldModule }      from '@angular/material/form-field';
import { MatInputModule }          from '@angular/material/input';
import { MatSelectModule }         from '@angular/material/select';
import { MatDialogModule }         from '@angular/material/dialog';
import { MatSnackBarModule }       from '@angular/material/snack-bar';
import { MatStepperModule }        from '@angular/material/stepper';
import { MatDividerModule }        from '@angular/material/divider';
import { MatListModule }           from '@angular/material/list';
import { MatMenuModule }           from '@angular/material/menu';
import { MatTooltipModule }        from '@angular/material/tooltip';
import { MatTabsModule }           from '@angular/material/tabs';
import { MatBadgeModule }          from '@angular/material/badge';
import { MatExpansionModule }      from '@angular/material/expansion';

const MATERIAL = [
  MatToolbarModule, MatButtonModule, MatIconModule, MatCardModule,
  MatTableModule, MatSortModule, MatPaginatorModule,
  MatProgressBarModule, MatProgressSpinnerModule, MatChipsModule,
  MatFormFieldModule, MatInputModule, MatSelectModule,
  MatDialogModule, MatSnackBarModule, MatStepperModule,
  MatDividerModule, MatListModule, MatMenuModule,
  MatTooltipModule, MatTabsModule, MatBadgeModule, MatExpansionModule,
];

@NgModule({ imports: MATERIAL, exports: MATERIAL })
export class AppMaterialModule {}
