import { Component, OnDestroy, OnInit } from '@angular/core';
import { UntypedFormGroup, UntypedFormBuilder, Validators } from '@angular/forms';
import { MatSnackBar } from '@angular/material/snack-bar';
import { ActivatedRoute, Router } from '@angular/router';
import { CommonService } from 'src/app/services/common.service';
import { UserService } from 'src/app/services/user.service';
import { matchingPasswords } from 'src/app/theme/utils/app-validators';


@Component({
  selector: 'app-password-reset',
  templateUrl: './password-reset.component.html',
  styleUrls: ['./password-reset.component.scss']
})
export class PasswordResetComponent implements OnInit, OnDestroy {


  // Whether to hide the passwords or not 
  public hide: boolean = true;
  public hideConfirmation: boolean = true;

  // The form itself
  public passwordResetForm: UntypedFormGroup = this.fb.group({});

  // The inputs
  public resetToken: string = '';
  public userId: string = '';
  public tokenVerified: boolean = false; // whether the token has been verified

  private sub: any;


  constructor(public fb: UntypedFormBuilder,
    private activatedRoute: ActivatedRoute,
    public userService: UserService,
    private router: Router,
    private commonService: CommonService,
    private snackbar: MatSnackBar) { }

  ngOnInit(): void {

    // Get the route parameters
    this.sub = this.activatedRoute.params.subscribe(params => {
      this.resetToken = params?.resetToken;
      this.userId = params?.userId;

      this.verifyToken();
    });


    this.passwordResetForm = this.fb.group({
      email: [null, Validators.compose([Validators.required, Validators.minLength(3)])],
      password: [null, Validators.compose([Validators.required, Validators.minLength(6)])],
      passwordConfirmation: [null, Validators.compose([Validators.required, Validators.minLength(6)])]
    }, { validators: matchingPasswords("password", "passwordConfirmation") });
  }

  ngOnDestroy() {
    this.sub.unsubscribe();
  }


  /**
   * This function verifies the token user the corresponding endpoint 
   * And sets the tokenVerified parameter so that the user is able to reset his password
   */
  private verifyToken() {
    this.userService.checkResetToken(this.userId, this.resetToken).subscribe({
      next: (verification) => {
        this.tokenVerified = verification;
      },
      error: (err) => {
        this.commonService.showSnackbar('Could not validate your reset link. Please try the reset password process again or contact our support in case the problem persists. We apologies for any inconvenience', true);
      }
    });
  }


  submitForm(): void {
    if (this.passwordResetForm.valid) {
      this.userService.performPasswordReset(this.passwordResetForm.value, this.resetToken, this.userId).subscribe({
        next: (data) => {
          this.router.navigate(["/login"]);
          this.commonService.showSnackbar("Your password has been changed successfully");
        },
        error: (err) => {
          this.commonService.showSnackbar("Something went wrong resetting your password", true);
        }
      })
    }
  }

}
