<script setup>
import {ref} from "vue"; import axios from "axios"; import {useRouter} from "vue-router"
const username=ref(""), password=ref(""), error=ref(""); const router=useRouter()
async function login(){try{const r=await axios.post("/api/auth/login",{username:username.value,password:password.value});localStorage.token=r.data.access_token;router.push("/")}catch(e){error.value=e.response?.data?.detail||"Login failed"}}
</script>
<template><div class="card"><h1>Login</h1><input v-model="username" autocomplete="username" placeholder="Username"><input v-model="password" autocomplete="current-password" type="password" placeholder="Password"><button @click="login">Login</button><p>{{error}}</p></div></template>
