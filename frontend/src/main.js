import { createApp } from "vue"
import { createPinia } from "pinia"
import { createRouter, createWebHistory } from "vue-router"
import App from "./App.vue"
import Login from "./pages/Login.vue"
import Dashboard from "./pages/Dashboard.vue"
import Users from "./pages/Users.vue"
import Inbounds from "./pages/Inbounds.vue"

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {path:"/login", component:Login},
    {path:"/", component:Dashboard, meta:{auth:true}},
    {path:"/users", component:Users, meta:{auth:true}},
    {path:"/inbounds", component:Inbounds, meta:{auth:true}},
    {path:"/subscriptions", component:()=>import("./pages/Subscriptions.vue"), meta:{auth:true}}
  ]
})
router.beforeEach((to)=>{
  if(to.meta.auth && !localStorage.token) return "/login"
})
createApp(App).use(createPinia()).use(router).mount("#app")
