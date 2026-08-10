<script setup>
import {onMounted,ref} from 'vue'; import axios from 'axios'; import {useRouter} from 'vue-router'
const router=useRouter(); const users=ref([]); const name=ref(''); const error=ref(''); const links=ref(null); const qr=ref(null)
const headers=()=>({Authorization:`Bearer ${localStorage.token}`})
async function load(){if(!localStorage.token){router.push('/login');return};try{users.value=(await axios.get('/api/users',{headers:headers()})).data}catch(e){error.value=e.response?.data?.detail||'Load failed'}}
async function add(){try{await axios.post('/api/users',{username:name.value},{headers:headers()});name.value='';await load()}catch(e){error.value=e.response?.data?.detail||'Create failed'}}
async function remove(id){if(confirm('Delete user?')){await axios.delete(`/api/users/${id}`,{headers:headers()});await load()}}
async function showLinks(id){links.value=(await axios.get(`/api/users/${id}/links`,{headers:headers()})).data;qr.value=null}
async function showQR(userId,inboundId,variant){const r=await axios.get('/api/qr/link',{headers:headers(),params:{user_id:userId,inbound_id:inboundId,variant},responseType:'blob'});qr.value=URL.createObjectURL(r.data)}
onMounted(load)
</script>
<template><div class="card"><h1>Users</h1><input v-model="name" placeholder="username"><button @click="add">Create</button><p v-if="error">{{error}}</p>
<table><tr><th>Username</th><th>UUID</th><th>Enabled</th><th>Actions</th></tr>
<tr v-for="u in users" :key="u.id"><td>{{u.username}}</td><td><code>{{u.uuid}}</code></td><td>{{u.enabled}}</td><td><button @click="showLinks(u.id)">Links / QR</button><button @click="remove(u.id)">Delete</button></td></tr></table>
<div v-if="links"><h3>{{links.user.username}}</h3><div v-for="l in links.links" :key="l.inbound_id" class="linkcard"><b>{{l.name}} — {{l.transport}}</b><p><small>Railway TLS:</small></p><textarea rows="3" style="width:100%">{{l.variants['edge-tls']}}</textarea><button @click="showQR(links.user.id,l.inbound_id,'edge-tls')">QR TLS</button><p><small>Plain HTTP:</small></p><textarea rows="3" style="width:100%">{{l.variants['plain-http']}}</textarea><button @click="showQR(links.user.id,l.inbound_id,'plain-http')">QR Plain</button></div></div>
<img v-if="qr" :src="qr" class="qr">
</div></template>
<style scoped>.linkcard{border:1px solid #e1e6ee;padding:12px;border-radius:10px;margin:10px 0}.qr{width:260px;height:260px;image-rendering:auto}textarea{font-family:monospace}</style>
