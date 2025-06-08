import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.scss'],
  standalone: true,
  imports: [CommonModule, RouterLink]
})
export class HomeComponent {
  constructor(private router: Router) {}

  goToAddTopic() {
    this.router.navigate(['/topics/new']);
  }
} 