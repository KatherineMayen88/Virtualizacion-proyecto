<script setup>
import { ref } from 'vue'
import LandingPage from './components/LandingPage.vue'
import LoginModal from './components/LoginModal.vue'
import UserPortal from './components/UserPortal.vue'

const showLoginModal = ref(false)
const loggedUser = ref(null)

const openLogin = () => {
  showLoginModal.value = true
}

const closeLogin = () => {
  showLoginModal.value = false
}

const handleLoginSuccess = (user) => {
  loggedUser.value = user
  showLoginModal.value = false
}

const logout = () => {
  loggedUser.value = null
}
</script>

<template>
  <LandingPage
    v-if="!loggedUser"
    @open-login="openLogin"
  />

  <UserPortal
    v-else
    :user="loggedUser"
    @logout="logout"
  />

  <LoginModal
    v-if="showLoginModal"
    @close="closeLogin"
    @login-success="handleLoginSuccess"
  />
</template>

<!-- Estilos globales sin scoped — afectan toda la app -->
<style>
*, *::before, *::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

html, body, #app {
  width: 100%;
  min-height: 100vh;
  background: #1a1a1a;
  overflow-x: hidden;
}

/* Elimina estilos por defecto de Vite */
body {
  font-family: 'Inter', Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
</style>