<script setup>
import { ref } from 'vue'
import axios from 'axios'

const emit = defineEmits(['close', 'login-success'])

const API_BASE = 'http://localhost:5000/api'

const mode = ref('login')
const error = ref('')

const loginForm = ref({
  username: '',
  password: ''
})

const registerForm = ref({
  username: '',
  password: '',
  fullName: '',
  favoriteGenres: ''
})

const login = async () => {
  try {
    const response = await axios.post(`${API_BASE}/auth/login`, loginForm.value)
    emit('login-success', response.data.user)
  } catch {
    error.value = 'Invalid username or password'
  }
}

const createAccount = async () => {
  try {
    await axios.post(`${API_BASE}/users`, {
      username: registerForm.value.username,
      password: registerForm.value.password,
      fullName: registerForm.value.fullName,
      favoriteGenres: registerForm.value.favoriteGenres
        .split(',')
        .map(item => item.trim())
        .filter(item => item.length > 0)
    })

    loginForm.value.username = registerForm.value.username
    loginForm.value.password = registerForm.value.password

    await login()
  } catch {
    error.value = 'Could not create account'
  }
}
</script>

<template>
  <div class="modal-overlay">
    <div class="login-modal">
      <h2>
        {{ mode === 'login' ? 'Sign In' : 'Create Account' }}
      </h2>

      <template v-if="mode === 'login'">
        <input v-model="loginForm.username" placeholder="Username" />
        <input v-model="loginForm.password" type="password" placeholder="Password" />

        <p v-if="error" class="error-text">{{ error }}</p>

        <div class="modal-actions">
          <button @click="login">Login</button>
          <button class="cancel-btn" @click="emit('close')">Cancel</button>
        </div>

        <p class="switch-text">
          No account?
          <span @click="mode = 'register'; error = ''">Create one</span>
        </p>
      </template>

      <template v-else>
        <input v-model="registerForm.username" placeholder="Username" />
        <input v-model="registerForm.password" type="password" placeholder="Password" />
        <input v-model="registerForm.fullName" placeholder="Full name" />
        <input v-model="registerForm.favoriteGenres" placeholder="Favorite genres: Pop, Rock" />

        <p v-if="error" class="error-text">{{ error }}</p>

        <div class="modal-actions">
          <button @click="createAccount">Create</button>
          <button class="cancel-btn" @click="mode = 'login'; error = ''">Back</button>
        </div>
      </template>
    </div>
  </div>
</template>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.72);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 999;
}

.login-modal {
  width: 440px;
  background: #1f1f1f;
  border: 1px solid rgba(255,255,255,0.12);
  border-radius: 28px;
  padding: 34px;
}

h2 {
  margin-top: 0;
}

input {
  width: 100%;
  margin-bottom: 14px;
  padding: 15px;
  border: 0;
  border-radius: 16px;
  background: #333;
  color: white;
}

.modal-actions {
  display: flex;
  gap: 14px;
}

button {
  flex: 1;
  border: 0;
  border-radius: 16px;
  padding: 15px;
  background: #00e653;
  color: white;
  font-weight: bold;
  cursor: pointer;
}

.cancel-btn {
  background: #5a5a5a;
}

.error-text {
  color: #ff4d4d;
}

.switch-text {
  color: #cfcfcf;
  text-align: center;
}

.switch-text span {
  color: #00e653;
  cursor: pointer;
  font-weight: bold;
}
</style>