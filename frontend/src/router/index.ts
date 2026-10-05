import {createRouter,createWebHistory} from 'vue-router'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import Board from '../views/Board.vue'

export default createRouter({
 history:createWebHistory(),
 routes:[
  {path:'/login',component:Login},
  {path:'/register',component:Register},
  {path:'/',redirect:'/board'},
  {path:'/board',component:Board}
 ]
})
