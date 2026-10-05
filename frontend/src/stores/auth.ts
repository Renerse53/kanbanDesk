import {defineStore} from 'pinia'
import axios from 'axios'
import type {Role, User} from '../types'

export const api=axios.create({baseURL:'http://localhost:8000'})

export const useAuthStore=defineStore('auth',{
  state:()=>({token:localStorage.getItem('token')||'', user: null as User|null}),
  actions:{
    async login(email:string,password:string){
      const r=await api.post('/api/auth/login',{email,password,role:'developer'})
      this.token=r.data.access_token; localStorage.setItem('token',this.token)
      await this.loadMe()
    },
    async register(email:string,password:string,role:Role){
      await api.post('/api/auth/register',{email,password,role})
      await this.login(email,password)
    },
    async loadMe(){
      if(!this.token)return
      try{this.user=(await api.get('/api/auth/me',{headers:{Authorization:`Bearer ${this.token}`}})).data}
      catch{this.logout()}
    },
    logout(){this.token='';this.user=null;localStorage.removeItem('token')}
  }
})

export function authConfig(token:string){return {headers:{Authorization:`Bearer ${token}`}}}
