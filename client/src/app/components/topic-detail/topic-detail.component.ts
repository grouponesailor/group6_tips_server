import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { DatePipe, CommonModule } from '@angular/common';

interface Tip {
  tip_id: number;
  title: string;
  description: string;
  media?: { type: string; url: string; alt_text?: string };
  display_order: number;
  topic_id: number;
  created_at: string;
  updated_at: string;
}

interface Topic {
  topic_id: number;
  title: string;
  description: string;
  media?: { type: string; url: string; alt_text?: string };
  tips: Tip[];
  created_at: string;
  updated_at: string;
}

@Component({
  selector: 'app-topic-detail',
  templateUrl: './topic-detail.component.html',
  styleUrls: ['./topic-detail.component.scss'],
  standalone: true,
  imports: [CommonModule],
  providers: [DatePipe]
})
export class TopicDetailComponent implements OnInit {
  topic: Topic | null = null;
  loading = false;
  error: string | null = null;

  constructor(
    private route: ActivatedRoute, 
    private http: HttpClient,
    private datePipe: DatePipe
  ) {}

  ngOnInit(): void {
    this.loading = true;
    const id = this.route.snapshot.paramMap.get('id');
    this.http.get<Topic>(`/api/topics/${id}`).subscribe({
      next: (topic) => {
        this.topic = topic;
        this.loading = false;
      },
      error: (err) => {
        this.error = err.error?.detail || 'Failed to load topic.';
        this.loading = false;
      }
    });
  }

  formatDate(date: string): string {
    return this.datePipe.transform(date, 'medium') || date;
  }
} 