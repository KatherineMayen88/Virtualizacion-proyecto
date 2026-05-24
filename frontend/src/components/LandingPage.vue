<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

defineEmits(['open-login'])

const API_BASE = 'http://localhost:5000/api'

const songs = ref([])
const genres = ref([])
const topSongs = ref([])

const songForm = ref({ title: '', artist: '', genre: '' })
const publicRatings = ref({})

const loadData = async () => {
  const [s, g, t] = await Promise.all([
    axios.get(`${API_BASE}/songs`),
    axios.get(`${API_BASE}/genres`),
    axios.get(`${API_BASE}/songs/top`)
  ])
  songs.value = s.data
  genres.value = g.data
  topSongs.value = t.data
}

const addSong = async () => {
  await axios.post(`${API_BASE}/songs`, songForm.value)
  songForm.value = { title: '', artist: '', genre: '' }
  await loadData()
}

const submitPublicRating = async (songId) => {
  await axios.post(`${API_BASE}/ratings/public`, {
    songId, score: Number(publicRatings.value[songId] || 0)
  })
  await loadData()
}

onMounted(loadData)
</script>

<template>
  <main class="page">

    <!-- HERO — compacto para ceder espacio a los paneles -->
    <section class="hero">
      <div class="hero-left">
        <p class="eyebrow">Docker + VUE + Flask + MongoDB</p>
        <h1>Music Discovery</h1>
        <p class="subtitle">Explore trends, manage songs, genres and listeners</p>
      </div>

      <div class="hero-right">
        <div class="stats">
          <div class="stat-card">
            <strong>{{ songs.length }}</strong>
            <span>Songs</span>
          </div>
          <div class="stat-card">
            <strong>{{ genres.length }}</strong>
            <span>Genres</span>
          </div>
          <div class="stat-card">
            <strong>{{ topSongs.length }}</strong>
            <span>Users</span>
          </div>
        </div>
        <button class="cta-btn" @click="$emit('open-login')">Sign in with user</button>
      </div>
    </section>

    <!-- GRID — ocupa el máximo espacio vertical disponible -->
    <section class="grid">

      <div class="col">
        <div class="panel add-panel">
          <h2>Add Song</h2>
          <input v-model="songForm.title" placeholder="Song title" />
          <input v-model="songForm.artist" placeholder="Artist" />
          <input v-model="songForm.genre" placeholder="Genre" />
          <button class="green-btn" @click="addSong">Save song</button>
        </div>

        <div class="panel rank-panel">
          <h2>Rank global songs</h2>
          <div class="list">
            <div v-for="song in songs" :key="song.id" class="card">
              <div class="card-info">
                <strong>{{ song.title }}</strong>
                <span>{{ song.artist }} · {{ song.genre }}</span>
              </div>
              <div class="card-right">
                <div class="sel-wrap">
                  <select v-model="publicRatings[song.id]" class="sel">
                    <option value="" disabled selected hidden></option>
                    <option v-for="n in 10" :key="n" :value="n">{{ n }}</option>
                  </select>
                  <span class="sel-ph" v-if="!publicRatings[song.id]">1-10</span>
                </div>
                <button class="small-btn" @click="submitPublicRating(song.id)">Rank</button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="panel top-songs-panel">
        <h2>Top Songs</h2>
        <div class="list">
          <div v-for="song in topSongs" :key="song.songId" class="card">
            <div class="card-info">
              <strong>{{ song.title }}</strong>
              <span>{{ song.artist }} · {{ song.genre }}</span>
            </div>
            <div class="card-right">
              <span class="badge">🔥 {{ song.averageScore }}</span>
              <span class="badge muted">🎵 {{ song.rankingCount }}</span>
            </div>
          </div>
        </div>
      </div>

    </section>
  </main>
</template>

<style scoped>
* { box-sizing: border-box; margin: 0; padding: 0; }

.page {
  min-height: 100vh;
  overflow-x: hidden;
  overflow-y: auto;

  background: #161616;
  color: #fff;
  font-family: 'Poppins', sans-serif;
  display: flex;
  flex-direction: column;
  /* Hero toma su altura natural, grid toma el resto */
  padding: 20px 36px 20px;
  gap: 16px;
}

/* ── HERO — más compacto ──────────────────── */
.hero {
  display: flex;
  justify-content: space-between;
  align-items: center;        /* centrado vertical para que no tome tanto espacio */
  gap: 24px;
  flex-shrink: 0;
}

.hero-left { flex: 1; }

.eyebrow {
  color: #00d856;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: .04em;
  margin-bottom: 2px;
}

h1 {
  /* Más pequeño para que el hero no robe altura a los paneles */
  font-size: clamp(32px, 3.8vw, 56px);
  line-height: .9;
  font-weight: 700;
  margin-bottom: 6px;
}

.subtitle { color: #888; font-size: 12px; }

.hero-right {
  display: flex;
  flex-direction: column;
  gap: 8px;
  flex-shrink: 0;
  width: 310px;
}

.stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; }

.stat-card {
  background: #252525;
  border-radius: 12px;
  padding: 10px 8px;
  display: flex; flex-direction: column; align-items: center; gap: 2px;
}
.stat-card strong { font-size: 26px; font-weight: 800; line-height: 1; }
.stat-card span   { font-size: 10px; color: #888; font-weight: 600; }

.cta-btn {
  width: 100%; border: none; border-radius: 30px; padding: 10px;
  background: #00d856; color: #fff; font-weight: 700; font-size: 13px; cursor: pointer;
}
.cta-btn:hover { background: #00b848; }

/* ── GRID — crece para llenar el resto ───── */
.grid {
  flex: 1;                    /* toma TODO el espacio que queda después del hero */
  display: grid;
  /*grid-template-columns: repeat(2, minmax(420px, 1fr));*/
  grid-template-columns: 1fr 1fr;
  gap: 30px;
  margin-top: 30px;
  align-items: start;
  min-height: 0;              /* necesario para que flex:1 funcione con overflow */
}

.col {
  display: flex;
  flex-direction: column;
  gap: 40px;
  min-height: 0;
}

.panel {
  background: #222;
  border-radius: 24px;
  padding: 22px;
  display: flex; flex-direction: column; gap: 10px;
}

/* Add Song: altura natural por su contenido */
.add-panel { flex-shrink: 0; }

/* Rank + Top Songs: crecen para llenar la columna */
.flex-panel { 
  flex: 1; 
  height: 520px;
  min-height: 0; 
}

/* TOP SONGS MÁS ALTO */
.top-songs-panel {

  height: 780px;
  display: flex;
  flex-direction: column;
}

/* RANK SONGS CON SCROLL */
.rank-panel {

  height: 500px;
  display: flex;
  flex-direction: column;
}


.panel h2 { font-size: 14px; font-weight: 700; flex-shrink: 0; }

/* ── INPUTS ───────────────────────────────── */
input {
  width: 100%; border: none; border-radius: 8px;
  padding: 9px 12px; background: #333; color: #fff; font-size: 13px; outline: none;
}
input::placeholder { color: #888; }

.green-btn {
  width: 100%; border: none; border-radius: 30px; padding: 10px;
  background: #00d856; color: #fff; font-weight: 700; font-size: 13px; cursor: pointer; margin-top: 2px;
}
.green-btn:hover { background: #00b848; }

/* ── LIST ─────────────────────────────────── */
.list {
  flex: 1; 
  overflow-y: auto; 
  min-height: 0;
  padding-right: 8px;
  display: flex; 
  flex-direction: column; 
  gap: 14px;
}
.list::-webkit-scrollbar { width: 3px; }
.list::-webkit-scrollbar-track { background: transparent; }
.list::-webkit-scrollbar-thumb { background: #00d856; border-radius: 4px; }

/* ── CARD ─────────────────────────────────── */
.card {
  background: #2e2e2e; border-radius: 10px; padding: 9px 12px;
  display: flex; justify-content: space-between; align-items: center;
  gap: 10px; flex-shrink: 0;
}
.card-info { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 2px; }
.card-info strong { font-size: 13px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.card-info span   { font-size: 11px; color: #888; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.card-right { display: flex; align-items: center; gap: 7px; flex-shrink: 0; }

/* ── SELECT + PLACEHOLDER ─────────────────── */
.sel-wrap { position: relative; width: 62px; flex-shrink: 0; }

.sel {
  width: 100%; border: none; border-radius: 20px; padding: 6px 8px;
  background: #444; color: #fff; font-size: 12px; font-weight: 600;
  cursor: pointer; appearance: none; -webkit-appearance: none;
  text-align: center; outline: none; position: relative; z-index: 1;
}
.sel:has(option[value=""]:checked) { color: transparent; }
.sel option { background: #333; color: #fff; }

.sel-ph {
  position: absolute; top: 50%; left: 50%;
  transform: translate(-50%, -50%);
  font-size: 12px; font-weight: 600; color: #ccc;
  pointer-events: none; z-index: 2; white-space: nowrap;
}

.small-btn {
  border: none; border-radius: 20px; padding: 6px 14px;
  background: #00d856; color: #fff; font-weight: 700; font-size: 12px; cursor: pointer;
}
.small-btn:hover { background: #00b848; }

.badge {
  font-size: 12px; font-weight: 700;
  background: #2a2a2a; border-radius: 20px; padding: 4px 10px; color: #fff;
}
.badge.muted { color: #888; }

@media (max-width: 860px) {
  .page { height: auto; overflow: auto; padding: 20px; }
  .hero { flex-direction: column; align-items: flex-start; }
  .hero-right { width: 100%; }
  .grid { grid-template-columns: 1fr; }
  .flex-panel { min-height: 380px; }
}
</style>