<script setup lang="ts">
import {computed, onMounted, ref} from 'vue'
import {api, authConfig, useAuthStore} from '../stores/auth'
import type {Board as BoardType, Project, Task, Priority, Column} from '../types'

const auth=useAuthStore()
const projects=ref<Project[]>([]), selectedProjectId=ref<number|null>(null), board=ref<BoardType|null>(null)
const search=ref(''), priority=ref<Priority|''>(''), error=ref(''), loading=ref(false), draggedTask=ref<Task|null>(null)
const showProject=ref(false), showColumn=ref(false), showTask=ref(false), editingTask=ref<Task|null>(null)
const projectForm=ref({name:'',description:''}), columnForm=ref({name:'',wip_limit:''}), taskForm=ref({title:'',description:'',priority:'medium' as Priority,due_date:'',column_id:0})
const canManage=computed(()=>auth.user?.role==='admin'||auth.user?.role==='manager')

function cfg(){return authConfig(auth.token)}
async function loadProjects(){projects.value=(await api.get('/api/projects',cfg())).data;if(!selectedProjectId.value&&projects.value.length)selectedProjectId.value=projects.value[0].id;if(selectedProjectId.value)await loadBoard()}
async function loadBoard(){if(!selectedProjectId.value)return;loading.value=true;try{board.value=(await api.get(`/api/projects/${selectedProjectId.value}/board`,cfg())).data}catch(e:any){error.value=e.response?.data?.detail||'Не удалось загрузить доску'}finally{loading.value=false}}
async function createProject(){if(!projectForm.value.name.trim())return;await api.post('/api/projects',projectForm.value,cfg());projectForm.value={name:'',description:''};showProject.value=false;await loadProjects()}
async function editProject(){if(!board.value||!selectedProjectId.value)return;const p=projects.value.find(x=>x.id===selectedProjectId.value);if(!p)return;const name=prompt('Название проекта',p.name);if(!name)return;await api.patch(`/api/projects/${p.id}`,{name,description:p.description},cfg());await loadProjects()}
async function deleteProject(){if(!selectedProjectId.value||!confirm('Удалить проект вместе с доской и задачами?'))return;await api.delete(`/api/projects/${selectedProjectId.value}`,cfg());selectedProjectId.value=null;board.value=null;await loadProjects()}
async function renameBoard(){if(!board.value)return;const name=prompt('Название доски',board.value.name);if(name) {board.value=(await api.patch(`/api/boards/${board.value.id}`,{name},cfg())).data}}
async function createColumn(){if(!board.value||!columnForm.value.name.trim())return;await api.post(`/api/boards/${board.value.id}/columns`,{name:columnForm.value.name,position:board.value.columns.length,wip_limit:columnForm.value.wip_limit?Number(columnForm.value.wip_limit):null},cfg());columnForm.value={name:'',wip_limit:''};showColumn.value=false;await loadBoard()}
async function deleteColumn(col:Column){if(!confirm(`Удалить колонку «${col.name}» и её задачи?`))return;await api.delete(`/api/columns/${col.id}`,cfg());await loadBoard()}
async function createTask(col:Column){taskForm.value={title:'',description:'',priority:'medium',due_date:'',column_id:col.id};editingTask.value=null;showTask.value=true}
async function editTask(task:Task){taskForm.value={title:task.title,description:task.description,priority:task.priority,due_date:task.due_date||'',column_id:task.column_id};editingTask.value=task;showTask.value=true}
async function saveTask(){if(!taskForm.value.title.trim())return;const body={title:taskForm.value.title,description:taskForm.value.description,priority:taskForm.value.priority,due_date:taskForm.value.due_date||null,position:0};if(editingTask.value)await api.patch(`/api/tasks/${editingTask.value.id}`,{...body,column_id:taskForm.value.column_id},cfg());else await api.post(`/api/columns/${taskForm.value.column_id}/tasks`,body,cfg());showTask.value=false;await loadBoard()}
async function deleteTask(task:Task){if(confirm(`Удалить задачу «${task.title}»?`)){await api.delete(`/api/tasks/${task.id}`,cfg());await loadBoard()}}
async function move(task:Task,columnId:number){try{await api.patch(`/api/tasks/${task.id}`,{column_id:columnId},cfg());await loadBoard()}catch(e:any){error.value=e.response?.data?.detail||'Не удалось переместить задачу'}}
function visible(tasks:Task[]){const q=search.value.toLowerCase();return tasks.filter(t=>t.title.toLowerCase().includes(q)||t.description.toLowerCase().includes(q)).filter(t=>!priority.value||t.priority===priority.value)}
function dragStart(task:Task){draggedTask.value=task}
async function drop(col:Column){if(draggedTask.value){await move(draggedTask.value,col.id);draggedTask.value=null}}
onMounted(async()=>{await auth.loadMe();if(!auth.token){location.href='/login';return}await loadProjects()})
</script>
<template>
<main class="app">
<header><div><h1>Kanban-доска</h1><small v-if="auth.user">{{auth.user.email}} · {{auth.user.role}}</small></div><button class="secondary" @click="auth.logout();location.href='/login'">Выйти</button></header>
<section class="workspace">
<aside class="sidebar"><div class="side-title"><b>Проекты</b><button v-if="canManage" @click="showProject=true">+</button></div><button v-for="p in projects" :key="p.id" :class="['project-item',{active:p.id===selectedProjectId}]" @click="selectedProjectId=p.id;loadBoard()">{{p.name}}</button><p v-if="!projects.length" class="muted">Проектов пока нет.</p></aside>
<section class="content" v-if="board">
<div class="board-title"><div><input class="board-name" :value="board.name" readonly/><div class="muted">Проект: {{projects.find(p=>p.id===selectedProjectId)?.name}}</div></div><div class="actions"><button v-if="canManage" @click="renameBoard">Переименовать доску</button><button v-if="canManage" @click="editProject">Изменить проект</button><button v-if="canManage" class="danger" @click="deleteProject">Удалить проект</button></div></div>
<div class="toolbar"><input v-model="search" placeholder="Поиск задач..."/><select v-model="priority"><option value="">Все приоритеты</option><option value="low">Низкий</option><option value="medium">Средний</option><option value="high">Высокий</option></select><button v-if="canManage" @click="showColumn=true">+ Колонка</button></div>
<div class="board"><section v-for="col in board.columns" :key="col.id" class="column" @dragover.prevent @drop="drop(col)"><div class="column-head"><div><h2>{{col.name}}</h2><small>{{col.tasks.length}}{{col.wip_limit?' / '+col.wip_limit:''}}</small></div><button v-if="canManage" class="icon danger-text" @click="deleteColumn(col)">×</button></div><article v-for="task in visible(col.tasks)" :key="task.id" class="task" draggable="true" @dragstart="dragStart(task)"><div class="task-top"><b>{{task.title}}</b><span :class="['priority',task.priority]">{{task.priority}}</span></div><p v-if="task.description">{{task.description}}</p><small v-if="task.due_date">Дедлайн: {{task.due_date}}</small><div class="task-actions"><button @click="editTask(task)">Изменить</button><button class="danger-text" @click="deleteTask(task)">Удалить</button></div></article><button class="add-task" @click="createTask(col)">+ Добавить задачу</button></section></div>
</section><div v-else class="empty"><h2>Создай первый проект</h2><p>Проект автоматически получит Kanban-доску и три стандартные колонки.</p><button v-if="canManage" @click="showProject=true">Создать проект</button></div>
</section>
<div v-if="showProject" class="modal"><form class="modal-card" @submit.prevent="createProject"><h2>Новый проект</h2><input v-model="projectForm.name" placeholder="Название" required/><textarea v-model="projectForm.description" placeholder="Описание"></textarea><div class="modal-actions"><button type="button" class="secondary" @click="showProject=false">Отмена</button><button>Создать</button></div></form></div>
<div v-if="showColumn" class="modal"><form class="modal-card" @submit.prevent="createColumn"><h2>Новая колонка</h2><input v-model="columnForm.name" placeholder="Например: Review" required/><input v-model="columnForm.wip_limit" type="number" min="1" placeholder="WIP-лимит (необязательно)"/><div class="modal-actions"><button type="button" class="secondary" @click="showColumn=false">Отмена</button><button>Создать</button></div></form></div>
<div v-if="showTask" class="modal"><form class="modal-card" @submit.prevent="saveTask"><h2>{{editingTask?'Изменить':'Новая'}} задача</h2><input v-model="taskForm.title" placeholder="Название задачи" required/><textarea v-model="taskForm.description" placeholder="Описание"></textarea><select v-model="taskForm.priority"><option value="low">Низкий приоритет</option><option value="medium">Средний приоритет</option><option value="high">Высокий приоритет</option></select><input v-model="taskForm.due_date" type="date"/><select v-model.number="taskForm.column_id"><option v-for="c in board?.columns" :key="c.id" :value="c.id">{{c.name}}</option></select><div class="modal-actions"><button type="button" class="secondary" @click="showTask=false">Отмена</button><button>Сохранить</button></div></form></div>
<p v-if="error" class="toast error">{{error}} <button @click="error=''">×</button></p>
</main>
</template>
