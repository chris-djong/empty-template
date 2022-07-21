import { Injectable } from '@angular/core';
import { ConfirmDialogComponent, ConfirmDialogModel } from '../shared/confirm-dialog/confirm-dialog.component';
import { AlertDialogComponent } from '../shared/alert-dialog/alert-dialog.component';
import { MatDialog } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';


@Injectable({
  providedIn: 'root'
})
export class CommonService {

  constructor(
    public dialog: MatDialog,
    private snackBar: MatSnackBar,
  ) { }

  public openConfirmDialog(title: string, message: string) {
    const dialogData = new ConfirmDialogModel(title, message);
    const dialogRef = this.dialog.open(ConfirmDialogComponent, {
      maxWidth: "400px",
      data: dialogData,
      panelClass: ['theme-dialog']
    });
    return dialogRef;
  }

  public openAlertDialog(message: string) {
    const dialogRef = this.dialog.open(AlertDialogComponent, {
      maxWidth: "400px",
      data: message,
      panelClass: ['theme-dialog']
    });
    return dialogRef;
  }

  /**
   * Function used to translate a given text using the translate service and show it on a snackbar
   * @param data the data to be translated
   * @param error a boolean to decide whether it is an error 
   */
  public async showSnackbar(message: string, error: boolean = false) {
    // The only thing that changes between an error snackbar and normal is the panelClass to red
    if (error) {
      this.snackBar.open(message, '×', {
        verticalPosition: 'top',
        horizontalPosition: 'end',
        duration: 15000,
        panelClass: ["error-snackbar"]
      });
    } else {
      this.snackBar.open(message, '×', {
        verticalPosition: 'top',
        horizontalPosition: 'end',
        duration: 15000,
        panelClass: ["theme-snackbar"]
      });
    }

  }
}
