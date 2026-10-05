<script setup lang="ts">
import {ref} from 'vue'
import {useRouter} from 'vue-router'
import {useAuthStore} from '../stores/auth'
const email=ref('admin@example.com'),password=ref('password'),error=ref('')
const router=useRouter(),auth=useAuthStore()
async function login(){error.value='';try{await auth.login(email.value,password.value);router.push('/board')}catch(e:any){error.value=e.response?.data?.detail||'Ошибка входа'}}
</script>
<template><main class="auth"><form class="card" @submit.prevent="login"><h1>Kanban</h1><p>Вход в систему</p><input v-model="email" type="email" placeholder="Email" required/><input v-model="password" type="password" placeholder="Пароль" required/><button>Войти</button><span class="error">{{error}}</span><p>Нет аккаунта? <RouterLink to="/register">Зарегистрироваться</RouterLink></p></form></main></template>
