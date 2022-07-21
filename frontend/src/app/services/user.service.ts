import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { DataService } from './data.service';
import { User } from 'src/app/models/users.models';

@Injectable({
  providedIn: 'root'
})
export class UserService {

  constructor(
    public dataService: DataService,
    public http: HttpClient
  ) { }

  private httpOptions = {
    headers: new HttpHeaders({ 'Content-Type': 'application/json' })
  };

  // Gets the user profile of the currently logged in user 
  public getUserProfile(): Observable<User> {
    return this.http.get<User>(this.dataService.backendUrl + '/user-profile', this.httpOptions);
  }

  // Updates the user profile using the currently logged in user 
  public updateUserProfile(data: any): Observable<any[]> {
    return this.http.put<any[]>(this.dataService.backendUrl + '/user-profile', data);
  }


  /**
   * Resend the email verification email to the given email adres
   * data should contain the results of the login form, so email and password
   */
  public resendEmailVerification(data: any): Observable<any[]> {
    return this.http.post<any[]>(this.dataService.backendUrl + '/register/resend-verification', data, this.httpOptions);
  }

  /**
   * Reset password for the given email
   * only email is valid. This endpoint will result in the user obtaining a token via email to change his password
   */
  public resetUserPassword(email: string): Observable<any[]> {
    return this.http.put<any[]>(this.dataService.backendUrl + '/user-profile/send-forgot-password', { email: email }, this.httpOptions);
  }

  /**
   * Function that checks whether a reset token is valid
   * In case it is not valid anymore the user is redirected to the login page with a corresponding error
   * @param user_id : the uuid of the corresponding user 
   * @param token: the reset token of the user 
   * returns a boolean to check whether the token is valid or not 
   */
  public checkResetToken(user_id: string, token: string): Observable<boolean> {
    return this.http.get<boolean>(`${this.dataService.backendUrl}/user-profile/forgot-password/${user_id}/${token}`, this.httpOptions);
  }

  /**
   * Post request that is used to change the user password
   * @param data the value of the password reset form 
   * @param token the reset token itself
   * @param userId the user id that has been provided
   */
  public performPasswordReset(data: any, token: string, userId: string): Observable<any> {
    return this.http.post<boolean>(`${this.dataService.backendUrl}/user-profile/forgot-password/d8fde17f-614d-4619-afa1-88ffd405473f/a4a1298f-88fa-4732-b6cf-114da5bcb82b`, { formData: data, token: token, userId: userId }, this.httpOptions);
  }

  // Retrieve the necessary user data by user id, mainly needed so that we obtain the agent and client id from a given user id 
  public getUserById(id: string): Observable<User> {
    return this.http.get<User>(this.dataService.backendUrl + '/user-information/' + id, this.httpOptions);
  }

}
