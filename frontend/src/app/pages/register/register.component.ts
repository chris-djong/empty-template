import { Component, OnInit } from '@angular/core';
import { UntypedFormGroup, UntypedFormBuilder, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { matchingPasswords, emailValidator } from 'src/app/theme/utils/app-validators';
import { AuthService } from 'src/app/services/auth.service';
import { MatSnackBar } from '@angular/material/snack-bar';
import { SpinnerService } from 'src/app/services/spinner.service';
import { CommonService } from 'src/app/services/common.service';


@Component({
  selector: 'app-register',
  templateUrl: './register.component.html',
  styleUrls: ['./register.component.scss']
})
export class RegisterComponent implements OnInit {
  public registerForm: UntypedFormGroup = this.fb.group({});
  public hide = true;


  constructor(
    public authService: AuthService,
    public fb: UntypedFormBuilder,
    public router: Router,
    private commonService: CommonService,
    private snackBar: MatSnackBar,
    private spinnerService: SpinnerService) { }

  ngOnInit() {
    this.registerForm = this.fb.group({
      username: ['', Validators.compose([Validators.required, Validators.minLength(3)])],
      email: ['', Validators.compose([Validators.required, emailValidator])],
      password: ['', Validators.compose([Validators.required,
      Validators.minLength(7),
      Validators.pattern('^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9]).+$') //this is for the letters (both uppercase and lowercase) and numbers validation
      ])],
      confirmPassword: ['', Validators.required],
      sub_newsletter: false
    }, { validator: matchingPasswords('password', 'confirmPassword') });
  }

  public onRegisterFormSubmit(values: Object): void {
    if (this.registerForm.controls['username'].value.includes('admin')) {
      this.commonService.showSnackbar("Come work for us and you can become an admin.");
    } else {
      if (this.registerForm.valid) {
        this.spinnerService.enableSpinner();
        this.authService.register(this.registerForm.value).subscribe({
          next: data => {
            this.router.navigate(['/login']);
            this.spinnerService.disableSpinner();
            this.commonService.showSnackbar("You registered successfully! You just have to verify your email using the verification link that we have send you.");
          },
          error: err => {
            console.log(err);
            this.spinnerService.disableSpinner();
            let foundError: boolean = false;  // to check whether it is an error that is shown to the user 
            if (err.error?.message?.username?.includes('user with this username already exists.')) {
              this.registerForm.controls['username'].setErrors({ 'exists': true });
              foundError = true;
            }
            if (err.error?.message?.email?.includes('user with this email already exists.')) {
              this.registerForm.controls['email'].setErrors({ 'exists': true });
              foundError = true
            }
            if (!foundError) {
              this.commonService.showSnackbar("Something went wrong registering your account. Please try again or contact our support in case the problem persists. We apologies for any inconvenience.", true);
            }
          }
        });
      }
    }
  }
}
