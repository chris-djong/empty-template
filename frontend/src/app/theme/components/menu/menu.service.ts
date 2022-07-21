import { Injectable } from '@angular/core';

import { Menu } from './menu.model';
import { menuItems } from './menu';

@Injectable()
export class MenuService {

  constructor() { }

  public getMenuItems(): Array<Menu> {
    return menuItems;
  }


}