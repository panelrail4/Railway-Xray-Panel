<script setup>
import {onMounted, ref, computed} from 'vue'
import axios from 'axios'
import {useRouter} from 'vue-router'
const router=useRouter()
const items=ref([]); const error=ref('')
const form=ref({name:'xhttp-tls',protocol:'vless',transport:'xhttp',security:'tls',listen_port:10000,path:'/xhttp',flow:null,settings:{}})
const headers=()=>({Authorization:`Bearer ${localStorage.token}`})
const transportInfo=computed(()=>({
 xhttp:'XHTTP: بهترین گزینه برای تست Railway در این پروژه؛ روی سرور بدون TLS و روی لینک با TLS/SNI دامنه Railway ساخته می‌شود.',
 websocket:'WebSocket با مسیر اختصاصی؛ TLS لینک در Edge Railway خاتمه می‌یابد.',
 grpc:'gRPC از نظر Xray معتبر است، اما عبور HTTP/2 تا سرویس Railway به رفتار Edge وابسته است.',
 httpupgrade:'HTTPUpgrade با مسیر اختصاصی؛ پشتیبانی Edge/کلاینت باید بررسی شود.'
}[form.value.transport]||''))
async function load(){if(!localStorage.token){router.push('/login');return};try{items.value=(await axios.get('/api/inbounds',{headers:headers()})).data}catch(e){error.value=e.response?.data?.detail||'Load failed'}}
async function add(){try{error.value='';await axios.post('/api/inbounds',form.value,{headers:headers()});await load()}catch(e){error.value=typeof e.response?.data?.detail==='string'?e.response.data.detail:(e.response?.data?.detail?.[0]?.msg||JSON.stringify(e.response?.data)||e.message||'Create failed')}}
async function remove(id){if(confirm('Delete inbound?')){await axios.delete(`/api/inbounds/${id}`,{headers:headers()});await load()}}
onMounted(load)
</script>
<template><div class="card">
<h1>Inbounds</h1>
<p>در این معماری، <b>TLS در لینک کلاینت</b> فعال است ولی Xray داخل Railway TLS را terminate نمی‌کند؛ Railway HTTPS را در Edge خاتمه داده و درخواست را به پورت خصوصی Xray می‌رساند. این دقیقاً مدل پروژه قدیمی XHTTP است که گفتی با آن اتصال گرفتی.</p>
<div class="grid">
<input v-model="form.name" placeholder="Name">
<select v-model="form.transport"><option value="xhttp">XHTTP</option><option value="websocket">WebSocket</option><option value="grpc">gRPC</option><option value="httpupgrade">HTTPUpgrade</option></select>
<select v-model="form.security"><option value="tls">TLS (Railway Edge)</option><option value="none">بدون TLS</option><option value="reality">REALITY (فقط TCP Proxy)</option></select>
<input v-model.number="form.listen_port" type="number" min="10000" max="65535" placeholder="Private Xray port">
<input v-model="form.path" placeholder="/xhttp or /ws or /grpc or /upgrade">
<button @click="add">Create inbound</button>
</div>
<p class="hint">{{transportInfo}}</p>
<p v-if="error" class="err">{{error}}</p>
<table><tr><th>Name</th><th>Transport</th><th>Client security</th><th>Private port</th><th>Path</th><th></th></tr>
<tr v-for="i in items" :key="i.id"><td>{{i.name}}</td><td>{{i.transport}}</td><td>{{i.security}}</td><td>{{i.listen_port}}</td><td>{{i.path}}</td><td><button @click="remove(i.id)">Delete</button></td></tr></table>
</div></template>
<style scoped>.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}.grid input,.grid select,.grid button{margin:0}.hint{padding:10px;background:#eef5ff;border-radius:8px}.err{color:#b00020}@media(max-width:700px){.grid{grid-template-columns:1fr}}</style>
