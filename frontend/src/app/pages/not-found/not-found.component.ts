import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { SpinnerService } from 'src/app/services/spinner.service';

@Component({
  selector: 'app-not-found',
  templateUrl: './not-found.component.html',
  styleUrls: ['./not-found.component.scss']
})
export class NotFoundComponent implements OnInit {

  constructor(public router: Router,
    private spinnerService: SpinnerService) { }

  ngOnInit() {
  }

  public goHome(): void {
    this.router.navigate(['/']);
  }

  ngAfterViewInit() {
    this.spinnerService.disableSpinner()
  }

}
