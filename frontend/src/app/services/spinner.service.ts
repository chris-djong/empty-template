import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class SpinnerService {

  private showSpinner: number = 0;  // 0 means dont show the spinner and otherwise yes. This ensure that if multiple endpoint activate the spinner we have to wait until the last on to actually deactivate it 
  private showProgress: boolean = false;

  constructor(
  ) { }

  public enableSpinner() {
    // Remove the class in case we were previously in a hide state 
    if (!this.showSpinner) {
      document.getElementById('spinner')?.classList.remove('hide');
    }
    // And increase the counter either way 
    this.showSpinner += 1;
  }

  public disableSpinner() {
    if (this.showSpinner > 0) {
      this.showSpinner -= 1;
    }
    // Remove the class whenever we reach 0 
    if (this.showSpinner <= 0) {
      document.getElementById('spinner')?.classList.add('hide');
      if (this.showProgress) {
        this.showProgress = false;
        document.getElementById("spinner-progress")?.classList.add("hide");
      }
    }
  }

  // Sets the progress of the progress bar in percentage 
  // Also allows setting of text to the spinner 
  public setProgress(value: number, text: string = '') {
    // Show the progress bar in case it is not shown
    if (!this.showProgress) {
      this.showProgress = true;
      document.getElementById("spinner-progress")?.classList.remove("hide");
    }

    // And set the amount 
    if (this.showProgress) {
      // Set the width of the bar 
      if (value > 100) {
        value = 100;
      } else if (value < 0) {
        value = 0;
      }
      let width = value + '%'
      let innerProgress = document.getElementById("spinner-progress-inner");
      if (innerProgress) {
        innerProgress.style.width = width;
      }

      // And add the text 
      let textField = document.getElementById('spinner-progress-text');
      if (textField) {
        textField.innerHTML = text
      }
    }
  }



}