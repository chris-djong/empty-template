import { Component, Inject, PLATFORM_ID } from '@angular/core';
import { Router, NavigationEnd } from '@angular/router';
import { isPlatformBrowser } from '@angular/common';
import { AuthService } from './services/auth.service';
import { SpinnerService } from './services/spinner.service';
import { CommonService } from './services/common.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent {

  constructor(
    public router: Router,
    @Inject(PLATFORM_ID) private platformId: Object,
    private authService: AuthService) {

    // Set a timer to refresh the token 
    this.authService.setRefreshTimer();
  }

  ngAfterViewInit() {
    this.router.events.subscribe(event => {
      if (event instanceof NavigationEnd) {
        setTimeout(() => {
          if (isPlatformBrowser(this.platformId)) {
            window.scrollTo(0, 0);
          }
        });
      }
    });

    // Hide the cookie consent policy in case we have accepted the cookies already
    if (localStorage.getItem("cookies-accepted")) {
      this.hideCookieOverlay();
    }
  }

  // By accepting the cookies we simply set the cookie
  public acceptCookies() {
    localStorage.setItem("cookies-accepted", "true");
    this.hideCookieOverlay();
  }

  private hideCookieOverlay() {
    let cookiePopup = document.getElementById("cookie-popup");
    if (cookiePopup) {
      cookiePopup.classList.add("hide");
    }
    let cookieOverlay = document.getElementById("cookie-overlay");
    if (cookieOverlay) {
      cookieOverlay.classList.add("hide");
    }

  }

}
