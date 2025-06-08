import { Routes } from '@angular/router';
import { CreateTopicComponent } from './components/create-topic/create-topic.component';
import { TopicListComponent } from './components/topic-list/topic-list.component';
import { TopicDetailComponent } from './components/topic-detail/topic-detail.component';

export const routes: Routes = [
  { path: '', component: TopicListComponent },
  { path: 'topics', component: TopicListComponent },
  { path: 'topics/new', component: CreateTopicComponent },
  { path: 'topics/:id', component: TopicDetailComponent },
  { path: '**', redirectTo: '' }
];
