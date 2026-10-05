<script setup lang="ts">
import {ref} from 'vue'
import {useRouter} from 'vue-router'
import {useAuthStore} from '../stores/auth'
import type {Role} from '../types'
const email=ref(''),password=ref(''),role=ref<Role>('developer'),error=ref('')
const router=useRouter(),auth=useAuthStore()
async function register(){error.value='';try{await auth.register(email.value,password.value,role.value);router.push('/board')}catch(e:any){error.value=e.response?.data?.detail||'Ошибка регистрации'}}
</script>
<template><main class="auth"><form class="card" @submit.prevent="register"><h1>Создание аккаунта</h1><input v-model="email" type="email" placeholder="Email" required/><input v-model="password" type="password" minlength="6" placeholder="Пароль (минимум 6 символов)" required/><select v-model="role"><option value="developer">Разработчик</option><option value="manager">Менеджер</option><option value="admin">Администратор</option></select><button>Зарегистрироваться</button><span class="error">{{error}}</span><p>Уже есть аккаунт? <RouterLink to="/login">Войти</RouterLink></p></form></main></template>
