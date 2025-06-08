import { Component } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-create-topic',
  templateUrl: './create-topic.component.html',
  styleUrls: ['./create-topic.component.scss'],
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule]
})
export class CreateTopicComponent {
  topicForm: FormGroup;
  loading = false;
  success = false;
  error: string | null = null;

  constructor(
    private fb: FormBuilder,
    private http: HttpClient,
    private router: Router
  ) {
    this.topicForm = this.fb.group({
      title: ['', Validators.required],
      description: ['', Validators.required],
      mediaType: [''],
      mediaUrl: [''],
      mediaAlt: ['']
    });
  }

  submit() {
    if (this.topicForm.invalid) return;
    this.loading = true;
    this.error = null;
    this.success = false;

    const { title, description, mediaType, mediaUrl, mediaAlt } = this.topicForm.value;
    const body: any = { title, description };
    if (mediaType && mediaUrl) {
      body.media = { type: mediaType, url: mediaUrl };
      if (mediaAlt) body.media.alt_text = mediaAlt;
    }

    this.http.post('/api/topics', body).subscribe({
      next: () => {
        this.success = true;
        this.loading = false;
        this.topicForm.reset();
        setTimeout(() => this.router.navigate(['/']), 1000);
      },
      error: err => {
        this.error = err.error?.detail || 'Failed to create topic.';
        this.loading = false;
      }
    });
  }
} 