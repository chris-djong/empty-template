import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { NotFoundComponent } from './pages/not-found/not-found.component';
import { PagesComponent } from './pages/pages.component';


export const routes: Routes = [
  {
    path: '',
    component: PagesComponent, children: [
      //{ path: '', redirectTo: '/landing', pathMatch: 'full' },
      { path: '', loadChildren: () => import('./pages/home/home.module').then(m => m.HomeModule) },
      { path: 'login', loadChildren: () => import('./pages/login/login.module').then(m => m.LoginModule) },
      { path: 'register', loadChildren: () => import('./pages/register/register.module').then(m => m.RegisterModule) },
      { path: 'password-reset', loadChildren: () => import('./pages/password-reset/password-reset.module').then(m => m.PasswordResetModule) },
    ]
  },
  // Lock screen is not deemed useful{ path: 'lock-screen', component: LockScreenComponent },
  { path: '**', component: NotFoundComponent }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
