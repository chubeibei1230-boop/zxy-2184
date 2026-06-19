import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User } from '@/types'
import { authApi } from '@/api'

export const useUserStore = defineStore('user', () => {
  const token = ref<string | null>(localStorage.getItem('token'))
  const user = ref<User | null>(null)

  const isLoggedIn = computed(() => !!token.value)
  const userRole = computed(() => user.value?.role || '')
  const userName = computed(() => user.value?.name || '')

  const setToken = (newToken: string) => {
    token.value = newToken
    localStorage.setItem('token', newToken)
  }

  const setUser = (newUser: User) => {
    user.value = newUser
    localStorage.setItem('user', JSON.stringify(newUser))
  }

  const login = async (username: string, password: string) => {
    const res = await authApi.login({ username, password })
    setToken(res.data.access_token)
    setUser(res.data.user)
    return res.data.user
  }

  const logout = () => {
    token.value = null
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  const loadUserFromStorage = () => {
    const stored = localStorage.getItem('user')
    if (stored) {
      try {
        user.value = JSON.parse(stored)
      } catch (e) {
        console.error('Failed to parse user from storage', e)
      }
    }
  }

  const fetchCurrentUser = async () => {
    try {
      const res = await authApi.getMe()
      setUser(res.data)
      return res.data
    } catch (e) {
      logout()
      throw e
    }
  }

  return {
    token,
    user,
    isLoggedIn,
    userRole,
    userName,
    setToken,
    setUser,
    login,
    logout,
    loadUserFromStorage,
    fetchCurrentUser
  }
})
