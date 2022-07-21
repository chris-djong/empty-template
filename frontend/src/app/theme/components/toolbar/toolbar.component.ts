import { Component, OnInit, Output, EventEmitter } from '@angular/core';
import { AuthService } from 'src/app/services/auth.service';

@Component({
  selector: 'app-toolbar',
  templateUrl: './toolbar.component.html'
})
export class ToolbarComponent implements OnInit {
  @Output() onMenuIconClick: EventEmitter<any> = new EventEmitter<any>();

  constructor(
    public authService: AuthService) { }

  ngOnInit() {

  }

  public sidenavToggle() {
    this.onMenuIconClick.emit();
  }
}