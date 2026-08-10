<script setup>
import {ref,onMounted} from 'vue'; import axios from 'axios'; import {useRouter} from 'vue-router'
const router=useRouter(); const users=ref([]), result=ref(null), error=ref(''), qr=ref(null)
const h=()=>({Authorization:`Bearer ${localStorage.token}`})
onMounted(async()=>{if(!localStorage.token){router.push('/login');return};try{users.value=(await axios.get('/api/users',{headers:h()})).data}catch(e){error.value=e.response?.data?.detail||'Load failed'}})
async function make(id){try{error.value='';result.value=(await axios.post('/api/subscriptions/'+id,{}, {headers:h()})).data;qr.value=null}catch(e){result.value=null;error.value=e.response?.data?.detail||'Subscription failed'}}
async function showQR(token){const r=await axios.get('/api/qr/subscription/'+token,{headers:h(),responseType:'blob'});qr.value=URL.createObjectURL(r.data)}
</script>
<template><div class="card"><h1>Subscriptions</h1><p>سابسکریپشن فقط لینک‌های سازگار با Railway Edge TLS را در خود قرار می‌دهد.</p><p v-if="error">{{error}}</p><div v-for="u in users" :key="u.id" class="row"><b>{{u.username}}</b><button @click="make(u.id)">Create subscription</button></div><div v-if="result"><p><b>Subscription URL</b></p><textarea rows="2" style="width:100%">{{result.url}}</textarea><button @click="showQR(result.token)">QR subscription</button><div v-for="l in result.links" :key="l"><textarea rows="4" style="width:100%">{{l}}</textarea></div><img v-if="qr" :src="qr" class="qr"></div></div></template>
<style scoped>.row{padding:10px 0;border-bottom:1px solid #eee}.qr{width:260px;height:260px}</style>
