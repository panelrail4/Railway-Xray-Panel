<script setup>
import {onMounted,ref} from 'vue'; import axios from 'axios'; import {useRouter} from 'vue-router'
const router=useRouter(); const token=localStorage.token; const h={Authorization:`Bearer ${token}`}; const health=ref({}),cap=ref({}),xray=ref({}),error=ref('')
async function load(){if(!token){router.push('/login');return};try{health.value=(await axios.get('/api/health')).data}catch{};try{cap.value=(await axios.get('/api/system/capabilities',{headers:h})).data}catch(e){error.value=e.response?.data?.detail||'Authorization required'};try{xray.value=(await axios.get('/api/xray/status',{headers:h})).data}catch{}}
async function restart(){await axios.post('/api/xray/restart',{}, {headers:h});await load()}
onMounted(load)
</script>
<template><div><div class="card"><h1>Railway XPanel 1.0.10</h1><p>Health: {{health.status}}</p><p>Database: {{health.database}}</p><p>Xray: <b>{{xray.status || health.xray}}</b> <button @click="restart">Restart Xray</button></p><p v-if="error">{{error}}</p></div><div class="card"><h2>Railway transport model</h2><p>Public domain: <b>{{cap.public_domain||'Set PUBLIC_HOST if Railway does not expose it'}}</b></p><p>TCP Proxy: <b>{{cap.tcp_proxy ? cap.tcp_proxy_domain+':'+cap.tcp_proxy_port : 'Disabled'}}</b></p><p>مدل TLS این نسخه: <b>Client TLS → Railway Edge → HTTP → Nginx → Xray</b></p><p>برای XHTTP ابتدا لینک TLS تولیدشده را بدون تغییر server-side استفاده کن. اگر قبلاً همانند پروژه قدیمی، لینک بدون TLS گرفتی، فقط TLS را در v2rayNG روشن و SNI را برابر Public Domain قرار بده.</p></div></div></template>
