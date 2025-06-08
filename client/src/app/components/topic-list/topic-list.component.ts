import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { CommonModule, DatePipe } from '@angular/common';

interface Topic {
  topic_id: number;
  title: string;
  description: string;
  media?: { type: string; url: string; alt_text?: string };
  tips: any[];
  created_at: string;
  updated_at: string;
}

@Component({
  selector: 'app-topic-list',
  templateUrl: './topic-list.component.html',
  styleUrls: ['./topic-list.component.scss'],
  standalone: true,
  imports: [CommonModule],
  providers: [DatePipe]
})
export class TopicListComponent implements OnInit {
  topics: Topic[] = [];
  loading = false;
  error: string | null = null;

  constructor(
    private http: HttpClient, 
    private router: Router,
    private datePipe: DatePipe
  ) {}

  ngOnInit(): void {
    this.loading = true;
    this.http.get<Topic[]>('/api/topics').subscribe({
      next: (topics) => {
        this.topics = topics;
        this.loading = false;
      },
      error: (err) => {
        this.error = err.error?.detail || 'Failed to load topics.';
        this.loading = false;
      }
    });
  }

  goToCreate() {
    this.router.navigate(['/topics/new']);
  }
  goToDetail(topic: Topic) {
    this.router.navigate(['/topics', topic.topic_id]);
  }

  formatDate(date: string): string {
    return this.datePipe.transform(date, 'medium') || date;
  }
} 