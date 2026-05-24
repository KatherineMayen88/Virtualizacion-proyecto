<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const props = defineProps({ user: { type: Object, required: true } })
const emit = defineEmits(['logout'])

const API_BASE = 'http://localhost:5000/api'

const songs = ref([])
const profile = ref(null)
const recommendations = ref([])
const dismissedRecommendations = ref([])
const ratings = ref({})
const editScores = ref({})
const songForm = ref({ title: '', artist: '', genre: '', score: '' })
const addingGenre = ref(false)
const newGenreText = ref('')

const availableGenres = [
  'Pop',
  'Rock',
  'Alternative',
  'Indie',
  'Country',
  'Hip-Hop',
  'R&B',
  'Electronic',
  'Latin'
]

const toggleGenre = async (genre) => {
  const currentGenres = profile.value?.user.favoriteGenres || []

  let updatedGenres = []

  if (currentGenres.includes(genre)) {
    updatedGenres = currentGenres.filter(item => item !== genre)
  } else {
    if (currentGenres.length >= 3) {
      return
    }

    updatedGenres = [...currentGenres, genre]
  }

  await axios.put(`${API_BASE}/users/${props.user.id}`, {
    username: profile.value.user.username,
    fullName: profile.value.user.fullName,
    favoriteGenres: updatedGenres
  })

  dismissedRecommendations.value = []

  await loadPortalData()
}

const clearGenres = async () => {
  await axios.put(`${API_BASE}/users/${props.user.id}`, {
    username: profile.value.user.username,
    fullName: profile.value.user.fullName,
    favoriteGenres: []
  })

  dismissedRecommendations.value = []

  await loadPortalData()
}

const isGenreSelected = (genre) => {
  return profile.value?.user.favoriteGenres?.includes(genre)
}


const loadPortalData = async () => {
  const exclude = dismissedRecommendations.value.join(',')
  const [s, p, r] = await Promise.all([
    axios.get(`${API_BASE}/songs`),
    axios.get(`${API_BASE}/users/${props.user.id}/profile`),
    axios.get(`${API_BASE}/users/${props.user.id}/recommendations`, { params: { exclude } })
  ])
  songs.value = s.data
  profile.value = p.data
  recommendations.value = r.data
}

const addSong = async () => {
  if (!songForm.value.title) return
  const res = await axios.post(`${API_BASE}/songs`, {
    title: songForm.value.title,
    artist: songForm.value.artist,
    genre: songForm.value.genre
  })
  if (songForm.value.score) {
    await axios.post(`${API_BASE}/ratings/user`, {
      userId: props.user.id, songId: res.data.id, score: Number(songForm.value.score)
    })
  }
  songForm.value = { title: '', artist: '', genre: '', score: '' }
  await loadPortalData()
}

const removeGenre = async (g) => {
  const updated = (profile.value?.user.favoriteGenres || []).filter(x => x !== g)
  await axios.put(`${API_BASE}/users/${props.user.id}`, {
    username: profile.value.user.username,
    fullName: profile.value.user.fullName,
    favoriteGenres: updated
  })
  await loadPortalData()
}

const addGenre = async () => {
  if (!newGenreText.value.trim()) return
  const cur = profile.value?.user.favoriteGenres || []
  if (cur.includes(newGenreText.value.trim())) { newGenreText.value = ''; addingGenre.value = false; return }
  await axios.put(`${API_BASE}/users/${props.user.id}`, {
    username: profile.value.user.username,
    fullName: profile.value.user.fullName,
    favoriteGenres: [...cur, newGenreText.value.trim()]
  })
  newGenreText.value = ''; addingGenre.value = false
  await loadPortalData()
}

const rankSong = async (songId) => {
  if (!ratings.value[songId]) return
  await axios.post(`${API_BASE}/ratings/user`, {
    userId: props.user.id, songId, score: Number(ratings.value[songId])
  })
  ratings.value[songId] = ''
  await loadPortalData()
}

const updateRating = async (ratingId) => {
  if (!editScores.value[ratingId]) return
  await axios.put(`${API_BASE}/ratings/${ratingId}`, { score: Number(editScores.value[ratingId]) })
  editScores.value[ratingId] = ''
  await loadPortalData()
}

const deleteRating = async (ratingId) => {
  await axios.delete(`${API_BASE}/ratings/${ratingId}`)
  await loadPortalData()
}

const addRecommendationToSongs = async (song) => {
  const r = await axios.post(`${API_BASE}/songs`, { title: song.title, artist: song.artist, genre: song.genre })
  await axios.post(`${API_BASE}/ratings/user`, { userId: props.user.id, songId: r.data.id, score: 10 })
  await loadPortalData()
}

const dismissRecommendation = async (song) => {
  dismissedRecommendations.value.push(song.title)
  await loadPortalData()
}

onMounted(loadPortalData)
</script>

<template>
  <main class="page">

    <section class="hero">
      <div class="hero-left">
        <p class="eyebrow">Welcome to Music Discovery</p>
        <h1>@{{ user.username }}</h1>
        <p class="subtitle">Manage your rankings, favorite genres and recommendations.</p>
      </div>
      <div class="hero-right">
        <div class="stats">
          <div class="stat-card">
            <strong>{{ songs.length }}</strong>
            <span>Songs</span>
          </div>
          <div class="stat-card">
            <strong>{{ profile?.user?.favoriteGenres?.length || 0 }}</strong>
            <span>Genres</span>
          </div>
          <div class="stat-card">
            <strong>{{ profile?.totalRankings || 0 }}</strong>
            <span>Rankings</span>
          </div>
        </div>
        <button class="cta-btn" @click="emit('logout')">Log out</button>
      </div>
    </section>

    <section class="portal-grid">

      <!-- Add Songs -->
      <div class="panel">
        <h2>Add your favorite songs!</h2>
        <input v-model="songForm.title" placeholder="Song title" />
        <input v-model="songForm.artist" placeholder="Artist" />
        <input v-model="songForm.genre" placeholder="Genre" />
        <div class="rank-row">
          <span class="rank-label">Rank</span>
          <select v-model="songForm.score" class="sel-inline">
            <option value="" disabled selected>Select 1-10</option>
            <option v-for="n in 10" :key="n" :value="n">{{ n }}</option>
          </select>
          <span class="auto-hint">Auto-ranks on save</span>
        </div>
        <button class="green-btn" @click="addSong">Save song</button>
      </div>

      <!-- Favorite Genres -->
      <div class="panel genre-panel">
        <h2>Your favorite genres</h2>

        <div class="genre-options">
          <button
            v-for="genre in availableGenres"
            :key="genre"
            class="genre-chip"
            :class="{ selected: isGenreSelected(genre) }"
            @click="toggleGenre(genre)"
          >
            {{ genre }}
          </button>
        </div>

        <button
            class="clear-btn"
            @click="clearGenres"
          >
            Clear genres
          </button>

        <p class="genre-help">
          Select up to 3 genres to receive mixed recommendations.
        </p>
      </div>

      <!-- Ranked Songs -->
      <div class="panel list-panel">
        <h2>Your ranked songs</h2>
        <div class="list">
          <div v-for="item in profile?.rankedSongs" :key="item.ratingId" class="card">
            <div class="card-info">
              <strong>{{ item.title }}</strong>
              <span>{{ item.artist }} · {{ item.genre }}</span>
            </div>
            <div class="card-right">
              <span class="score-pill">🔥 {{ item.score }}</span>
              <div class="sel-wrap">
                <select v-model="editScores[item.ratingId]" class="sel">
                  <option value="" disabled selected hidden></option>
                  <option v-for="n in 10" :key="n" :value="n">{{ n }}</option>
                </select>
                <span class="sel-placeholder" v-if="!editScores[item.ratingId]">1-10</span>
              </div>
              <button class="small-btn" @click="updateRating(item.ratingId)">Rank</button>
              <button class="del-btn" @click="deleteRating(item.ratingId)">Delete</button>
            </div>
          </div>
          <p v-if="!profile?.rankedSongs?.length" class="empty">No ranked songs yet.</p>
        </div>
      </div>

      <!-- Global Songs -->
      <div class="panel list-panel">
        <h2>Global songs in MusicDiscovery</h2>
        <div class="list">
          <div v-for="song in songs" :key="song.id" class="card">
            <div class="card-info">
              <strong>{{ song.title }}</strong>
              <span>{{ song.artist }} · {{ song.genre }}</span>
            </div>
            <div class="card-right">
              <span v-if="song.averageScore" class="score-pill muted">⭐ {{ song.averageScore }}</span>
              <div class="sel-wrap">
                <select v-model="ratings[song.id]" class="sel">
                  <option value="" disabled selected hidden></option>
                  <option v-for="n in 10" :key="n" :value="n">{{ n }}</option>
                </select>
                <span class="sel-placeholder" v-if="!ratings[song.id]">1-10</span>
              </div>
              <button class="small-btn" @click="rankSong(song.id)">Rank</button>
            </div>
          </div>
        </div>
      </div>

      <!-- Recommendations -->
      <div class="panel rec-panel" v-if="recommendations.length">
        <h2>Recommendations for you</h2>
        <div class="rec-list">
          <div v-for="song in recommendations" :key="song.previewUrl || song.title" class="rec-card">
            <img v-if="song.artworkUrl" :src="song.artworkUrl" class="album-art" />
            <div class="rec-info">
              <strong>{{ song.title }}</strong>
              <span>{{ song.artist }} · {{ song.genre }}</span>
              <audio v-if="song.previewUrl" :src="song.previewUrl" controls></audio>
            </div>
            <div class="rec-btns">
              <button class="small-btn" @click="addRecommendationToSongs(song)">Add to my songs</button>
              <button class="blue-btn" @click="dismissRecommendation(song)">Not for me</button>
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
  background: #161616;
  color: #fff;
  font-family: 'Poppins', sans-serif;
  display: flex; flex-direction: column;
  padding: 28px 36px;
  gap: 20px;
}

.hero {
  display: flex; justify-content: space-between; align-items: flex-start;
  gap: 42px; flex-shrink: 0;
}
.hero-left { flex: 1; }
.eyebrow { color: #00d856; font-size: 12px; font-weight: 700; letter-spacing: .04em; margin-bottom: 4px; }
h1 { font-size: clamp(28px, 3.5vw, 50px); font-weight: 700; line-height:.9; margin-bottom: 6px; }
.subtitle { color: #888; font-size: 13px; }

.hero-right { display: flex; flex-direction: column; gap: 10px; flex-shrink: 0; width: 320px; }
.stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; }
.stat-card {
  background: #252525; border-radius: 14px; padding: 14px 8px;
  display: flex; flex-direction: column; align-items: center; gap: 3px;
}
.stat-card strong { font-size: 28px; font-weight: 800; line-height: 1; }
.stat-card span   { font-size: 11px; color: #888; font-weight: 600; }

.cta-btn {
  width: 100%; border: none; border-radius: 30px; padding: 11px;
  background: #00d856; color: #fff; font-weight: 700; font-size: 13px; cursor: pointer;
}
.cta-btn:hover { background: #00b848; }

/* ── GRID ─────────────────────────────────── */
.portal-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 28px;
}

.panel {
  background: #222; border-radius: 16px; padding: 18px 20px;
  display: flex; flex-direction: column; gap: 10px;
}

.list-panel { height: 380px; }

.genre-panel { justify-content: space-between; min-height: 200px; }

.rec-panel { grid-column: 1 / -1; }

.panel h2 { font-size: 14px; font-weight: 700; flex-shrink: 0; }

/* ── INPUTS ───────────────────────────────── */
input {
  width: 100%; border: none; border-radius: 8px;
  padding: 9px 12px; background: #333; color: #fff; font-size: 13px; outline: none;
}
input::placeholder { color: #888; }

/* Rank row en Add Song */
.rank-row {
  display: flex; align-items: center; gap: 10px;
  background: #333; border-radius: 8px; padding: 9px 12px;
}
.rank-label { font-size: 13px; color: #888; flex-shrink: 0; }
.sel-inline {
  flex: 1; border: none; background: transparent;
  color: #fff; font-size: 13px; font-weight: 600;
  cursor: pointer; outline: none;
  appearance: none; -webkit-appearance: none;
}
.sel-inline option { background: #333; }
.auto-hint { font-size: 11px; color: #00d856; flex-shrink: 0; white-space: nowrap; }

.green-btn {
  width: 100%; border: none; border-radius: 30px; padding: 10px;
  background: #00d856; color: #fff; font-weight: 700; font-size: 13px; cursor: pointer;
}
.green-btn:hover { background: #00b848; }
.small-green { width: auto; padding: 8px 24px; }

/* ── LIST ─────────────────────────────────── */
.list {
  flex: 1; overflow-y: auto; min-height: 0; padding-right: 4px;
  display: flex; flex-direction: column; gap: 14px;
}
.genre-list { max-height: 140px; flex: none; }
.list::-webkit-scrollbar { width: 3px; }
.list::-webkit-scrollbar-track { background: transparent; }
.list::-webkit-scrollbar-thumb { background: #00d856; border-radius: 4px; }

/* ── CARD ─────────────────────────────────── */
.card {
  background: #2e2e2e; border-radius: 10px; padding: 9px 12px;
  display: flex; justify-content: space-between; align-items: center; gap: 8px; flex-shrink: 0;
}
.card-info { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 2px; }
.card-info strong { font-size: 13px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.card-info span   { font-size: 11px; color: #888; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.genre-name { font-size: 13px; font-weight: 600; }
.card-right { display: flex; align-items: center; gap: 6px; flex-shrink: 0; }

/* ── SELECT CON PLACEHOLDER ───────────────── */
.sel-wrap { position: relative; width: 62px; flex-shrink: 0; }

.sel {
  width: 100%; border: none; border-radius: 20px; padding: 6px 8px;
  background: #444; color: #fff; font-size: 12px; font-weight: 600;
  cursor: pointer; appearance: none; -webkit-appearance: none;
  text-align: center; outline: none; position: relative; z-index: 1;
}
/* Cuando no hay valor seleccionado, hacemos el texto transparente para ver el placeholder */
.sel:has(option[value=""]:checked) { color: transparent; }
.sel option { background: #333; color: #fff; }

.sel-placeholder {
  position: absolute;
  top: 50%; left: 50%;
  transform: translate(-50%, -50%);
  font-size: 12px; font-weight: 600; color: #ccc;
  pointer-events: none; z-index: 2;
  white-space: nowrap;
}

/* ── SCORE PILL ───────────────────────────── */
.score-pill {
  font-size: 12px; font-weight: 700;
  background: #1a1a1a; border-radius: 20px; padding: 4px 10px;
  color: #fff; white-space: nowrap; flex-shrink: 0;
}
.score-pill.muted { color: #aaa; }

/* ── BUTTONS ──────────────────────────────── */
.small-btn {
  border: none; border-radius: 20px; padding: 6px 14px;
  background: #00d856; color: #fff; font-weight: 700; font-size: 12px; cursor: pointer; white-space: nowrap;
}
.small-btn:hover { background: #00b848; }

.del-btn {
  border: none; border-radius: 20px; padding: 6px 12px;
  background: #d63b3b; color: #fff; font-weight: 700; font-size: 12px; cursor: pointer; white-space: nowrap;
}
.del-btn:hover { background: #b52e2e; }

.blue-btn {
  border: none; border-radius: 20px; padding: 6px 14px;
  background: #1e9fd4; color: #fff; font-weight: 700; font-size: 12px; cursor: pointer; white-space: nowrap;
}
.blue-btn:hover { background: #1780aa; }

.cancel-btn {
  border: none; border-radius: 20px; padding: 6px 12px;
  background: #555; color: #fff; font-size: 12px; font-weight: 600; cursor: pointer;
}

/* ── GENRE CONTROLS ───────────────────────── */
.inline-row { display: flex; gap: 8px; align-items: center; }
.flex-input { flex: 1; margin: 0; }
.center { text-align: center; }
.empty { font-size: 12px; color: #666; text-align: center; padding: 12px 0; }

/* ── RECOMMENDATIONS ──────────────────────── */
.rec-list { display: flex; flex-direction: column; gap: 10px; }
.rec-card {
  background: #2a2a2a; border-radius: 12px; padding: 12px 16px;
  display: flex; align-items: center; gap: 14px;
}
.album-art { width: 52px; height: 52px; border-radius: 8px; object-fit: cover; flex-shrink: 0; }
.rec-info { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 3px; }
.rec-info strong { font-size: 13px; }
.rec-info span   { font-size: 11px; color: #888; }
.rec-info audio  { width: 100%;
  height: 34px;
  margin-top: 8px;

  filter:
    invert(0.92)
    sepia(0.08)
    saturate(0.7)
    hue-rotate(180deg)
    brightness(0.88)
    contrast(0.92);

  opacity: 0.92;}
.rec-btns { display: flex; flex-direction: column; gap: 6px; flex-shrink: 0; }

@media (max-width: 860px) {
  .page { padding: 20px; }
  .hero { flex-direction: column; }
  .hero-right { width: 100%; }
  .portal-grid { grid-template-columns: 1fr; }
  .list-panel { height: 240px; }
  .rec-panel { grid-column: 1; }
}

.genre-options {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.genre-chip {
  border: none;
  border-radius: 22px;
  padding: 10px 18px;
  background: #333;
  color: white;
  font-weight: 700;
  cursor: pointer;
}

.genre-chip.selected {
  background: #00d856;
  color: white;
}

.genre-help {
  color: #888;
  font-size: 12px;
  margin-top: 12px;
}

.clear-btn {
  border: none;
  border-radius: 20px;
  padding: 8px 18px;
  background: #1e9fd4;
  color: white;
  font-weight: 700;
  cursor: pointer;
  margin-top: 12px;
}

.clear-btn:hover {
  background: #444;
}

</style>