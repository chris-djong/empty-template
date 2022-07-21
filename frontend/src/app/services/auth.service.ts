import { Inject, Injectable, PLATFORM_ID } from "@angular/core";
import { HttpClient, HttpHeaders, HttpInterceptor, HttpHandler, HttpRequest, HttpEvent, HttpErrorResponse, } from "@angular/common/http";
import { MatDialog } from "@angular/material/dialog";
import { ActivatedRouteSnapshot, CanActivate, Router, RouterStateSnapshot } from "@angular/router";
import { MatSnackBar } from "@angular/material/snack-bar";
import { Observable, throwError, BehaviorSubject } from "rxjs";
import { catchError, shareReplay, switchMap, filter, take, finalize } from "rxjs/operators";

import jwtDecode from "jwt-decode";
import * as moment from "moment";
import { DataService } from "./data.service";
import { UserService } from "./user.service";

@Injectable({
  providedIn: "root",
})
export class AuthService {
  constructor(
    private dataService: DataService,
    private snackBar: MatSnackBar,
    public http: HttpClient,
    private userService: UserService,
    public dialog: MatDialog,
    public router: Router,
  ) { }

  private httpOptions = {
    headers: new HttpHeaders({ "Content-Type": "application/json" }),
  };

  // User login data
  public username: string = '';
  public userId: string = '';
  private refreshTimerSet: boolean = false;

  // Send the username and password via https to the server in order to obtain a token
  public login(user: any) {
    return this.http
      .post(
        this.dataService.backendUrl + "/login",
        JSON.stringify(user),
        this.httpOptions
      )
      .pipe(shareReplay());
  }

  public verifyEmail(userId: string, verificationToken: string) {
    return this.http.post(
      this.dataService.backendUrl + "/email-verification",
      { userId: userId, verificationToken: verificationToken },
      this.httpOptions
    );
  }

  // Sets the user session by storing expiration date and token in the local browser storage
  public setSession(token: string, refresh: string) {
    const payload = <JWTPayload>jwtDecode(token);
    const expiresAt = moment.unix(payload.exp);

    // This is required for the case that the refresh token call is used
    // Whenever the response comes we set the local storage as well
    // However, in case we were not previously logged in the session will have a undefined in the localstorage and hence we have to restore it first
    if (this.username == null) {
      this.loadLocalStorage();
    }

    localStorage.setItem("token", token);
    localStorage.setItem("refresh", refresh);
    localStorage.setItem("expires_at", JSON.stringify(expiresAt.valueOf()));
    localStorage.setItem("username", this.username);

    // Whenever we set the session we also download the user data
    this.getUserData();

    // Refresh the token whenever it expires
    this.setRefreshTimer();
  }

  public setRefreshTimer() {
    // In case no refresh timer is set then set one
    if (!this.refreshTimerSet && localStorage.getItem("refresh")) {
      // So that only one timer is set
      this.refreshTimerSet = true;

      // Get the expiration date
      const expiration = localStorage.getItem("expires_at");
      const expiresAt = JSON.parse('' + expiration);
      const expiry = moment(expiresAt);

      // Set the refresh timer 10 seconds before expiry
      let refreshTimer = expiry.diff(moment(), "milliseconds") - 10000;

      // And finally create a timeout that refreshed the token
      setTimeout(() => {
        this.refreshToken().subscribe((data: any) => {
          this.setSession(data["access"], data["refresh"]);
        });
        this.refreshTimerSet = false;
      }, refreshTimer);
    }
  }

  // Get the expiration date of the current token
  private getExpiration() {
    const expiration = localStorage.getItem("expires_at");
    const expiresAt = JSON.parse(expiration + '');
    return moment(expiresAt);
  }

  // Loads the user information from the current local storage
  private loadLocalStorage() {
    this.userId = localStorage.getItem("agentId") + '';
    this.username = localStorage.getItem("username") + '';
  }

  // Loggin status
  isLoggedIn() {
    let result = moment().isBefore(this.getExpiration());
    // Whenever we check the login we also update the username and userPicture from local storage in case not there
    // ToCheck: This is needed in case the user enters the website a second time and the login status is retrieved from localStorage and not login
    if (result && this.username == null) {
      this.loadLocalStorage();
      // Otherwise try to refresh the token in case it is still possible
    }
    return result;
  }

  // Logout status
  isLoggedOut() {
    return !this.isLoggedIn();
  }

  // Refresh the token using the first token to extend its availbility / find out how this should be implemented. Probably in case the this.tokenExpires is about to expire
  refreshToken() {
    const refresh = localStorage.getItem("refresh");
    return this.http.post(this.dataService.backendUrl + "/token/refresh", {
      refresh: refresh,
    });
  }

  // Registration endpoint
  public register(user: any) {
    return this.http.post(
      this.dataService.backendUrl + "/register",
      JSON.stringify(user),
      this.httpOptions
    );
  }

  // Changes the password
  // Data = {'old': old password, 'new': new password}
  public changePassword(data: any) {
    let httpOptions = {
      headers: new HttpHeaders({
        "Content-Type": "application/json",
      }),
    };
    return this.http.put<any[]>(
      this.dataService.backendUrl + "/user-profile/change-password",
      data,
      httpOptions
    );
  }

  // Retrieves relevant user data from our api
  private getUserData() {
    this.userService.getUserProfile().subscribe({
      next: (data) => {
        this.username = data['username'];
      },
    });
  }

  // Reset tokens in case we log out, so that the user can not authenticate himself anymore
  public logout() {
    // this.token = null;
    // this.tokenExpires = null;
    localStorage.clear();
    this.router.navigate(["/login"]);
  }
}

// Class that intercepts each http request and adds the JWT header based on the locally stored JWT token
@Injectable()
export class JWTInterceptor implements HttpInterceptor {
  // Create a subject for the refreshing
  // 'A subject is like an Observable, but can multicast to many Observer'
  private tokenSubject: BehaviorSubject<string> = new BehaviorSubject<string>('');
  private refreshInProgress: boolean = false;

  constructor(
    private authService: AuthService,
    private dataService: DataService
  ) { }

  // Function that injects the token into the request
  injectToken(req: HttpRequest<any>) {
    const token = localStorage.getItem("token");
    // It might be that the user kept the expires at localstorage but removed the token itself
    if (token) {
      // Clone the request with the given header and return it
      const cloned = req.clone({
        headers: req.headers.set("Authorization", "Bearer ".concat(token)),
      });
      return cloned;
    } else {
      return req;
    }
  }

  // Functions that check whether an error is of type token expiry
  errorIsTokenExpiry(error: HttpErrorResponse): boolean {
    if (error.status == 401 && error.error.code == "token_not_valid") {
      return true;
    } else {
      return false;
    }
  }

  // https://stackoverflow.com/questions/54327548/trying-to-repeat-a-http-request-after-refresh-token-with-a-interceptor-in-angula
  // This function handles all unauthorized errors
  // Whenever an error is encountered, the interface tries to refresh the token
  // ToDo: find out what happens when the refresh token expires
  handleUnauthorized(
    req: HttpRequest<any>,
    next: HttpHandler
  ): Observable<any> {
    // In case we are not refreshing the token yet start the refresh process
    if (!this.refreshInProgress) {
      // Make sure that no other tokens are requested
      this.refreshInProgress = true;

      // Reset here so that the following requests wait until the token comes back from the refreshToken call.
      this.tokenSubject.next('');

      // Get a new token from the API endpoint
      return this.authService.refreshToken().pipe(
        // Loop through the token and set the session
        switchMap((result: any) => {
          let token = result["access"];
          let refresh = result["refresh"];
          this.authService.setSession(token, refresh);

          // If we got a new token redo the request and show the tokensubject that a new request is available
          // Move the subject to the next position providing the new token
          this.tokenSubject.next(token);
          return next.handle(this.injectToken(req));
        }),
        // In case of errors log out
        catchError((error) => {
          // In case there was an error refreshing the token then logout the user and throw an error
          this.authService.logout();
          return throwError(error);
        }),
        // At the finalisation of the refresh token we reset the refreshInProgress variable
        finalize(() => {
          this.refreshInProgress = false;
        })
      );
      // Otherwise in case the refresh process is being executed return the token subject
    } else {
      return this.tokenSubject.pipe(
        // We filter all the subjects that do not have a token set to null (as the null value is set above whenever a refresh has been started)
        filter((token) => token != null),
        // Take only 1 of the calls
        take(1),
        // And try to execute it using the current token - whenever we get an unauthorized error the whole process repeats
        switchMap(() => {
          return next.handle(this.injectToken(req));
        })
      );
    }
  }

  // The actual intercept. Here the logic that is executed for each http request resides
  intercept(
    req: HttpRequest<any>,
    next: HttpHandler
  ): Observable<HttpEvent<any>> {
    // Only perform the token verification steps in case we have a call to the backend which is not a refresh call (the refresh call condition is needed to avoid an infinite loop in case of refresh)
    if (
      req.url.startsWith(this.dataService.backendUrl) &&
      !(req.url == this.dataService.backendUrl + "/token/refresh")
    ) {
      // Then create a pipe that tries to execute the query and catches the error in case it detects one
      return next.handle(this.injectToken(req)).pipe(
        catchError((error, caught) => {
          // The only errors that we currently want to catch are of http errors that are token expired
          // All remaining errors are just thrown
          if (error instanceof HttpErrorResponse) {
            if (
              this.errorIsTokenExpiry(error) &&
              localStorage.getItem("refresh")
            ) {
              return this.handleUnauthorized(req, next);
            } else {
              return throwError(error);
            }
            // In case we dont have an HTTP error throw an observable error
          } else {
            return throwError(error);
          }
        })
      );
    } else {
      return next.handle(req);
    }
  }
}

// This class works as a shield and stop unauthenticated access to the routes that required authentication.
// If a not logged in user tries to access the guarded route he is redirected to the login page and all the cookies are deleted
@Injectable()
export class AuthGuard implements CanActivate {
  constructor(private authService: AuthService, private router: Router) { }

  canActivate(route: ActivatedRouteSnapshot, state: RouterStateSnapshot) {
    if (this.authService.isLoggedIn()) {
      return true;
    } else {
      this.authService.logout();
      this.router.navigate(["login"], {
        queryParams: { returnUrl: state.url },
      });
      return false;
    }
  }
}

// Interface to store the jwt payload
interface JWTPayload {
  user_id: number;
  username: string;
  email: string;
  exp: number;
}
