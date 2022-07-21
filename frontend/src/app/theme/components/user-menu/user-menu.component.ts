import { Component, OnInit } from '@angular/core';
import { AuthService } from 'src/app/services/auth.service';

// This is used to show the user menu ones he presses the account button in the header
@Component({
  selector: 'app-user-menu',
  templateUrl: './user-menu.component.html',
  styleUrls: ['./user-menu.component.scss']
})
export class UserMenuComponent implements OnInit {

  constructor(
    public authService: AuthService,
  ) { }

  ngOnInit() {
  }

}
