import { UntypedFormControl, AbstractControl, ValidationErrors } from '@angular/forms';

export function emailValidator(control: UntypedFormControl): { [key: string]: any } {
    var emailRegexp = /[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,3}$/;
    if (control.value && !emailRegexp.test(control.value)) {
        return { invalidEmail: true };
    } else {
        return { invalidEmail: false };
    }
}


export function matchingPasswords(password: string, confirmPassword: string) {
    return (control: AbstractControl): ValidationErrors | null => {
        const input = control.get(password);
        const matchingInput = control.get(confirmPassword);

        if (input === null || matchingInput === null) {
            return null;
        }

        if (matchingInput?.errors && !matchingInput.errors.confirmedValidator) {
            return null;
        }

        if (input.value !== matchingInput.value) {
            matchingInput.setErrors({ confirmedValidator: true });
            return ({ confirmedValidator: true });
        } else {
            matchingInput.setErrors(null);
            return null;
        }
    };
}