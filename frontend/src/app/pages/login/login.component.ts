import { Component, OnDestroy, OnInit } from '@angular/core';
import { UntypedFormGroup, UntypedFormBuilder, Validators } from '@angular/forms';
import { MatSnackBar } from '@angular/material/snack-bar';
import { ActivatedRoute, Router } from '@angular/router';
import { AuthService } from 'src/app/services/auth.service';
import { CommonService } from 'src/app/services/common.service';
import { UserService } from 'src/app/services/user.service';


@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss']
})
export class LoginComponent implements OnInit, OnDestroy {

  public loginForm: UntypedFormGroup = this.fb.group({});
  public hide = true;
  private sub: any;
  private returnUrl: string = '';

  public resendVerification: string = '';

  private verificationToken: string = '';
  private userId: string = '';

  constructor(public fb: UntypedFormBuilder,
    public authService: AuthService,
    private activatedRoute: ActivatedRoute,
    public router: Router,
    private commonService: CommonService,
    private userService: UserService,
    private snackBar: MatSnackBar,) { }

  ngOnInit() {
    // get return url from route parameters or default to '/'
    this.returnUrl = this.activatedRoute.snapshot.queryParams['returnUrl'] || '/';

    this.loginForm = this.fb.group({
      email: [null, Validators.compose([Validators.required, Validators.minLength(3)])],
      password: [null, Validators.compose([Validators.required, Validators.minLength(7)])]
    });

    // See whether we have provided email verification parameters
    this.sub = this.activatedRoute.params.subscribe(params => {
      this.verificationToken = params?.verificationToken;
      this.userId = params?.userId;
    });

    // Whenever we detect a verification token and a user id in the URL then we perform the email verification steps
    if (this.verificationToken && this.userId) {
      this.verifyEmail();
    }

    // In case we are logged in already redirect the user
    if (this.authService.isLoggedIn()) {
      this.router.navigateByUrl(this.returnUrl);
    }
  }

  ngOnDestroy() {
    this.sub.unsubscribe();
  }


  private verifyEmail() {
    this.authService.verifyEmail(this.userId, this.verificationToken).subscribe(
      data => {
        this.processLoginResponse(data);
        this.router.navigateByUrl(this.returnUrl);
        this.commonService.showSnackbar("Email validated sucessfully. Welcome to <my_new_app>!");
      },
      err => {
        this.commonService.showSnackbar("Error validating email. Please contact our support in case the problem persists.", true);
      }
    )
  }


  public onLoginFormSubmit(values: Object): void {
    if (this.loginForm.valid) {
      this.authService.login(this.loginForm.value).subscribe(
        data => {
          this.processLoginResponse(data);
          this.router.navigateByUrl(this.returnUrl);
        },
        err => {
          console.log(err);
          // Filter errors and show the user 
          if (err.error.message?.non_field_errors == 'User with given email and password does not exist.') {
            this.commonService.showSnackbar('Invalid Username/Password combination. Please try again.', true);
          } else if (err.error.message?.non_field_errors == 'User not verified.') {
            this.resendVerification = this.loginForm.controls['email'].value;
            this.commonService.showSnackbar("Please verify your email first", true);
          } else {
            this.commonService.showSnackbar("Error logging in. Please try again and contact our support in case the problem persists. We apologies for any inconvenience.", true);
          }
        }
      );;
    }
  }

  // This function processes the login response for data obtained by either the login endpoint or the email verification endpoint
  // It sets the relevant variables in the authService and downloads user data such as favorites and compares
  private processLoginResponse(data: any) {
    this.authService.username = data['username'];
    this.authService.setSession(data['token'], data['refresh']);
  }

  public resendEmailVerificationLink() {
    if (this.loginForm.valid) {
      let email = this.loginForm.controls['email'].value;
      if (!email.includes('@')) {
        this.loginForm.controls['email'].setErrors({ 'no-username': true });
        // In case we have provided an email generate the api call
      } else {
        this.userService.resendEmailVerification(this.loginForm.value).subscribe({
          next: data => {
            this.commonService.showSnackbar("We have resend your verification email. Please check your spam and contact our support in case you are not able to retrieve the email.");
          },
          error: err => {
            this.commonService.showSnackbar("Something went wrong sending the verification email. Please try again and contact our support in case the problem persists. We apologies for any inconvenience.", true);
          }
        })
      }
    } else {
      if (!this.loginForm.controls['email'].value) {
        this.loginForm.controls['email'].setErrors({ 'email-required': true });
        this.loginForm.controls['email'].markAsTouched();
      }
      if (!this.loginForm.controls['password'].value) {
        this.loginForm.controls['password'].setErrors({ 'password-required': true });
        this.loginForm.controls['password'].markAsTouched();
      }
      this.commonService.showSnackbar("Please provide us with your username/email and password firstT", true);
    }
  }

  public forgotPassword() {
    // First check whether the email login form is valid 
    if (this.loginForm.controls['email'].valid) {
      // First check whether the user provided an email adress 
      let email = this.loginForm.controls['email'].value;
      if (!email.includes('@')) {
        this.loginForm.controls['email'].setErrors({ 'no-username': true });
        // In case we have provided an email generate the api call
      } else {
        this.userService.resetUserPassword(this.loginForm.controls['email'].value).subscribe({
          // And let the user know that the email has been send to the given email adres 
          next: data => {
            this.commonService.showSnackbar("A password reset email has been send. Please check your spam and contact our support in case your able not able to retrieve the email.");
          },
          // In case of an error show the error (this should not happen)
          error: err => {
            this.commonService.showSnackbar("Something went wrong resetting your password. Please try again and contact our support in case the problem persists. We apologies for any inconvenience.", true);
          }
        });
      }
      // In case we did not provide a valid email show the validation error
    } else {
      this.loginForm.controls['email'].setErrors({ 'email-required': true });
      this.loginForm.controls['email'].markAsTouched();
    }
  }

}
