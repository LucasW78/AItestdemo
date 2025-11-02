import { defineStore } from 'pinia'

export const useAppStore = defineStore('app', {
  state: () => ({
    globalLoading: false,
    sidebarCollapsed: false,
    notifications: [],
    user: null
  }),

  getters: {
    isAuthenticated: (state) => !!state.user,
    unreadNotifications: (state) => state.notifications.filter(n => !n.read)
  },

  actions: {
    setGlobalLoading(loading) {
      this.globalLoading = loading
    },

    toggleSidebar() {
      this.sidebarCollapsed = !this.sidebarCollapsed
    },

    addNotification(notification) {
      const id = Date.now().toString()
      this.notifications.push({
        id,
        ...notification,
        timestamp: new Date(),
        read: false
      })
    },

    markNotificationAsRead(id) {
      const notification = this.notifications.find(n => n.id === id)
      if (notification) {
        notification.read = true
      }
    },

    removeNotification(id) {
      const index = this.notifications.findIndex(n => n.id === id)
      if (index > -1) {
        this.notifications.splice(index, 1)
      }
    },

    setUser(user) {
      this.user = user
    },

    logout() {
      this.user = null
      this.notifications = []
    }
  }
})