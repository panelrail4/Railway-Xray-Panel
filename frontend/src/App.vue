<template>
  <main class="shell">
    <nav>
      <strong>Railway XPanel</strong>
      <span>
        <router-link to="/">Dashboard</router-link> ·
        <router-link to="/users">Users</router-link> ·
        <router-link to="/inbounds">Inbounds</router-link> ·
        <router-link to="/subscriptions">Subscriptions</router-link> ·
        <router-link to="/login">Login</router-link>
        <button @click="logout">Logout</button>
      </span>
    </nav>
    <router-view />
  </main>
</template>
<script setup>
import {useRouter} from "vue-router"
const router=useRouter()
function logout(){localStorage.removeItem("token");router.push("/login")}
</script>
<style>
body{font-family:system-ui;margin:0;background:#f5f7fb;color:#18202a}.shell{max-width:1100px;margin:auto;padding:24px}nav{display:flex;justify-content:space-between;padding:16px;background:white;border-radius:12px;margin-bottom:20px}a{color:#2255aa;text-decoration:none}.card{background:white;padding:20px;border-radius:12px;margin:12px 0}input,select,button{padding:10px;margin:6px;border:1px solid #ccd3dd;border-radius:8px}button{cursor:pointer}table{width:100%;border-collapse:collapse}td,th{padding:8px;border-bottom:1px solid #eee;text-align:left}code{word-break:break-all}textarea{box-sizing:border-box}
</style>
