import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { PagesComponent } from './pages/pages.component';
import { NotFoundComponent } from './pages/not-found/not-found.component';
import { FormsModule } from '@angular/forms';
import { HttpClientModule, HTTP_INTERCEPTORS } from '@angular/common/http';
import { SharedModule } from './shared/shared.module';
import { AuthGuard, AuthService, JWTInterceptor } from './services/auth.service';
import { ToolbarComponent } from './theme/components/toolbar/toolbar.component';
import { UserMenuComponent } from './theme/components/user-menu/user-menu.component';
import { HorizontalMenuComponent } from './theme/components/menu/horizontal-menu/horizontal-menu.component';
import { SocialIconsComponent } from './theme/components/social-icons/social-icons.component';
import { VerticalMenuComponent } from './theme/components/menu/vertical-menu/vertical-menu.component';

@NgModule({
  declarations: [
    AppComponent,
    PagesComponent,
    NotFoundComponent,
    ToolbarComponent,
    UserMenuComponent,
    HorizontalMenuComponent,
    VerticalMenuComponent,
    SocialIconsComponent
  ],
  imports: [
    BrowserModule.withServerTransition({ appId: 'serverApp' }),
    BrowserAnimationsModule,
    AppRoutingModule,
    BrowserAnimationsModule,
    FormsModule,
    HttpClientModule,
    AppRoutingModule,
    SharedModule,
  ],
  providers: [
    AuthService,
    AuthGuard,
    { provide: HTTP_INTERCEPTORS, useClass: JWTInterceptor, multi: true }, // intercepts messages and add the JWT token if available
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
